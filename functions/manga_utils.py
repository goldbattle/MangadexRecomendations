import re
import json
import html
import os.path
from string import punctuation
from collections import defaultdict

from functions import manga_obj
from functions import anilist_helpers


def clean_string(str_raw, removeStopWords=False):

    # bbcodes that our description will have in it
    # https://github.com/CarlosEsco/Neko/blob/master/app/src/main/java/eu/kanade/tachiyomi/source/online/utils/MdUtil.kt
    descriptionLanguages = [
        "Russian / Русский",
        "[u]Russian",
        "[b][u]Russian",
        "[RUS]",
        "Russian / Русский",
        "Russian/Русский:",
        "Russia/Русское",
        "Русский",
        "RUS:",
        "[b][u]German / Deutsch",
        "German/Deutsch:",
        "Espa&ntilde;ol / Spanish",
        "Spanish / Espa&ntilde;ol",
        "Spanish / Espa & ntilde; ol",
        "Spanish / Espa&ntilde;ol",
        "[b][u]Spanish",
        "[Espa&ntilde;ol]:",
        "[b] Spanish: [/ b]",
        "정보",
        "Spanish/Espa&ntilde;ol",
        "Espa&ntilde;ol / Spanish",
        "Italian / Italiano",
        "Italian/Italiano",
        "\r\n\r\nItalian\r\n",
        "Pasta-Pizza-Mandolino/Italiano",
        "Persian /فارسی",
        "Farsi/Persian/",
        "Polish / polski",
        "Polish / Polski",
        "Polish Summary / Polski Opis",
        "Polski",
        "Portuguese (BR) / Portugu&ecirc;s",
        "Portuguese / Portugu&ecirc;s",
        "Português / Portuguese",
        "Portuguese / Portugu",
        "Portuguese / Portugu&ecirc;s",
        "Portugu&ecirc;s",
        "Portuguese (BR) / Portugu & ecirc;",
        "Portuguese (BR) / Portugu&ecirc;",
        "[PTBR]",
        "R&eacute;sume Fran&ccedil;ais",
        "R&eacute;sum&eacute; Fran&ccedil;ais",
        "[b][u]French",
        "French / Fran&ccedil;ais",
        "Fran&ccedil;ais",
        "[hr]Fr:",
        "French - Français:",
        "Turkish / T&uuml;rk&ccedil;e",
        "Turkish/T&uuml;rk&ccedil;e",
        "T&uuml;rk&ccedil;e",
        "[b][u]Chinese",
        "Arabic / العربية",
        "العربية",
        "[hr]TH",
        "[b][u]Vietnamese",
        "[b]Links:",
        "[b]Link[/b]",
        "Links:",
        "[b]External Links"
    ]
    englishDescriptionTags = [
        "[b][u]English:",
        "[b][u]English",
        "[English]:",
        "[B][ENG][/B]"
    ]
    bbcodes = [
        "[list]",
        "[/list]",
        "[*]",
        "[hr]",
        "[u]",
        "[/u]",
        "[b]",
        "[/b]"
    ]

    # remove all non-english descriptions
    # this assumes the english one is first
    for tag in descriptionLanguages:
        str_raw = str_raw.split(tag, 1)[0]

    # now remove all english tags which are no longer needed
    for tag in englishDescriptionTags:
        str_raw = str_raw.replace(tag, "")

    # convert all works to lower case
    # also remove multiple white space and replace with single
    str_raw = html.unescape(str_raw)
    str_raw = str_raw.lower()
    str_raw = " ".join(str_raw.split())

    # run a second time now, but with all lower case
    # for tag in descriptionLanguages:
    #     str_raw = str_raw.split(tag.lower(), 1)[-1]
    # for tag in englishDescriptionTags:
    #     str_raw = str_raw.replace(tag.lower(), "")

    # next clean the string from any bbcodes
    for tag in bbcodes:
        str_raw = str_raw.replace(tag, "")
    str_raw = re.sub('\[.*?]', '', str_raw)

    # remove source parentheses typical of anilist
    # Eg: (source: solitarycross), (source: eat manga)
    str_raw = re.sub(r'\(source: [^)]*\)', '', str_raw)

    # remove any html codes
    str_raw = re.sub(r'<[^>]*>', r' ', str_raw)

    # remove emails and urls
    str_raw = re.sub(r'^https?:\/\/.*[\r\n]*', ' ', str_raw, flags=re.MULTILINE)
    str_raw = re.sub(r'^http?:\/\/.*[\r\n]*', ' ', str_raw, flags=re.MULTILINE)
    str_raw = re.sub(r'[\w\.-]+@[\w\.-]+', ' ', str_raw, flags=re.MULTILINE)

    # now clean stop words which are not helpful
    # we want to basically just collect a bunch of words
    stops = ['the', 'a', 'an', 'and', 'but', 'if', 'or', 'because', 'as', 'what', 'which', 'this', 'that', 'these',
             'those', 'then', 'just', 'so', 'than', 'such', 'both', 'through', 'about', 'for', 'is', 'of', 'while',
             'during', 'to']

    # Remove punctuation and stop words
    if removeStopWords:
        str_raw = ''.join([c for c in str_raw if c not in punctuation])
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

    # Remove all symbols (clean to normal english)
    # str_raw = re.sub(r'[^A-Za-z0-9\s]', r' ', str_raw)
    str_raw = re.sub(r'\n', r' ', str_raw)
    # str_raw = re.sub(r'[0-9]', r'', str_raw)
    str_raw = " ".join(str_raw.split())

    # return the final cleaned string
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
    labels = defaultdict(int)
    for id, manga in enumerate(manga_data):
        for label in manga.content:
            labels[label] += 1
        for label in manga.demographic:
            labels[label] += 1
        for label in manga.format:
            labels[label] += 1
        for label in manga.genre:
            labels[label] += 1
        for label in manga.theme:
            labels[label] += 1
    return labels


def get_label_ranks(labels_vec):
    # vector of high priority labels we should weight more
    high_level4 = ["Ecchi",
                   "Gore",
                   "Sexual Violence",
                   "Smut",
                   "4-Koma",
                   "Wuxia"]
    high_level3 = ["Loli",
                   "Incest",
                   "Sports",
                   "Yaoi",
                   "Shoujo Ai",
                   "Yuri",
                   "Isekai",
                   "Villainess",
                   "Shounen Ai"]
    high_level2 = ["Historical",
                   "Horror",
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
            labels_weights.append(0.95)
        elif label in high_level2:
            labels_weights.append(0.90)
        else:
            labels_weights.append(0.85)

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


def get_compressed_representation_string_v2(manga_data):
    # cleaned data file
    managa_data_out = {}

    # loop through each index page, and extract the mangas
    for ct1, manga1 in enumerate(manga_data):

        # skip if we don't have matches
        if len(manga1.matches) < 1:
            continue

        # create the cleaned manga
        manga_temp = {}
        ids_added = []

        # append the matches (only ones not already added)
        for ct2, match in enumerate(manga1.matches):
            if match["id"] in ids_added:
                continue
            manga_temp.setdefault("m_ids", []).append(match["id"])
            manga_temp.setdefault("m_titles", []).append(match["title"])

        # Append to the clean data out vector if not added
        managa_data_out[manga1.id] = manga_temp

    # get mappings to external services
    # AL: anilist, MAL: myanimelist, MU: mangaupdates
    md2external = {}
    for manga in manga_data:
        if len(manga.external) < 1:
            continue
        temp_data = manga.external
        temp_data["title"] = manga.title
        md2external[manga.id] = temp_data

    # construct the final dictionary
    # this will include mapping to MAL and AL
    managa_data_out_final = {
        "data": managa_data_out,
        "external": md2external
    }

    # return the dict
    return managa_data_out_final


def read_raw_manga_data_files(path):
    # data to return
    manga_data = []
    # loop through each file and append
    ct = 0
    found_file = False
    while not found_file:
        file_in = path + "mangas_raw_" + format(ct, '03') + ".json"
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


def write_raw_manga_data_files(path, manga_data, count_per_file=1000):
    # create output direction if not exists
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    # sort the manga data based on the id
    manga_data = sorted(manga_data, key=lambda d: d.id)

    # loop through each file and append
    ct = 0
    count_exported = 0
    while count_exported < len(manga_data):
        file_out = path + "mangas_raw_" + format(ct, '03') + ".json"
        ct = ct + 1
        with open(file_out, 'w') as outfile:
            out_data = []
            for i in range(0, count_per_file):
                if count_exported > len(manga_data) - 1:
                    break
                out_data.append(manga_data[count_exported].__dict__)
                count_exported += 1
            json.dump(out_data, outfile, indent=2, sort_keys=False)
            # json.dump(out_data, outfile, sort_keys=False)
    return manga_data


def make_dir_if_not(dir):
    if not os.path.exists(os.path.dirname(dir)):
        os.makedirs(os.path.dirname(dir))
