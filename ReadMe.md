# Neko Recommendations

This repo has both the scraping and matching utilities to find mangas which are close in content to others.
The idea is to create a recommendation system outside MangaDex since there isn't one and thus allow for users to discover other content.
Right now it is pretty rudimentary, but seems to give ok results most of the time.

## Dependencies

The main dependencies required by the project is a Python 3 environment and the following packages:
```
pip3 install requests
pip3 install bs4 # no longer needed
pip3 install scikit-learn
```

## Scripts Descriptions

* `01_scrape_mangas.py` - This will query the main Mangadex api endpoint and get the latest information for all manga on the website. Additionally, this script will query AniList to try to get any additional information. This content is then recorded to our "database" which consists of a series of JSON files.
  
* `02_calc_similarities.py` - This will calculate the similarity between each manga and all others. We require that there is a minimum overlap of labels to narrow down bad matches. We then use term frequency–inverse document frequency (Tfidf) to score how much the title+description match. We also score based on the intersection between each manga's labels (genres, themes, demographic, etc) and combine it with the Tfidf score. We then pick the top scores that pass a threshold. Finally, we export a compressed file that can be used by Neko.
  
* `03_inspect.py` - Small script to create a json sub-set of specified manga. Useful if you want to look at the compressed output for a specific mangadex id.






