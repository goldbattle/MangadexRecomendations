# Import general libraries
import time
import re
import sys
import os
import codecs
import requests
# from bs4 import BeautifulSoup

# import our specific functions
from functions import manga_obj
from functions import manga_utils
from functions import anilist_helpers

# script parameters
# NOTE: you will be blocked if a high thread count is chosen
# NOTE: thus pick a reasonable one (2 seems to work ok)
url_main = "https://mangadex.org"
dir_inout = "data/jsons/"
skip_already_downloaded = False
if len(sys.argv) == 3:
    id_start = int(sys.argv[1])
    id_end = int(sys.argv[2])
else:
    id_start = 1
    id_end = 60000

assert id_end > id_start
assert id_end > 0
assert id_start > 0

# set api call settings
cookies = {}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/77.0'
}

# if we have a cache'ed old file load it in
manga_data = []
manga_data_old = manga_utils.read_raw_manga_data_files(dir_inout)
print("loaded " + str(len(manga_data_old)) + " from file")
time_start = time.time()

# create output direction if not exists
cache_files = True
path_cache_manga_api = "data/page_manga_api/"
path_cache_manga_ext = "data/page_manga_ext/"
manga_utils.make_dir_if_not(path_cache_manga_api)
manga_utils.make_dir_if_not(path_cache_manga_ext)

# loop through each index page, and extract the mangas
manga_count = id_start
while manga_count < id_end:

    # create the object
    t20 = time.time()
    print("processing manga " + str(manga_count)+":")
    data = manga_obj.MangaObj()
    data.id = manga_count
    data.url = url_main + "/manga/" + str(manga_count)

    # check if this manga has already been downloaded
    already_downloaded = False
    downloaded_manga = None
    for cmp_ct, cmp_manga in enumerate(manga_data_old):
        if data.id == cmp_manga.id:
            already_downloaded = True
            downloaded_manga = cmp_manga
            break

    # if it is already downloaded and are being told not to pull
    # then we should skip this manga so we don't need to process it!
    if already_downloaded and skip_already_downloaded:
        manga_data.append(downloaded_manga)
        manga_count = manga_count + 1
        continue

    # downloading the json api endpoint for this manga
    # success = data.download_and_parse_labels_soup(headers, cookies, cache_files, path_cache_manga)
    success = data.download_and_parse_labels_json(url_main, headers, cookies, cache_files, path_cache_manga_api)
    if not success:
        manga_count = manga_count + 1
        continue
    data.download_and_parse_externals(headers, cookies, cache_files, path_cache_manga_ext)

    # nice debug for this
    t21 = time.time()
    count_labels = len(data.content) + len(data.demographic) + len(data.format) + len(data.genre) + len(data.theme)
    print("    -> "
          + str(count_labels) + " labels | "
          + str(data.count_chapters) + " chapters | "
          + str(round(data.rating, 2)) + " rating | "
          + str(len(data.related)) + " related | "
          + ("is r18" if data.is_r18 else "not r18")
          + " (" + str(round(t21 - t20, 2)) + " sec)")

    # move forward in time
    manga_data.append(data)
    manga_count = manga_count + 1


# Remove any mangas that have been added to the json with the same id/title
# This could happen if the download of the manga list takes long
# and a new manga updated/added, thus changing what is on each manga list page.
ct_before = len(manga_data)
t01 = time.time()
manga_data = manga_utils.remove_dups_from_manga_list(manga_data)
ct_after = len(manga_data)
t11 = time.time()

# nice debug print
print("===========================")
print("reduced " + str(ct_before) + " to only " + str(ct_after) + " mangas (" + str(round(t11 - t01, 2)) + " seconds)")


# build the lookup table for the anilist ids to mangadex
# for all mangadex mangas that have linked to anilist
# this will be used to reverse the anilist api ids
(al2md, md2al, md2al_title) = anilist_helpers.build_mangadex_to_anilist_id_lookup(manga_data)
(mal2md, md2mal, md2mal_title) = anilist_helpers.build_mangadex_to_myanimelist_id_lookup(manga_data)
manga_data = anilist_helpers.append_anilist_related_and_recs(manga_data, al2md, md2al_title, mal2md, md2mal_title)


# Save our json to file!
manga_utils.write_raw_manga_data_files(dir_inout, manga_data)
print("outputted to " + dir_inout)
print("script took " + str(round(time.time() - time_start, 2)) + " seconds")
