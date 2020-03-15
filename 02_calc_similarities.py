# Import libraries
import time
import json
import string
import operator

# import our specific functions
from functions import manga_utils
from functions import manga_compator

# files in and out and settings
dir_inout = "output/"
min_same_labels = 5
min_desc_chars = 10
max_num_matches = 18
ignore_label_score_above_this_val = 0.20
weighting_label_score = 1.0
redo_all_matches = False


# Open the manga json file and load
manga_data = manga_utils.read_raw_manga_data_files(dir_inout)
print("loaded " + str(len(manga_data)) + " mangas")

# get our list of labels (genres, demographics, themes, etc)
labels_dict = manga_utils.get_used_labels(manga_data)
print("loaded " + str(len(labels_dict)) + " labels")
labels_vec = []
for label in sorted(labels_dict.keys()):
    print("    " + str(labels_dict[label]) + " " + label + " in data")
    labels_vec.append(label)
labels_weights = manga_utils.get_label_ranks(labels_vec)

# Loop through each manga, and create a corpus of descriptions
# NOTE: we remove non-numeric and non-alphabetical chars
# NOTE: we remove non-english words, is this really ok?
# NOTE: should we add the genres here?? not sure..
corpus = []
printable = set(string.printable)
for idx, manga in enumerate(manga_data):
    str_raw = manga.title + ". " + manga.description
    corpus.append((idx, manga_utils.clean_string(str_raw)))

# build a TF/IDF matrix for each paper
tfidf_matrix = manga_compator.load_corpus_into_tfidf(corpus)

# what we will load our matches into and the start time
time_start = time.time()

# loop through each and find the top matches
for ct, manga1 in enumerate(manga_data):

    # nice debug only a certain set of manga ids
    # if not manga1.id == 2404 and not manga1.id == 18806 and not manga1.id == 3132:
    #     continue

    # skip if we already have matches
    if len(manga1.matches) > 0 and not redo_all_matches:
        continue
    manga1.matches.clear()

    # nice debug print of which one we are processing
    print(str(round(100 * float(ct) / len(manga_data), 2)) +
          "% -> manga " + str(manga1.id) + " - " + manga1.title + " - " + manga1.url)

    # skip if description is not long enough
    if len(manga1.description) < min_desc_chars:
        continue

    # get our scores based on tfidf and labels
    scores = manga_compator.find_similar_tfidf(tfidf_matrix, ct)
    scores_labels = manga_compator.find_similar_labels(manga1, labels_vec, labels_weights, manga_data)

    # loop through our data, and combine our two scores
    for idx, manga in enumerate(manga_data):

        # cache if we are in either list
        bool_in_s1 = idx in scores
        bool_in_s2 = idx in scores_labels

        # if it is greater, then add a total score
        if bool_in_s1 and scores[idx] >= ignore_label_score_above_this_val:
            scores[idx] += 1.0
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

    # skip if we don't have at least one label
    if count_manga1 < 1:
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

        # skip if this manga does not have any chapters
        # todo: since we don't update this count, we can't match to old
        # todo: manga that have since had a chapter added to them...
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
        if count_same < min(min(min_same_labels, count_manga1), count_manga2):
            continue

        # append this matched manga to our current manga
        manga_data[ct].matches.append({
            'id': manga2.id,
            'title': manga2.title,
            'url': manga2.url,
            'score': scores[idx] / 2.0
        })

        # nice debug print
        count_matched = count_matched + 1
        print("   match " + str(manga2.id) + " (" + str(round(scores[idx] / 2.0, 4))
              + ") - " + manga2.title + " - " + manga2.url)


# Save our json to file!
manga_utils.write_raw_manga_data_files(dir_inout, manga_data)
print("===========================")
print("outputted to " + dir_inout)

# Finally get the compressed representation
dict_compressed = manga_utils.get_compressed_representation_string(manga_data)
with open(dir_inout + "mangas_compressed.json", 'w') as outfile:
    json.dump(dict_compressed, outfile, sort_keys=False)
print("outputted to " + dir_inout + "mangas_compressed.json")
print("compressed " + str(len(manga_data)) + " to only " + str(len(dict_compressed)) + " mangas")
print("script took " + str(round(time.time() - time_start, 2)) + " seconds")
