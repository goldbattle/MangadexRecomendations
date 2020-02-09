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

        # create the cleaned manga
        manga_temp = {}
        manga_temp["m_ids"] = []
        manga_temp["m_titles"] = []
        manga_temp["scores"] = []
        for match in manga1.matches:
            manga_temp["m_ids"].append(match["id"])
            manga_temp["m_titles"].append(match["title"])
            manga_temp["scores"].append(round(match["score"], 3))

        # Append to the clean data out vector if not added
        managa_data_out[manga1.id] = manga_temp

    # return the dict
    return managa_data_out
