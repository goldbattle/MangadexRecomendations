# Import general libraries
import re
import os
import codecs
import requests
import json
from datetime import datetime
# from bs4 import BeautifulSoup

# import our specific functions
from functions import manga_utils


class MangaObj:

    def __init__(self, json_obj=None):

        # default values for our class
        self.id = None
        self.title = None
        self.url = None
        self.description = None
        self.is_r18 = False
        self.count_chapters = 0
        self.last_upload = 0
        self.last_updated = "unknown"
        self.rating = 0.0
        self.content = []
        self.demographic = []
        self.format = []
        self.genre = []
        self.theme = []
        self.related = []
        self.matches = []
        self.matches_al = []
        self.vec_xor_cached = None

        # external ids (al = AniList, mu = MangaUpdates, mal = MyAnimeList)
        self.external = {}
        self.external_al = {}

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
        if "is_r18" in json_obj:
            self.is_r18 = json_obj["is_r18"]
        if "count_chapters" in json_obj:
            self.count_chapters = json_obj["count_chapters"]
        if "last_upload" in json_obj:
            self.last_upload = json_obj["last_upload"]
        if "last_updated" in json_obj:
            self.last_updated = json_obj["last_updated"]
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
        if "matches_al" in json_obj:
            self.matches_al = json_obj["matches_al"]
        if "vec_xor_cached" in json_obj:
            self.vec_xor_cached = json_obj["vec_xor_cached"]
        if "external" in json_obj:
            self.external = json_obj["external"]
        if "external_al" in json_obj:
            self.external_al = json_obj["external_al"]

    # def download_and_parse_labels_soup(self, headers, cookies, cache_files, cache_path):
    #
    #     # assert that we have at least the id and url set
    #     assert self.id
    #     assert self.url
    #
    #     # Download the page if we should get new ones or read from cache
    #     filename = cache_path + format(self.id, '06') + ".txt"
    #     if cache_files and os.path.exists(filename):
    #         print("    -> manga " + str(self.id) + " loading " + filename)
    #         file = codecs.open(filename, "r", "utf-8")
    #         response_text = file.read()
    #         save_to_disk = False
    #     else:
    #         print("    -> manga " + str(self.id) + " downloading " + self.url)
    #         try:
    #             response = requests.get(self.url, headers=headers, cookies=cookies)
    #             response_text = response.text
    #             time.sleep(0.5)
    #         except:
    #             response_text = ""
    #         save_to_disk = True
    #
    #     # Cache to disk if we need too
    #     if cache_files and save_to_disk:
    #         print("    -> manga " + str(self.id) + " saving " + filename)
    #         file = codecs.open(filename, "w", "utf-8")
    #         file.write(response_text)
    #
    #     # Check if successful download
    #     if "is not available" in response_text:
    #         print("\033[93mwarning!! manga download probably failed!!\033[0m")
    #         return False
    #
    #     # Create a BeautifulSoup object
    #     soup = BeautifulSoup(response_text, 'html.parser')
    #
    #     # Content
    #     divs_cont = soup.find_all(text=re.compile('Content:'))
    #     self.content = manga_utils.get_labels_from_soup_obj(divs_cont)
    #
    #     # Demographic
    #     divs_demo = soup.find_all(text=re.compile('Demographic:'))
    #     self.demographic = manga_utils.get_labels_from_soup_obj(divs_demo)
    #
    #     # Format
    #     divs_format = soup.find_all(text=re.compile('Format:'))
    #     self.format = manga_utils.get_labels_from_soup_obj(divs_format)
    #
    #     # Genre
    #     divs_genre = soup.find_all(text=re.compile('Genre:'))
    #     self.genre = manga_utils.get_labels_from_soup_obj(divs_genre)
    #
    #     # Theme
    #     divs_theme = soup.find_all(text=re.compile('Theme:'))
    #     self.theme = manga_utils.get_labels_from_soup_obj(divs_theme)
    #
    #     # Number of chapters
    #     span_chapter_num = soup.find('span', {'title': 'Total chapters'})
    #     if span_chapter_num and span_chapter_num.parent:
    #         self.count_chapters = int(span_chapter_num.parent.text.replace(",", ""))
    #
    #     # Related by mangadex
    #     span_related = soup.find_all(text=re.compile('Related:'))
    #     if span_related and len(span_related) > 0:
    #         div_paren = span_related[0].parent.parent
    #         divs = div_paren.find_all("div")
    #         if len(divs) > 0:
    #             self.related.clear()
    #             labels = divs[-1].find_all("a")
    #             for label in labels:
    #                 related_url = label.get('href')
    #                 related_title = label.getText()
    #                 related_id = int(re.search(r'\d+', related_url).group())
    #                 self.related.append({"id": related_id, "title": related_title})
    #
    #     # External links
    #     divs_external_info = soup.find_all(text=re.compile('Information:'))
    #     if divs_external_info and len(divs_external_info) > 0:
    #         div_paren = divs_external_info[0].parent.parent
    #         divs = div_paren.find_all("div")
    #         if len(divs) > 0:
    #             self.external = {}
    #             links = divs[-1].find_all("a")
    #             for link in links:
    #                 external_link = link.get('href')
    #                 # external_title = link.getText()
    #                 # print("\t\t-> " + external_title + " " + external_link)
    #                 # MangaUpdates https://www.mangaupdates.com/series.html?id=64690
    #                 if "mangaupdates.com" in external_link:
    #                     self.external["mu"] = int(re.search(r'\d+', external_link).group())
    #                 # AniList https://anilist.co/manga/65013/
    #                 if "anilist.co" in external_link:
    #                     self.external["al"] = int(re.search(r'\d+', external_link).group())
    #                 # MyAnimeList https://myanimelist.net/manga/35013
    #                 if "myanimelist.net" in external_link:
    #                     self.external["mal"] = int(re.search(r'\d+', external_link).group())
    #
    #     # done!
    #     return True

    def download_and_parse_labels_json(self, url_main, headers, cookies, cache_files, cache_path):

        # assert that we have at least the id and url set
        assert self.id

        # Download the page if we should get new ones or read from cache
        filename = cache_path + format(self.id, '06') + ".txt"
        json_url = url_main + "/api/v2/manga/" + str(self.id) + "/?include=chapters"
        if cache_files and os.path.exists(filename):
            print("    -> loading " + filename)
            file = codecs.open(filename, "r", "utf-8")
            response_text = file.read()
            save_to_disk = False
        else:
            print("    -> downloading " + json_url)
            try:
                response = requests.get(json_url, headers=headers, cookies=cookies)
                response_text = response.text
            except:
                response_text = ""
            save_to_disk = True

        # Cache to disk if we need too
        if cache_files and save_to_disk:
            print("    -> saving " + filename)
            file = codecs.open(filename, "w", "utf-8")
            file.write(response_text)

        # Parse into a json file, return if error
        try:
            data = json.loads(response_text)
            if data["code"] == 404 or data["status"] == "error":
                return False
            data = data["data"]
        except (KeyError, ValueError, TypeError, json.JSONDecodeError):
            print("\033[93mwarning!! manga download probably failed!!\033[0m")
            return False

        # check if valid
        if "manga" not in data or "chapters" not in data:
            print("\033[93mwarning!! manga download probably failed!!\033[0m")
            return False
        if "tags" not in data["manga"] or "id" not in data["manga"] or "publication" not in data["manga"] or "links" not in data["manga"]:
            print("\033[93mwarning!! manga download probably failed!!\033[0m")
            return False

        # ID lookups to our types
        # Content, Format, Genre, Theme
        # https://mangadex.org/api/v2/tag
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
                      74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85]
        names_themes = ["Cooking", "Gyaru", "Harem", "Martial Arts", "Music", "School Life", "Supernatural",
                        "Video Games", "Aliens", "Animals", "Crossdressing", "Demons", "Delinquents", "Genderswap",
                        "Ghosts", "Monster Girls", "Loli", "Magic", "Military", "Monsters", "Ninja", "Office Workers",
                        "Police", "Post-Apocalyptic", "Reincarnation", "Reverse Harem", "Samurai", "Shota", "Survival",
                        "Time Travel", "Vampires", "Traditional Games", "Virtual Reality", "Zombies", "Incest",
                        "Mafia", "Villainess"]

        assert len(ids_content) == len(names_content)
        assert len(ids_format) == len(names_format)
        assert len(ids_genre) == len(names_genre)
        assert len(ids_themes) == len(names_themes)

        # Load our manga id information
        self.id = data["manga"]["id"]
        self.title = data["manga"]["title"]
        self.description = data["manga"]["description"]

        # Loop through each genre and parse it
        self.content.clear()
        self.format.clear()
        self.genre.clear()
        self.theme.clear()
        for genre_id in data["manga"]["tags"]:
            if genre_id in ids_content:
                self.content.append(names_content[ids_content.index(genre_id)])
            if genre_id in ids_format:
                self.format.append(names_format[ids_format.index(genre_id)])
            if genre_id in ids_genre:
                self.genre.append(names_genre[ids_genre.index(genre_id)])
            if genre_id in ids_themes:
                self.theme.append(names_themes[ids_themes.index(genre_id)])

        # Number of chapters
        self.count_chapters = len(data["chapters"])

        # Last upload
        self.last_upload = data["manga"]["lastUploaded"]

        # is r18
        self.is_r18 = bool(data["manga"]["isHentai"])

        # rating
        self.rating = data["manga"]["rating"]["bayesian"]

        # demographic
        ids_demographic = [1, 2, 3, 4]
        names_demographic = ["Shounen", "Shoujo", "Seinen", "Josei"]
        self.demographic.clear()
        if data["manga"]["publication"]["demographic"] in ids_demographic:
            self.demographic.append(names_demographic[ids_demographic.index(data["manga"]["publication"]["demographic"])])

        # related
        ids_rec_type = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        name_rec_type = ["Prequel", "Sequal", "Adapted from", "Spin-off", "Side story",
                         "Main story", "Alternate story", "Doujinshi", "Based on",
                         "Coloured", "Monochrome", "Schared universe", "Same franchise",
                         "Pre-serialization", "Serialization"]
        self.related.clear()
        for related in data["manga"]["relations"]:
            self.related.append({
                "id": related["id"],
                "title": related["title"],
                "type": name_rec_type[ids_rec_type.index(related["type"])]
            })

        # externals
        self.external = {}
        if data["manga"]["links"] and "mu" in data["manga"]["links"]:
            self.external["mu"] = data["manga"]["links"]["mu"]
        if data["manga"]["links"] and "al" in data["manga"]["links"]:
            self.external["al"] = data["manga"]["links"]["al"]
        if data["manga"]["links"] and "mal" in data["manga"]["links"]:
            self.external["mal"] = data["manga"]["links"]["mal"]

        # set last updated timestamp to current time
        self.last_updated = datetime.utcnow().strftime("%B %d, %Y %H:%M:%S") + " UTC"

        return True

    def download_and_parse_externals(self, headers, cookies, cache_files, cache_path):

        # # Check that we have a mu key
        # # MangaUpdates https://www.mangaupdates.com/series.html?id=64690
        # if "mu" in self.external:
        #
        #     # Download the page if we should get new ones or read from cache
        #     file = cache_path + format(self.id, '06') + "_mu.txt"
        #     url = "https://www.mangaupdates.com/series.html?id=" + str(self.external["mu"])
        #     if cache_files and os.path.exists(file):
        #         print("    -> manga " + str(self.id) + " loading " + file)
        #         file = codecs.open(file, "r", "utf-8")
        #         response_text = file.read()
        #         save_to_disk = False
        #     else:
        #         print("    -> manga " + str(self.id) + " downloading " + url)
        #         try:
        #             response = requests.get(url, headers=headers)
        #             response_text = response.text
        #             time.sleep(0.5)
        #         except:
        #             response_text = ""
        #         save_to_disk = True
        #
        #     # Cache to disk if we need too
        #     if cache_files and save_to_disk:
        #         print("    -> manga " + str(self.id) + " saving " + file)
        #         file = codecs.open(file, "w", "utf-8")
        #         file.write(response_text)
        #
        #     # Create a BeautifulSoup object
        #     soup = BeautifulSoup(response_text, 'html.parser')
        #
        #     # Get the full description
        #     # NOTE: if there is an expand button, grab the "more" / longer desc
        #     div_desc = soup.find_all(class_="sContent")
        #     if div_desc and len(div_desc) > 0 and len(div_desc[0].getText()) > 100:
        #         description = div_desc[0].getText()
        #         div_more = div_desc[0].find(id="div_desc_more")
        #         if div_more:
        #             description = div_more.getText()
        #             description = description.replace('Less...', '')
        #         self.external_description["mu"] = description.strip()
        #         # print("MU ================================")
        #         # print(description)

        # Check that we have an al key
        # AniList https://anilist.co/manga/65013/
        if "al" in self.external:

            # formulate the graphql query format
            # https://anilist.co/graphiql
            # https://anilist.gitbook.io/anilist-apiv2-docs/overview/graphql/getting-started#example-query-request
            query = '''
            query ($id: Int) {
              Media (id: $id, type: MANGA) {
                id
                title {
                  userPreferred
                }
                description
                status
                relations {
                  edges {
                    relationType
                    node {
                      id
                      idMal
                      format
                      title {
                        userPreferred
                      }
                    }
                  }
                }
                recommendations {
                  edges {
                    node {
                        mediaRecommendation {
                            id
                            idMal
                            format
                            title {
                              userPreferred
                            }
                        }
                      rating
                    }
                  }
                }
              }
            }
            '''
            variables = {'id': self.external["al"]}
            url = 'https://graphql.anilist.co'

            # Download the page if we should get new ones or read from cache
            file = cache_path + format(self.id, '06') + "_al.txt"
            if cache_files and os.path.exists(file):
                print("    -> loading " + file)
                file = codecs.open(file, "r", "utf-8")
                response_text = file.read()
                save_to_disk = False
            else:
                print("    -> downloading https://anilist.co/manga/" + str(self.external["al"]))
                try:
                    response = requests.post(url, json={'query': query, 'variables': variables})
                    response_text = response.text
                except:
                    response_text = ""
                save_to_disk = True

            # Cache to disk if we need too
            if cache_files and save_to_disk:
                print("    -> saving " + file)
                file = codecs.open(file, "w", "utf-8")
                file.write(response_text)

            # Parse into a json file, skip if error
            # NOTE: we skip if the description was copied from manga updates...
            try:
                data = json.loads(response_text)
                if data and "data" in data \
                        and "Media" in data["data"] \
                        and "description" in data["data"]["Media"] \
                        and len(data["data"]["Media"]["description"]) > 100:
                    # and "mangaupdates" not in data["data"]["Media"]["description"].lower():
                    description = data["data"]["Media"]["description"]
                    # description = description.replace('<br>', '\n')
                    # description = re.sub(r'[\r\n][\r\n]{2,}', '\n', description)
                    self.external_al["description"] = description.strip()
                    # print("AL ================================")
                    # print(description)

                    # Go through and get related manga
                    # NOTE: we need to ensure this is a MANGA type
                    # NOTE: it could be a TV show relation, but we don't care about that
                    if "relations" in data["data"]["Media"] \
                            and "edges" in data["data"]["Media"]["relations"] \
                            and len(data["data"]["Media"]["relations"]["edges"]) > 0:
                        related_id_al = []
                        related_id_mal = []
                        for related in data["data"]["Media"]["relations"]["edges"]:
                            if related["node"]["format"] != "MANGA":
                                continue
                            related_id_al.append(related["node"]["id"])
                            related_id_mal.append(related["node"]["idMal"])
                        self.external_al["related_al"] = related_id_al
                        self.external_al["related_mal"] = related_id_mal

                    # Go through and get manga recommendations
                    # NOTE: ensure we have a positive rating from the users
                    # NOTE: we need to ensure this is a MANGA type
                    # NOTE: it could be a TV show relation, but we don't care about that
                    if "recommendations" in data["data"]["Media"] \
                            and "edges" in data["data"]["Media"]["recommendations"] \
                            and len(data["data"]["Media"]["recommendations"]["edges"]) > 0:
                        rec_id_al = []
                        rec_id_mal = []
                        rec_score = []
                        for rec in data["data"]["Media"]["recommendations"]["edges"]:
                            if rec["node"]["rating"] < 0:
                                continue
                            if rec["node"]["mediaRecommendation"]["format"] != "MANGA":
                                continue
                            rec_id_al.append(rec["node"]["mediaRecommendation"]["id"])
                            rec_id_mal.append(rec["node"]["mediaRecommendation"]["idMal"])
                            rec_score.append(rec["node"]["rating"])
                        self.external_al["rec_al"] = rec_id_al
                        self.external_al["rec_mal"] = rec_id_mal
                        self.external_al["rec_score"] = rec_score

            except (ValueError, TypeError, json.JSONDecodeError):
                pass

        # done!
        return True

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
