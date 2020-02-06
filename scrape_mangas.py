# Import libraries
import time
import json
import re
import codecs
import requests
import os.path
from bs4 import BeautifulSoup


# script parameters
# jan 20, 2020 -> 795 total pages
# jan 24, 2020 -> 796 total pages
# jan 25, 2020 -> 797 total pages
# feb 2, 2020 -> 800 total pages
url_main = "https://mangadex.org"
file_inout = "mangas_raw.json"
max_pages = 800
pull_from_website = False
cookies = {
    'mangadex_session': 'xxxxxxx',
    'mangadex_rememberme_token': 'xxxxxxx'
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.123 Safari/537.36'
}


# the main json object we have
if os.path.exists(file_inout):
    with open(file_inout) as json_file:
        managa_data = json.load(json_file)
else:
    managa_data = []

# loop through each index page, and extract the mangas
for i in range(0, max_pages + 1):

    # Download the page if we should get new ones
    t0 = time.time()
    filename = "pages_list/html_" + format(i, '03') + ".txt"
    if pull_from_website or not os.path.exists(filename):
        urlstr = url_main + '/titles/0/' + str(i) + '/?s=2#listing'
        print("downloading " + urlstr)
        response = requests.get(urlstr, cookies=cookies, headers=headers)
        file = codecs.open(filename, "w", "utf-8")
        file.write(response.text)
        #time.sleep(1)

    # Read the file from disk
    file = codecs.open(filename, "r", "utf-8")
    response_test = file.read()

    # Create a BeautifulSoup object
    soup = BeautifulSoup(response_test, 'html.parser')

    # Get all mangas on this page, and process them
    count_added = 0
    manga_list = soup.find_all(class_='manga-entry')
    for managa in manga_list:
        links = managa.find_all('a')
        title = links[1].getText()
        url = links[1]['href']
        url_img = links[0].find('img')['src']
        id = int(re.search(r'\d+', url).group())
        des = managa.find_all('div')[-1].getText()
        if len(title) > 0 and len(url) > 0 and len(des) > 100 and id > 0:
            managa_data.append({'id': id, 'title': title, 'url': url_main+url, 'img': url_main+url_img, 'description': des})
            count_added = count_added + 1

    # Nice debug to the user
    t1 = time.time()
    print("-> page " + str(i) + " processed " + str(count_added)
          + " mangas in " + str(round(t1 - t0, 2)) + " seconds")


# Save our json to file!
with open(file_inout, 'w') as outfile:
    outfile.write(json.dumps(managa_data, indent=4))



