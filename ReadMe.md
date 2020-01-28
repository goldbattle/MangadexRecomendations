# MangaDex Recommendations

This repo has both the scraping utilities and the matching utilities to find mangas which are close in content to others. The idea is to create a recommendation system outside of MangaDex since there isn't one and thus allow for users to discover other content. Right now it is pretty rudimentary, but seems to give ok results most of the time.


## Manga JSON Download

* [**Latest Recommendation File**](https://github.com/goldbattle/MangadexRecomendations/releases/download/0.0.1/mangas_compressed.json)
* [link](https://github.com/goldbattle/MangadexRecomendations/releases/download/0.0.1/mangas_compressed.json) - v0.0.1 initial release of matches, Jan 28, 2020



## Scripts Descriptions

* Step 1 - `scrape_mangas.py` - Download the manga list from the manga title directory. There should be 40 mangas per page and the number of pages will increase as new mangas are added to the site. You will need to get your session cookies to allow for reliable access.
* Step 2 - `scrape_cleandups.py` - This will remove any mangas that have been added to the json with the same id/title. This could happen if the download of the manga list takes long, and a new manga updated/added, thus changing what is on each manga list page.
* Step 3 - `scrape_genres.py` - In the previous step we only downloaded the title, id, url, and description so we want to next get more information about each manga not listed on the main website. This will download each page of the manga and extract the genre, topics, themes, etc. You will need to get your session cookies to allow for access to most mangas here.
* Step 4 - `calc_simularities.py` - This will calculate the similarity between each manga and all others. We require that there is a minimum overlap of genres and demographics to narrow down bad matches. We then use term frequency–inverse document frequency (Tfidf) to score how much the title+description+labels match. We then pick the top scores that pass a threshold.
* Step 5 - `calc_compress.py` - Removes all un-needed stuff to reduce the size of the final file. Just keeps the id, title, score, and url.





