# Import libraries
import time
import re
import json
import nltk
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


# files in and out and settings
file_in = "mangas_genres.json"
file_out = "mangas_matched.json"
min_same_genres = 1
min_same_demographic = 1


# Open the manga json file and load
with open(file_in) as json_file:
    managa_data = json.load(json_file)
print("loaded " + str(len(managa_data)) + " mangas")


# Loop through each manga, and create a corpus of descriptions
# NOTE: we remove non-numeric and non-alphabetical chars
# NOTE: we remove non-english words, is this really ok?
# NOTE: should we add the genres here?? not sure..
corpus = []
printable = set(string.printable)
for ct, manga1 in enumerate(managa_data):
    str_raw = manga1["title"]+". "+manga1["description"]
    str_raw = re.sub(r'http\S+', '', str_raw)
    str_raw = ''.join(filter(lambda x: x in printable, str_raw))
    #str_eng = re.sub(r'[^A-Za-z0-9 ]+', '', manga1["title"]+". "+manga1["description"])
    corpus.append((ct, str_raw))


# build a TF/IDF matrix for each paper
# https://markhneedham.com/blog/2016/07/27/scitkit-learn-tfidf-and-cosine-similarity-for-computer-science-papers/
tf = TfidfVectorizer(analyzer='word', min_df=0, ngram_range=(1, 3), stop_words='english')
tfidf_matrix = tf.fit_transform([content for file, content in corpus])


# top n similar papers based on cosine similarity
def find_similar(tfidf_matrix, index, top_n=5):
    cosine_similarities = linear_kernel(tfidf_matrix[index:index+1], tfidf_matrix).flatten()
    related_docs_indices = [i for i in cosine_similarities.argsort()[::-1] if i != index]
    return [(index, cosine_similarities[index]) for index in related_docs_indices][0:top_n]


# cleaned data file with only mangas that have matches
managa_data_out = []

# loop through each and find the top matches
for ct, manga1 in enumerate(managa_data):

    # nice debug print of which one we are processing
    print(str(round(100*float(ct)/len(managa_data), 2)) + "% -> manga "+str(managa_data[ct]["id"])+" - "+manga1["title"]+" - "+manga1["url"])

    # get the top matches, and then only select good ones
    count_matched = 0
    manga_temp = manga1
    manga_temp["matches"] = []
    for index, score in find_similar(tfidf_matrix, ct, 100):

        # skip if low score value
        if score < 0.01:
            continue

        # skip if already have our top 24
        if len(manga_temp["matches"]) > 24:
            break

        # count number of genres are the same
        idx = corpus[index][0]
        same_genre_ct = 0
        for genre1 in manga1["genre"]:
            for genre2 in managa_data[idx]["genre"]:
                if genre1 == genre2:
                    same_genre_ct = same_genre_ct + 1

        # count number of demographic are the same
        same_demographic_ct = 0
        for demo1 in manga1["demographic"]:
            for demo2 in managa_data[idx]["demographic"]:
                if demo1 == demo2:
                    same_demographic_ct = same_demographic_ct + 1

        # skip if not enough same genres
        if same_genre_ct < min_same_genres or same_demographic_ct < min_same_demographic:
            continue

        # else we can add it to our data structure
        manga_temp["matches"].append({
            'id': managa_data[idx]["id"],
            'title': managa_data[idx]["title"],
            'url':  managa_data[idx]["url"],
            'score': score
        })
        count_matched = count_matched + 1

        # nice debug print
        print("   match " + str(managa_data[idx]["id"]) + " (" + str(round(score, 3)) + ")"
              + " - " + managa_data[idx]["title"] + " - " + managa_data[idx]["url"])

    # only append if we have matches
    if count_matched > 0:
        managa_data_out.append(manga_temp)


# finally write to file the result
with open(file_out, 'w') as outfile:
    outfile.write(json.dumps(managa_data_out, indent=4))





