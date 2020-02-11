# MangaDex Recommendations

This repo has both the scraping utilities and the matching utilities to find mangas which are close in content to others. The idea is to create a recommendation system outside of MangaDex since there isn't one and thus allow for users to discover other content. Right now it is pretty rudimentary, but seems to give ok results most of the time.


## Manga JSON Download

This file gets updated automatically at midnight UTC.
This link should always have the latest related recommendations.
Please click the link below, or you can find it in the output directory above.

[**LATEST RECOMMENDATION FILE DOWNLOAD LINK**](https://raw.githubusercontent.com/goldbattle/MangadexRecomendations/master/output/mangas_compressed.json)




## Scripts Descriptions

* Step 1 - `01_scrape_mangas.py` - Download the manga list from the manga title directory. There should be 40 mangas per page and the number of pages will increase as new mangas are added to the site. You will need to get your session cookies to allow for reliable access. We also download each page of the manga and extract the genre, topics, themes, etc. You will need to get your session cookies to allow for access to most mangas here. Finally we will remove any mangas that have been added to the json with the same id/title. This could happen if the download of the manga list takes long, and a new manga updated/added, thus changing what is on each manga list page.
* Step 2 - `02_calc_similarities.py` - This will calculate the similarity between each manga and all others. We require that there is a minimum overlap of labels to narrow down bad matches. We then use term frequency–inverse document frequency (Tfidf) to score how much the title+description match. We also score based on the intersection between each manga's labels (genres, themes, demographic, etc) and combine it with the Tfidf score. We then pick the top scores that pass a threshold. Finally, we also export a compressed file that just keeps the id, title, score, and url.





