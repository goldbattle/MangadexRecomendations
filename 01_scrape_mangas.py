# Import general libraries
import time
import re
import sys
import requests
from bs4 import BeautifulSoup

# import our specific functions
from functions import manga_obj
from functions import manga_utils

# script parameters
# NOTE: you will be blocked if a high thread count is chosen
# NOTE: thus pick a reasonable one (2 seems to work ok)
url_main = "https://mangadex.org"
dir_inout = "output/"
pull_from_website = False
cookies = {}
if len(sys.argv) == 3:
    cookies['mangadex_session'] = sys.argv[1]
    cookies['mangadex_rememberme_token'] = sys.argv[2]
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64)'
}

# if we have a cache'ed old file load it in
manga_data = manga_utils.read_raw_manga_data_files(dir_inout)
print("loaded " + str(len(manga_data)) + " from file")
time_start = time.time()

# loop through each index page, and extract the mangas
page_count = 1
count_num_times_we_had_zero_mangas = 0
while count_num_times_we_had_zero_mangas < 2:

    # Download the page if we should get new ones
    t0 = time.time()
    urlstr = url_main + '/titles/0/' + str(page_count) + '/?s=2#listing'
    print("downloading " + urlstr)
    response = requests.get(urlstr, headers=headers, cookies=cookies)

    # Create a BeautifulSoup object
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get all mangas on this page, and process them
    count_added = 0
    manga_list = soup.find_all(class_='manga-entry')
    for manga in manga_list:

        # extract from html
        links = manga.find_all('a')

        # create the object
        t20 = time.time()
        data = manga_obj.MangaObj()
        data.url = url_main + links[1]['href']
        data.id = int(re.search(r'\d+', data.url).group())
        data.title = links[1].getText()
        data.description = manga.find_all('div')[-1].getText()

        # get the baysian rating of this manga
        stats = manga.find_all('ul')
        if stats and len(stats) > 0:
            stats = stats[0].findAll('li')
            if stats and len(stats) > 0:
                data.rating = float(stats[0].find_all('span')[-1].text)

        # check if this manga has already been downloaded
        already_downloaded = False
        for ct, manga in enumerate(manga_data):
            if data.id == manga.id:
                already_downloaded = True
                break

        # if it is already downloaded and are being told not to pull
        # then we should skip this manga so we don't need to process it!
        if already_downloaded and not pull_from_website:
            continue

        # now lets download the labels if this is a new manga
        # NOTE: the json api endpoint doesn't let us get the demographic
        # NOTE: thus we recommend using the soup version of this
        # NOTE: we fall back on the JSON API method if we can't access this manga
        success = data.download_and_parse_labels_soup(headers, cookies)
        if not success:
            data.download_and_parse_labels_json(url_main, headers, cookies)
        time.sleep(1)

        # nice debug for this
        t21 = time.time()
        count_labels = len(data.content) + len(data.demographic) + len(data.format) + len(data.genre) + len(data.theme)
        print("    -> manga " + str(data.id) + " has "
              + str(count_labels) + " labels | "
              + str(data.count_chapters) + " chapters | "
              + str(round(data.rating, 2)) + " rating | "
              + str(len(data.related)) + " related (" + str(round(t21 - t20, 2)) + " sec)")

        # move forward in time
        manga_data.append(data)
        count_added = count_added + 1

    # here we should how many mangas we have extracted from this page
    # we will know we have reached the end of the listing if we have zero
    if len(manga_list) < 1:
        count_num_times_we_had_zero_mangas += 1

    # Nice debug to the user
    t1 = time.time()
    print("page " + str(page_count) + " processed " + str(count_added) + " mangas in "
          + str(round(t1 - t0, 2)) + " seconds")
    page_count = page_count + 1
    #time.sleep(5)

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

# Save our json to file!
manga_utils.write_raw_manga_data_files(dir_inout, manga_data)
print("outputted to " + dir_inout)
print("script took " + str(round(time.time() - time_start, 2)) + " seconds")
