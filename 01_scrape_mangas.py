# Import general libraries
import time
import json
import re
import codecs
import requests
import os.path
from bs4 import BeautifulSoup

# import our specific functions
from functions import manga_obj
from functions import manga_utils

# script parameters
# jan 20, 2020 -> 795 total pages
# jan 24, 2020 -> 796 total pages
# jan 25, 2020 -> 797 total pages
# feb 2, 2020 -> 800 total pages
url_main = "https://mangadex.org"
file_out = "output/mangas_raw.json"
max_pages = 800
pull_from_website = False
cookies = {
    'mangadex_session': 'xxxxxxxxxxxxxxx',
    'mangadex_rememberme_token': 'xxxxxxxxxxxxxxx'
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.123 Safari/537.36'
}

# the main json object we have
manga_data = []
time_start = time.time()

# loop through each index page, and extract the mangas
for i in range(0, max_pages + 1):

    # Download the page if we should get new ones
    t0 = time.time()
    filename = "data/pages_list/html_" + format(i, '03') + ".txt"
    if pull_from_website or not os.path.exists(filename):
        urlstr = url_main + '/titles/0/' + str(i) + '/?s=2#listing'
        print("downloading " + urlstr)
        response = requests.get(urlstr, cookies=cookies, headers=headers)
        file = codecs.open(filename, "w", "utf-8")
        file.write(response.text)

    # Read the file from disk
    file = codecs.open(filename, "r", "utf-8")
    response_test = file.read()

    # Create a BeautifulSoup object
    soup = BeautifulSoup(response_test, 'html.parser')

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
        # data.img = url_main+links[0].find('img')['src']
        data.description = manga.find_all('div')[-1].getText()
        data.download_and_parse_labels(headers, cookies, pull_from_website)

        # nice debug for this
        t21 = time.time()
        count_labels = len(data.content) + len(data.demographic) + len(data.format) + len(data.genre) + len(data.theme)
        print("    -> manga " + str(data.id) + " added " + str(count_labels)
              + " labels in " + str(round(t21 - t20, 2)) + " seconds")

        # move forward in time
        manga_data.append(data)
        count_added = count_added + 1

    # Nice debug to the user
    t1 = time.time()
    print(str(round(100 * float(i + 1) / (max_pages + 1), 2)) +
          "% -> page " + str(i) + " processed " + str(count_added)
          + " mangas in " + str(round(t1 - t0, 2)) + " seconds")

# Remove any mangas that have been added to the json with the same id/title
# This could happen if the download of the manga list takes long
# and a new manga updated/added, thus changing what is on each manga list page.
ct_before = len(manga_data)
t0 = time.time()
manga_data = manga_utils.remove_dups_from_manga_list(manga_data)
ct_after = len(manga_data)
t1 = time.time()

# nice debug print
print("===========================")
print("reduced " + str(ct_before) + " to only " + str(ct_after) + " mangas (" + str(round(t1 - t0, 2)) + " seconds)")

# create output direction if not exists
if not os.path.exists(os.path.dirname(file_out)):
    os.makedirs(os.path.dirname(file_out))

# Save our json to file!
with open(file_out, 'w') as outfile:
    json.dump([ob.__dict__ for ob in manga_data], outfile, indent=4, sort_keys=True)
print("outputted to " + file_out)
print("script took " + str(round(time.time() - time_start, 2)) + " seconds")
