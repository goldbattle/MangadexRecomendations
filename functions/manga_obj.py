# Import general libraries
import time
import json
import re
import codecs
import requests
import os.path
from bs4 import BeautifulSoup

# import our specific functions
from functions import manga_utils


class MangaObj:

    def __init__(self, json_obj=None):

        # default values for our class
        self.id = None
        self.title = None
        self.url = None
        self.description = None
        self.content = None
        self.demographic = None
        self.format = None
        self.genre = None
        self.theme = None
        self.matches = []

        # if we have a json object then we should load it
        # if the json is missing things they will stay None
        if json_obj:
            self.load_from_json(json_obj)

    def load_from_json(self, json_obj):
        if "id" in json_obj:
            self.id = json_obj["id"]
        if "title" in json_obj:
            self.title = json_obj["title"]
        if "url" in json_obj:
            self.url = json_obj["url"]
        if "description" in json_obj:
            self.description = json_obj["description"]
        if "content" in json_obj:
            self.content = json_obj["content"]
        if "demographic" in json_obj:
            self.demographic = json_obj["demographic"]
        if "format" in json_obj:
            self.format = json_obj["format"]
        if "genre" in json_obj:
            self.genre = json_obj["genre"]
        if "theme" in json_obj:
            self.theme = json_obj["theme"]
        if "matches" in json_obj:
            self.matches = json_obj["matches"]

    def download_and_parse_labels(self, headers, cookies, pull_from_website):

        # assert that we have at least the id and url set
        assert self.id
        assert self.url

        # Download the file if needed, otherwise load from disk
        filename = "data/pages_main/html_" + format(self.id, '06') + ".txt"
        if pull_from_website or not os.path.exists(filename):
            print("    -> manga " + str(self.id) + " downloading " + self.url)
            response = requests.get(self.url, cookies=cookies, headers=headers)
            if "is not available" in response.text:
                print("\033[93mwarning!! manga download probably failed!!\033[0m")
            file = codecs.open(filename, "w", "utf-8")
            file.write(response.text)

        # Read the file from disk
        file = codecs.open(filename, "r", "utf-8")
        response_test = file.read()

        # Create a BeautifulSoup object
        soup = BeautifulSoup(response_test, 'html.parser')

        # Content
        divs_cont = soup.find_all(text=re.compile('Content:'))
        self.content = manga_utils.get_labels_from_soup_obj(divs_cont)

        # Demographic
        divs_demo = soup.find_all(text=re.compile('Demographic:'))
        self.demographic = manga_utils.get_labels_from_soup_obj(divs_demo)

        # Format
        divs_format = soup.find_all(text=re.compile('Format:'))
        self.format = manga_utils.get_labels_from_soup_obj(divs_format)

        # Genre
        divs_genre = soup.find_all(text=re.compile('Genre:'))
        self.genre = manga_utils.get_labels_from_soup_obj(divs_genre)

        # Theme
        divs_theme = soup.find_all(text=re.compile('Theme:'))
        self.theme = manga_utils.get_labels_from_soup_obj(divs_theme)

    def compute_xor_label_vector(self, all_labels):

        # create default vector for each label
        vec = [False] * len(all_labels)

        # loop through each label
        # if we have it, set to true in our vec
        for id, item in enumerate(all_labels):
            if self.demographic and item in self.demographic:
                vec[id] = True
            if self.format and item in self.format:
                vec[id] = True
            if self.genre and item in self.genre:
                vec[id] = True
            if self.theme and item in self.theme:
                vec[id] = True

        # finally return the list of matches
        return vec
