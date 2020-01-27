# Import libraries
import time
import json
import re
import codecs
import requests
import os.path
from bs4 import BeautifulSoup


# script parameters
pull_from_website = False
cookies = {
    'mangadex_session': 'xxxxxxx',
    'mangadex_rememberme_token': 'xxxxxxx'
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.123 Safari/537.36'
}
file_in = "mangas_raw.json"
file_out = "mangas_genres.json"


# the main json object we have
with open(file_in) as json_file:
    managa_data = json.load(json_file)

# loop through each index page, and extract the mangas
for ct, manga in enumerate(managa_data):

    # Download the page if we should get new ones
    t0 = time.time()
    filename = "pages_main/html_" + format(manga['id'], '06') + ".txt"
    if pull_from_website or not os.path.exists(filename):
        print("downloading " + manga['url'])
        response = requests.get(manga['url'], cookies=cookies, headers=headers)
        if "is not available" in response.text:
            print("\033[93mwarning!! manga download probably failed!!\033[0m")
        file = codecs.open(filename, "w", "utf-8")
        file.write(response.text)

    # Read the file from disk
    file = codecs.open(filename, "r", "utf-8")
    response_test = file.read()

    # Create a BeautifulSoup object
    soup = BeautifulSoup(response_test, 'html.parser')

    # Content ===================================================
    count_labels = 0
    divs_cont = soup.find_all(text=re.compile('Content:'))
    managa_data[ct]["content"] = []
    if len(divs_cont) > 0:
        div_paren = divs_cont[0].parent.parent
        divs = div_paren.find_all("div")
        if len(divs) > 0:
            labels = divs[-1].find_all("a")
            for label in labels:
                managa_data[ct]["content"].append(label.getText())
                count_labels = count_labels + 1

    # Demographic ===================================================
    divs_demo = soup.find_all(text=re.compile('Demographic:'))
    managa_data[ct]["demographic"] = []
    if len(divs_demo) > 0:
        div_paren = divs_demo[0].parent.parent
        divs = div_paren.find_all("div")
        if len(divs) > 0:
            labels = divs[-1].find_all("a")
            for label in labels:
                managa_data[ct]["demographic"].append(label.getText())
                count_labels = count_labels + 1

    # Format ===================================================
    divs_format = soup.find_all(text=re.compile('Format:'))
    managa_data[ct]["format"] = []
    if len(divs_format) > 0:
        div_paren = divs_format[0].parent.parent
        divs = div_paren.find_all("div")
        if len(divs) > 0:
            labels = divs[-1].find_all("a")
            for label in labels:
                managa_data[ct]["format"].append(label.getText())
                count_labels = count_labels + 1

    # Genre ===================================================
    divs_genre = soup.find_all(text=re.compile('Genre:'))
    managa_data[ct]["genre"] = []
    if len(divs_genre) > 0:
        div_paren = divs_genre[0].parent.parent
        divs = div_paren.find_all("div")
        if len(divs) > 0:
            labels = divs[-1].find_all("a")
            for label in labels:
                managa_data[ct]["genre"].append(label.getText())
                count_labels = count_labels + 1

    # Theme ===================================================
    divs_theme = soup.find_all(text=re.compile('Theme:'))
    managa_data[ct]["theme"] = []
    if len(divs_theme) > 0:
        div_paren = divs_theme[0].parent.parent
        divs = div_paren.find_all("div")
        if len(divs) > 0:
            labels = divs[-1].find_all("a")
            for label in labels:
                managa_data[ct]["theme"].append(label.getText())
                count_labels = count_labels + 1

    # Nice debug to the user
    t1 = time.time()
    print(str(round(100*float(ct)/len(managa_data), 2)) + "% -> manga "
          + str(manga["id"]) + " added " + str(count_labels)
          + " labels in " + str(round(t1 - t0, 2)) + " seconds")


# Save our json to file!
with open(file_out, 'w') as outfile:
    outfile.write(json.dumps(managa_data, indent=4))



