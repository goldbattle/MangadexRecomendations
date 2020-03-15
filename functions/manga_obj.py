# Import general libraries
import re
import requests
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
        self.count_chapters = 0
        self.rating = 0.0
        self.content = []
        self.demographic = []
        self.format = []
        self.genre = []
        self.theme = []
        self.related = []
        self.matches = []
        self.vec_xor_cached = None

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
        if "count_chapters" in json_obj:
            self.count_chapters = json_obj["count_chapters"]
        if "rating" in json_obj:
            self.rating = json_obj["rating"]
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
        if "related" in json_obj:
            self.related = json_obj["related"]
        if "matches" in json_obj:
            self.matches = json_obj["matches"]

    def download_and_parse_labels_soup(self, headers, cookies):

        # assert that we have at least the id and url set
        assert self.id
        assert self.url

        # Download the file if needed
        print("    -> manga " + str(self.id) + " downloading " + self.url)
        response = requests.get(self.url, headers=headers)
        if "is not available" in response.text:
            print("\033[93mwarning!! manga download probably failed!!\033[0m")
            return False

        # Create a BeautifulSoup object
        soup = BeautifulSoup(response.text, 'html.parser')

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

        # Number of chapters
        span_chapter_num = soup.find('span', {'title': 'Total chapters'})
        if span_chapter_num and span_chapter_num.parent:
            self.count_chapters = int(span_chapter_num.parent.text.replace(",", ""))

        # Related by mangadex
        span_related = soup.find_all(text=re.compile('Related:'))
        if span_related and len(span_related) > 0:
            div_paren = span_related[0].parent.parent
            divs = div_paren.find_all("div")
            if len(divs) > 0:
                self.related.clear()
                labels = divs[-1].find_all("a")
                for label in labels:
                    related_url = label.get('href')
                    related_title = label.getText()
                    related_id = int(re.search(r'\d+', related_url).group())
                    self.related.append({"id": related_id, "title": related_title})

        # done!
        return True

    def download_and_parse_labels_json(self, url_main, headers, cookies):

        # assert that we have at least the id and url set
        assert self.id

        # Download the file if needed
        json_url = url_main + "/api/manga/" + str(self.id) + "/"
        print("    -> manga " + str(self.id) + " downloading " + json_url)
        response = requests.get(json_url, headers=headers)
        if "is not available" in response.text:
            print("\033[93mwarning!! manga download probably failed!!\033[0m")

        # Parse into a json file
        data = response.json()

        # ID lookups to our types
        # https://github.com/CarlosEsco/Neko/blob/master/app/src/main/java/eu/kanade
        # /tachiyomi/source/online/handlers/FilterHandler.kt
        ids_content = [9, 32, 49, 50]
        names_content = ["Ecchi", "Smut", "Gore", "Sexual Violence"]
        ids_format = [1, 4, 7, 21, 36, 42, 43, 44, 45, 46, 47, 48]
        names_format = ["4-koma", "Award Winning", "Doujinshi", "Oneshot", "Long Strip", "Adaptation", "Anthology",
                        "Web Comic", "Full Color", "User Created", "Official Colored", "Fan Colored"]
        ids_genre = [2, 3, 5, 8, 10, 13, 14, 17, 18, 20, 22, 23, 25, 28, 30, 31, 33, 35, 37, 38, 41, 51, 51, 53, 54, 55,
                     56]
        names_genre = ["Action", "Adventure", "Comedy", "Drama", "Fantasy", "Historical", "Horror", "Mecha", "Medical",
                       "Mystery", "Psychological", "Romance", "Sci-Fi", "Shoujo Ai", "Shounen Ai", "Slice of Life",
                       "Sports", "Tragedy", "Yaoi", "Yuri", "Isekai", "Crime", "Magical Girls", "Philosophical",
                       "Superhero", "Thriller", "Wuxia"]
        ids_themes = [6, 11, 12, 16, 19, 24, 34, 40, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73,
                      74, 75, 76, 77, 78, 79, 80, 81, 82, 83]
        names_themes = ["Cooking", "Gyaru", "Harem", "Martial Arts", "Music", "School Life", "Supernatural",
                        "Video Games", "Aliens", "Animals", "Crossdressing", "Demons", "Delinquents", "Genderswap",
                        "Ghosts", "Monster Girls", "Loli", "Magic", "Military", "Monsters", "Ninja", "Office Workers",
                        "Police", "Post-Apocalyptic", "Reincarnation", "Reverse Harem", "Samurai", "Shota", "Survival",
                        "Time Travel", "Vampires", "Traditional Games", "Virtual Reality", "Zombies", "Incest"]

        assert len(ids_content) == len(names_content)
        assert len(ids_format) == len(names_format)
        assert len(ids_genre) == len(names_genre)
        assert len(ids_themes) == len(names_themes)

        # Loop through each genre and parse it
        self.content.clear()
        self.format.clear()
        self.genre.clear()
        self.theme.clear()
        if "manga" in data and "genres" in data["manga"]:
            for genre_id in data["manga"]["genres"]:
                if genre_id in ids_content:
                    self.content.append(names_content[ids_content.index(genre_id)])
                if genre_id in ids_format:
                    self.format.append(names_format[ids_format.index(genre_id)])
                if genre_id in ids_genre:
                    self.genre.append(names_genre[ids_genre.index(genre_id)])
                if genre_id in ids_themes:
                    self.theme.append(names_themes[ids_themes.index(genre_id)])

        # Number of chapters
        if "chapter" in data:
            self.count_chapters = len(data["chapter"])

    def compute_xor_label_vector(self, all_labels):

        # return cache if we have it
        if self.vec_xor_cached:
            return self.vec_xor_cached

        # create default vector for each label
        vec = [False] * len(all_labels)

        # loop through each label
        # if we have it, set to true in our vec
        for idx, item in enumerate(all_labels):
            if self.demographic and item in self.demographic:
                vec[idx] = True
            if self.format and item in self.format:
                vec[idx] = True
            if self.genre and item in self.genre:
                vec[idx] = True
            if self.theme and item in self.theme:
                vec[idx] = True

        # finally return the list of matches
        self.vec_xor_cached = vec
        return self.vec_xor_cached
