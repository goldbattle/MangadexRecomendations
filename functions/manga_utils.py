import json
import os.path

from functions import manga_obj


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


def get_compressed_representation_string(manga_data):
    # cleaned data file
    managa_data_out = {}

    # loop through each index page, and extract the mangas
    for ct1, manga1 in enumerate(manga_data):

        # skip if we don't have matches
        if len(manga1.matches) < 1:
            continue

        # create the cleaned manga
        manga_temp = {}
        manga_temp["m_ids"] = []
        manga_temp["m_titles"] = []
        for match in manga1.matches:
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


def write_raw_manga_data_files(path, manga_data, count_per_file=5000):
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
                if count_exported > len(manga_data)-1:
                    break
                out_data.append(manga_data[count_exported].__dict__)
                count_exported += 1
            # json.dump(out_data, outfile, indent=2, sort_keys=False)
            json.dump(out_data, outfile, sort_keys=False)
    return manga_data
