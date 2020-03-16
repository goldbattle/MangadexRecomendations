import re
import json
import os.path
from string import punctuation

from functions import manga_obj


def clean_string(str_raw):
    stops = ['the', 'a', 'an', 'and', 'but', 'if', 'or', 'because', 'as', 'what', 'which', 'this', 'that', 'these',
             'those', 'then', 'just', 'so', 'than', 'such', 'both', 'through', 'about', 'for', 'is', 'of', 'while',
             'during', 'to']

    # Remove punctuation from text
    str_raw = ''.join([c for c in str_raw if c not in punctuation])

    # Remove stop words
    str_raw = " ".join([w for w in str_raw.split() if w.lower() not in stops])

    # Replace apostrophes with standard lexicons
    str_raw = str_raw.replace("isn't", "is not")
    str_raw = str_raw.replace("aren't", "are not")
    str_raw = str_raw.replace("ain't", "am not")
    str_raw = str_raw.replace("won't", "will not")
    str_raw = str_raw.replace("didn't", "did not")
    str_raw = str_raw.replace("shan't", "shall not")
    str_raw = str_raw.replace("haven't", "have not")
    str_raw = str_raw.replace("hadn't", "had not")
    str_raw = str_raw.replace("hasn't", "has not")
    str_raw = str_raw.replace("don't", "do not")
    str_raw = str_raw.replace("wasn't", "was not")
    str_raw = str_raw.replace("weren't", "were not")
    str_raw = str_raw.replace("doesn't", "does not")
    str_raw = str_raw.replace("'s", " is")
    str_raw = str_raw.replace("'re", " are")
    str_raw = str_raw.replace("'m", " am")
    str_raw = str_raw.replace("'d", " would")
    str_raw = str_raw.replace("'ll", " will")

    # remove emails and urls
    str_raw = re.sub(r'^https?:\/\/.*[\r\n]*', ' ', str_raw, flags=re.MULTILINE)
    str_raw = re.sub(r'[\w\.-]+@[\w\.-]+', ' ', str_raw, flags=re.MULTILINE)

    # Remove all symbols (clean to normal english)
    str_raw = re.sub(r'[^A-Za-z0-9\s]', r' ', str_raw)
    str_raw = re.sub(r'\n', r' ', str_raw)
    str_raw = re.sub(r'[0-9]', r' ', str_raw)
    return str_raw


def get_labels_from_soup_obj(divs):
    # return if we don't have any divs
    vec_strs = []
    if len(divs) == 0:
        return vec_strs

    # else lets extract the labels from the divs
    div_paren = divs[0].parent.parent
    divs = div_paren.find_all("div")
    if len(divs) > 0:
        labels = divs[-1].find_all("a")
        for label in labels:
            vec_strs.append(label.getText())
    return vec_strs


def remove_dups_from_manga_list(manga_data):
    # cleaned data file with no dups
    manga_data_out = []

    # loop through each index page, and extract the mangas
    for ct1, manga1 in enumerate(manga_data):

        # check if this has already been added to our out vector
        found = False
        for ct2, manga2 in enumerate(manga_data_out):
            if manga1.id == manga2.id:
                found = True
                break

        # Append to the clean data out vector if not added
        if not found:
            manga_data_out.append(manga1)

    # finally return the cleaned array
    return manga_data_out


def get_used_labels(manga_data):
    labels = {}
    for id, manga in enumerate(manga_data):
        for label in manga.content:
            if label not in labels:
                labels[label] = 1
            else:
                labels[label] += 1
        for label in manga.demographic:
            if label not in labels:
                labels[label] = 1
            else:
                labels[label] += 1
        for label in manga.format:
            if label not in labels:
                labels[label] = 1
            else:
                labels[label] += 1
        for label in manga.genre:
            if label not in labels:
                labels[label] = 1
            else:
                labels[label] += 1
        for label in manga.theme:
            if label not in labels:
                labels[label] = 1
            else:
                labels[label] += 1
    return labels


def get_label_ranks(labels_vec):
    # vector of high priority labels we should weight more
    high_level4 = ["Ecchi",
                   "Gore",
                   "Sexual Violence",
                   "Smut",
                   "4-Koma"]
    high_level3 = ["Loli",
                   "Incest",
                   "Sports",
                   "Yaoi",
                   "Shoujo Ai",
                   "Yuri",
                   "Shounen Ai"]
    high_level2 = ["Historical",
                   "Horror",
                   "Isekai",
                   "Mecha",
                   "Medical",
                   "Slice of Life",
                   "Cooking",
                   "Crossdressing",
                   "Genderswap",
                   "Harem",
                   "Reverse Harem",
                   "Vampires",
                   "Zombies"]

    # loop through and append
    labels_weights = []
    for label in labels_vec:
        if label in high_level4:
            labels_weights.append(1.00)
        elif label in high_level3:
            labels_weights.append(0.80)
        elif label in high_level2:
            labels_weights.append(0.65)
        else:
            labels_weights.append(0.45)

    # return the result
    return labels_weights


def get_compressed_representation_string(manga_data):
    # cleaned data file
    managa_data_out = {}

    # get the id to chapter count dictionary (used to rank related)
    map_id_to_chap_num = {}
    map_id_to_rating = {}
    for manga1 in manga_data:
        map_id_to_chap_num[manga1.id] = manga1.count_chapters
        map_id_to_rating[manga1.id] = manga1.rating

    # loop through each index page, and extract the mangas
    for ct1, manga1 in enumerate(manga_data):

        # skip if we don't have matches
        if len(manga1.matches) < 1:
            continue

        # create the cleaned manga
        manga_temp = {}
        ids_added = []
        manga_temp["m_ids"] = []
        manga_temp["m_titles"] = []

        # if we have related, add those
        # NOTE: add at max the top four of them
        # NOTE: we sort by top rated related manga
        related_sorted = sorted(manga1.related, reverse=True,
                                key=lambda d: map_id_to_rating[d["id"]] if d["id"] in map_id_to_rating else -1)
        for match in related_sorted:
            if len(manga_temp["m_ids"]) >= 6:
                break
            if match["id"] in ids_added:
                continue
            ids_added.append(match["id"])
            manga_temp["m_ids"].append(match["id"])
            manga_temp["m_titles"].append(match["title"])

        # append the matches (only ones not already added)
        for match in manga1.matches:
            if match["id"] in ids_added:
                continue
            ids_added.append(match["id"])
            manga_temp["m_ids"].append(match["id"])
            manga_temp["m_titles"].append(match["title"])

        # Append to the clean data out vector if not added
        managa_data_out[manga1.id] = manga_temp

    # return the dict
    return managa_data_out


def read_raw_manga_data_files(path):
    # data to return
    manga_data = []
    # loop through each file and append
    ct = 0
    found_file = False
    while not found_file:
        file_in = path + "mangas_raw_" + str(ct) + ".json"
        ct = ct + 1
        if os.path.exists(file_in):
            print("opening " + file_in)
            with open(file_in) as json_file:
                manga_data_json = json.load(json_file)
            for manga_json in manga_data_json:
                manga_data.append(manga_obj.MangaObj(manga_json))
        else:
            print("\033[93mwarning!! unable to open " + file_in + "!!\033[0m")
            found_file = True
    return manga_data


def write_raw_manga_data_files(path, manga_data, count_per_file=2000):
    # create output direction if not exists
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    # loop through each file and append
    ct = 0
    count_exported = 0
    while count_exported < len(manga_data):
        file_out = path + "mangas_raw_" + str(ct) + ".json"
        ct = ct + 1
        with open(file_out, 'w') as outfile:
            out_data = []
            for i in range(0, count_per_file):
                if count_exported > len(manga_data) - 1:
                    break
                out_data.append(manga_data[count_exported].__dict__)
                count_exported += 1
            # json.dump(out_data, outfile, indent=2, sort_keys=False)
            json.dump(out_data, outfile, sort_keys=False)
    return manga_data
