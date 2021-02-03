# Import libraries
import sys
import time
import json
import string
import operator
import gzip
import os
import shutil
from datetime import datetime

# import our specific functions
from functions import manga_utils
from functions import manga_compator

# files in and out and settings
dir_in = "data/jsons/"
dir_logs = "data/logs/"
dir_out = "output/"
min_same_labels = 4
min_same_labels_h18 = 2
min_desc_chars = 100
max_num_matches = 25
ignore_label_score_above_this_val = 0.30
ignore_label_score_below_this_val = 0.05
weighting_label_score = 0.8
use_labels_to_match = True
redo_all_matches = True
if len(sys.argv) == 3:
    id_start = int(sys.argv[1])
    id_end = int(sys.argv[2])
else:
    id_start = 1
    id_end = 60000

assert id_end >= id_start
assert id_end > 0
assert id_start > 0

# Open the manga json file and load
time_start = time.time()
t01 = time.time()
manga_data = manga_utils.read_raw_manga_data_files(dir_in)
t11 = time.time()
print("loaded " + str(len(manga_data)) + " mangas (" + str(round(t11 - t01, 2)) + " seconds)")

# get our list of labels (genres, demographics, themes, etc)
t02 = time.time()
labels_dict = manga_utils.get_used_labels(manga_data)
print("loaded " + str(len(labels_dict)) + " labels")
labels_vec = []
for label in sorted(labels_dict.keys()):
    # print("    " + str(labels_dict[label]) + " " + label + " in data")
    labels_vec.append(label)
labels_weights = manga_utils.get_label_ranks(labels_vec)

# print largest to smallest generes
labels_dict_sorted = sorted(labels_dict.items(), key=operator.itemgetter(1))
for label, num in labels_dict_sorted:
    print("    " + str(num) + " " + label + " in data")

# calculate mapping between manga_data index and mangadex id
data2mangadexid = {}
for idx, manga in enumerate(manga_data):
    data2mangadexid[manga.id] = idx

# Loop through each manga, and create a corpus of descriptions
# NOTE: we remove non-numeric and non-alphabetical chars
# NOTE: we remove non-english words, is this really ok?
# NOTE: should we add the genres here?? not sure..
corpus = []
id2corups = {}
corups2id = {}
counter = 0
printable = set(string.printable)
for idx, manga in enumerate(manga_data):
    # create a compounded text description
    str_raw = manga.title + ". " + manga.description
    if "description" in manga.external_al:
        str_raw = str_raw + manga.external_al["description"]
    # loop through all the related and append those descriptions also
    for related in manga.related:
        if related["id"] in data2mangadexid:
            str_raw = str_raw + manga_data[data2mangadexid[related["id"]]].description
            break
    # append description is not long enough
    if len(manga.description) > min_desc_chars:
        corpus.append((idx, manga_utils.clean_string(str_raw, False)))
        id2corups[idx] = counter
        corups2id[counter] = idx
        counter = counter + 1

# build a TF/IDF matrix for each paper
tfidf_matrix = manga_compator.load_corpus_into_tfidf(corpus)
t12 = time.time()
print("setup tf-idf in " + str(round(t12 - t02, 2)) + " seconds")

# loop through each and find the top matches
count_manga_matching = 0
count_manga_matched_to = 0
for ct, manga1 in enumerate(manga_data):

    # nice debug only a certain set of manga ids
    # test_manga = [29557, 33691, 38917, 50727, 52297]
    # test_manga = [40299]
    # if manga1.id not in test_manga:
    #     continue

    # skip if not in the range we will match through
    if manga1.id < id_start or manga1.id > id_end:
        continue

    # skip if we already have matches
    if len(manga1.matches) > 0 and not redo_all_matches:
        continue
    manga1.matches.clear()
    manga_data[ct].matches.clear()

    # nice debug print of which one we are processing
    print(str(round(100 * float(ct) / len(manga_data), 2)) +
          "% -> manga " + str(manga1.id) + " - " + manga1.title + " - " + manga1.url)

    # get our scores based on tfidf and labels
    # only get tfidf score if we have a big enough description
    scores = {}
    if len(manga1.description) > min_desc_chars:
        scores = manga_compator.find_similar_tfidf(tfidf_matrix, id2corups[ct])
        # loop through tfidf and change ids to the manga_data ids
        scores_temp = {}
        for tmpid, score in scores.items():
            scores_temp[corups2id[tmpid]] = score
        scores = scores_temp

    # get score labels if enabled
    if use_labels_to_match:
        scores_labels = manga_compator.find_similar_labels(manga1, labels_vec, labels_weights, manga_data)
    else:
        scores_labels = {}

    # loop through our data, and combine our two scores
    for idx, manga in enumerate(manga_data):

        # cache if we are in either list
        bool_in_s1 = idx in scores
        bool_in_s2 = idx in scores_labels

        # if it is greater, then add a total score
        if bool_in_s1 and scores[idx] >= ignore_label_score_above_this_val:
            scores[idx] += 1.0
            continue

        # if less than, just use the genre matching scheme
        if bool_in_s1 and bool_in_s2 and scores[idx] < ignore_label_score_below_this_val:
            scores[idx] = scores_labels[idx]
            continue

        # otherwise we should just add the score we have
        if bool_in_s1 and bool_in_s2:
            scores[idx] += weighting_label_score * scores_labels[idx]
            continue

        # if not originally in it, we should append it
        if not bool_in_s1 and bool_in_s2:
            scores[idx] = weighting_label_score * scores_labels[idx]
            continue

    # finally sort in decending order, so highest is near the top
    scores = dict(sorted(scores.items(), key=operator.itemgetter(1), reverse=True))

    # count if how many labels we have
    manga1_labels = manga1.compute_xor_label_vector(labels_vec)
    count_manga1 = 0
    for idlc, val in enumerate(manga1_labels):
        if manga1_labels[idlc]:
            count_manga1 += 1

    # skip if we don't have at least two labels
    if count_manga1 < 2:
        continue

    # get the top matches, and then only select good ones
    count_matched = 0
    for idx in scores:

        # skip if already have our top
        if count_matched >= max_num_matches:
            break

        # get the manga object for the match
        manga2 = manga_data[idx]

        # skip if the manga ids are the same
        if manga1.id == manga2.id:
            continue

        # skip if the related has (promo) in the title
        # this are promotional items for mangas, thus are not really a true manga
        if "(promo)" in manga2.title.lower():
            continue

        # skip any manga which is already a related manga
        # no need to append if it is already listed on mangadex
        is_related = False
        for related in manga1.related:
            if manga2.id == related["id"]:
                is_related = True
                # print("found "+str(manga2.id)+" is already related to "+manga1.url)
                break
        if is_related:
            continue

        # skip if this manga does not have any chapters
        if manga2.count_chapters < 1:
            continue

        # calc the label vector
        manga2_labels = manga2.compute_xor_label_vector(labels_vec)
        count_manga2 = 0
        for idlc, val in enumerate(manga2_labels):
            if manga2_labels[idlc]:
                count_manga2 += 1

        # check our exact matches requires and see if we have any invalid
        if not manga_compator.is_exact_match(manga1, manga2):
            continue

        # count the number of same labels between the two
        count_same = 0
        for idlc, val in enumerate(manga1_labels):
            if manga1_labels[idlc] and manga2_labels[idlc]:
                count_same += 1

        # skip this if it doesn't have the min number of matches
        # note that we won't skip if the current manga has less than the required
        if manga1.is_r18 and count_same < min(min_same_labels_h18, count_manga1):
            continue
        if not manga1.is_r18 and count_same < min(min_same_labels, count_manga1):
            continue

        # append this matched manga to our current manga
        manga_data[ct].matches.append({
            'id': manga2.id,
            'title': manga2.title,
            'url': manga2.url,
            'score': round(scores[idx] / 2.0, 4),
            'r18': manga2.is_r18
        })

        # nice debug print
        count_matched = count_matched + 1
        print("   match " + str(manga2.id) + " (" + str(round(scores[idx] / 2.0, 4))
              + ") - " + manga2.title + " - " + manga2.url)

    # if we have had some matches, then we are good
    if count_matched > 0:
        count_manga_matching = count_manga_matching + 1
        count_manga_matched_to = count_manga_matched_to + count_matched

# Save our json to file!
manga_utils.write_raw_manga_data_files(dir_in, manga_data)
print("===========================")
print("outputted to " + dir_in)

# Finally get the compressed representation
dict_compressed = manga_utils.get_compressed_representation_string(manga_data)
manga_utils.make_dir_if_not(dir_out)
with open(dir_out + "mangas_compressed.json", 'w') as outfile:
    json.dump(dict_compressed, outfile, sort_keys=False)
with gzip.open(dir_out + 'mangas_compressed.json.gz', 'wb') as f:
    out_str = json.dumps(dict_compressed, sort_keys=False)
    f.write(out_str.encode('utf-8'))
print("outputted to " + dir_out + "mangas_compressed.json")
print("compressed " + str(len(manga_data)) + " to only " + str(len(dict_compressed)) + " mangas")

# Write the relation between each mangadex id and external
dict_compressed_v2 = manga_utils.get_compressed_representation_string_v2(manga_data)
with open(dir_out + "md2external.json", 'w') as outfile:
    json.dump(dict_compressed_v2["external"], outfile, sort_keys=False)
with gzip.open(dir_out + 'md2external.json.gz', 'wb') as f:
    out_str = json.dumps(dict_compressed_v2["external"], sort_keys=False)
    f.write(out_str.encode('utf-8'))

# write out the second api version format
path_output_api = dir_out + "api/"
if os.path.exists(path_output_api):
    shutil.rmtree(path_output_api)
os.makedirs(path_output_api)
for key, manga1 in dict_compressed_v2["data"].items():
    path_output_api_file = path_output_api + format(manga1["id"], '05') + ".json"
    with open(path_output_api_file, 'w') as outfile:
        json.dump(manga1, outfile, indent=2, sort_keys=False)
print("outputted to " + path_output_api)
print("saved " + str(len(dict_compressed_v2["data"])) + " api json endpoints (v2)")

# show how long it took to run
print("script took " + str(round(time.time() - time_start, 2)) + " seconds")

# output content to log file
manga_utils.make_dir_if_not(dir_logs)
with open(dir_logs + "log_calc_similarities.txt", "a") as myfile:
    myfile.write(
        "[" + datetime.utcnow().strftime("%B %d, %Y %H:%M:%S") + "]: " +
        "Calculated similarity for " + str(count_manga_matching) + " mangas. " +
        "Average of " + str(round(count_manga_matched_to / (count_manga_matching+1), 2)) + " matches per manga. " +
        "Took " + str(round((time.time() - time_start) / 60.0, 2)) + " minutes to complete.\n"
    )
