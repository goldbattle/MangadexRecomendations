

def build_mangadex_to_anilist_id_lookup(manga_data):
    al2md = {}
    md2al = {}
    md2al_title = {}
    for manga in manga_data:
        if "al" in manga.external:
            al2md[manga.external["al"]] = manga.id
            md2al[manga.id] = manga.external["al"]
            md2al_title[manga.id] = manga.title
    return al2md, md2al, md2al_title


def build_mangadex_to_myanimelist_id_lookup(manga_data):
    mal2md = {}
    md2mal = {}
    md2mal_title = {}
    for manga in manga_data:
        if "mal" in manga.external:
            mal2md[manga.external["mal"]] = manga.id
            md2mal[manga.id] = manga.external["mal"]
            md2mal_title[manga.id] = manga.title
    return mal2md, md2mal, md2mal_title


def append_anilist_related_and_recs(manga_data, al2md, md2al_title, mal2md, md2mal_title):
    for ct, manga in enumerate(manga_data):
        # loop through related manga for this manga
        if "related_al" in manga.external_al and "related_mal" in manga.external_al:
            for idx, idal in enumerate(manga.external_al["related_al"]):
                # case 1: we know the mapping!
                # case 2: id has unknown mapping
                idal = manga.external_al["related_al"][idx]
                idmal = manga.external_al["related_mal"][idx]
                if isinstance(idal, int) and idal in al2md:
                    idmd = al2md[idal]
                    titlemd = md2al_title[idmd]
                elif isinstance(idmal, int) and idmal in mal2md:
                    idmd = mal2md[idmal]
                    titlemd = md2mal_title[idmd]
                    continue
                else:
                    continue
                # loop through the current related
                # need to see if it is already added
                already_added = False
                for related in manga.related:
                    if idmd == related["id"]:
                        already_added = True
                        break
                # if not already added, then we can append this related!!
                if not already_added:
                    manga_data[ct].related.append({"id": idmd, "title": titlemd})

        # loop through AniList user recommendations
        if "rec_al" in manga.external_al \
                and "rec_score" in manga.external_al \
                and len(manga.external_al["rec_al"]) == len(manga.external_al["rec_score"]):
            manga_data[ct].matches_al = []
            for idx, idal in enumerate(manga.external_al["rec_al"]):
                # case 1: we know the mapping!
                # case 2: id has unknown mapping
                idal = manga.external_al["rec_al"][idx]
                idmal = manga.external_al["rec_mal"][idx]
                if isinstance(idal, int) and idal in al2md:
                    idmd = al2md[idal]
                    titlemd = md2al_title[idmd]
                elif isinstance(idmal, int) and idmal in mal2md:
                    idmd = mal2md[idmal]
                    titlemd = md2mal_title[idmd]
                else:
                    continue
                # append it to our recommendation array
                score = manga.external_al["rec_score"][idx]
                manga_data[ct].matches_al.append({
                    'id': idmd,
                    'title': titlemd,
                    'url': 'https://mangadex.org/title/' + str(idmd) + '/',
                    'score': score
                })

    return manga_data
