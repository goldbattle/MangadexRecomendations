# Import libraries
import time
import re
import os
import json
import string
import operator

# import our specific functions
from functions import manga_obj
from functions import manga_utils
from functions import manga_compator

# files in and out and settings
file_in = "output/mangas_raw_10.json"
file_out_matched = "output/mangas_matched.json"
file_out_compressed = "output/mangas_compressed.json"
min_same_labels = 2
max_num_matches = 2
ignore_label_score_above_this_val = 0.05

# Open the manga json file and load
with open(file_in) as json_file:
    manga_data_json = json.load(json_file)

# convert to our objects from the json
manga_data = []
for ct, manga_json in enumerate(manga_data_json):
    manga_data.append(manga_obj.MangaObj(manga_json))
print("loaded " + str(len(manga_data)) + " mangas")

# get our list of labels (genres, demographics, themes, etc)
labels_dict = manga_utils.get_used_labels(manga_data)
print("loaded " + str(len(labels_dict)) + " labels")
labels_vec = []
for label in sorted(labels_dict.keys()):
    print("    " + str(labels_dict[label]) + " " + label + " in data")
    labels_vec.append(label)

# Loop through each manga, and create a corpus of descriptions
# NOTE: we remove non-numeric and non-alphabetical chars
# NOTE: we remove non-english words, is this really ok?
# NOTE: should we add the genres here?? not sure..
corpus = []
printable = set(string.printable)
for ct, manga in enumerate(manga_data):
    str_raw = manga.title + ". " + manga.description
    str_raw = re.sub(r'http\S+', '', str_raw)
    str_raw = ''.join(filter(lambda x: x in printable, str_raw))
    # str_eng = re.sub(r'[^A-Za-z0-9 ]+', '', manga1["title"]+". "+manga1["description"])
    corpus.append((ct, str_raw))

# build a TF/IDF matrix for each paper
tfidf_matrix = manga_compator.load_corpus_into_tfidf(corpus)

# what we will load our matches into and the start time
managa_data_out = []
time_start = time.time()

# loop through each and find the top matches
for ct, manga1 in enumerate(manga_data):

    # nice debug print of which one we are processing
    print(str(round(100 * float(ct) / len(manga_data), 2)) +
          "% -> manga " + str(manga1.id) + " - " + manga1.title + " - " + manga1.url)

    # get our scores based on tfidf and labels
    scores_tfidf = manga_compator.find_similar_tfidf(tfidf_matrix, ct)
    scores_labels = manga_compator.find_similar_labels(manga1, labels_vec, manga_data)
    scores = []
    for id1, score1 in scores_tfidf:
        score2 = 1.0
        for id2, scoretemp in scores_labels:
            if id1 == id2 and score1 < ignore_label_score_above_this_val:
                score2 = scoretemp
        scores.append((id1, (score1+score2)/2.0, score1, score2))
    scores.sort(key=operator.itemgetter(1), reverse=True)

    # get the top matches, and then only select good ones
    count_matched = 0
    manga_temp = manga1
    for index, score_summed, score1, score2 in scores:

        # skip if already have our top 12
        if count_matched >= max_num_matches:
            break

        # get the manga object for the match
        idx = corpus[index][0]
        manga2 = manga_data[idx]

        # calc the label vectors
        manga1_labels = manga1.compute_xor_label_vector(labels_vec)
        manga2_labels = manga2.compute_xor_label_vector(labels_vec)

        # count the number of same labels between the two
        count_same = 0
        for idlc, val in enumerate(manga1_labels):
            if manga1_labels[idlc] and manga2_labels[idlc]:
                count_same += 1

        # skip this if it doesn't have the min number of matches
        if count_same < min_same_labels:
            continue

        # append this matched manga to our current manga
        manga_data[ct].matches.append({
            'id': manga2.id,
            'title': manga2.title,
            'url':  manga2.url,
            'score': score_summed
        })

        # nice debug print
        count_matched = count_matched + 1
        print("   match " + str(manga2.id) + " (" + str(round(score_summed, 3)) + "," + str(round(score1, 3))
              + "," + str(round(score2, 3)) + ")" + " - " + manga2.title + " - " + manga2.url)

    # only append if we have matches
    if count_matched > 0:
        managa_data_out.append(manga_temp)

# create output direction if not exists
if not os.path.exists(os.path.dirname(file_out_matched)):
    os.makedirs(os.path.dirname(file_out_matched))

# Save our json to file!
with open(file_out_matched, 'w') as outfile:
    json.dump([ob.__dict__ for ob in managa_data_out], outfile, indent=4, sort_keys=True)
print("===========================")
print("outputted to " + file_out_matched)


# Finally get the compressed representation
dict_compressed = manga_utils.get_compressed_representation_string(managa_data_out)
with open(file_out_compressed, 'w') as outfile:
    json.dump(dict_compressed, outfile, indent=4, sort_keys=True)
print("outputted to " + file_out_compressed)
print("script took "+str(round(time.time() - time_start, 2)) + " seconds")
