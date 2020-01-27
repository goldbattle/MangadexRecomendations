# Import libraries
import time
import json


# script parameters
file_in = "mangas_matched.json"
file_out = "mangas_compressed.json"


# the main json object we have
with open(file_in) as json_file:
    managa_data = json.load(json_file)

# cleaned data file with no dups
managa_data_out = {}
managa_data_out["result"] = []

# loop through each index page, and extract the mangas
t0 = time.time()
for ct1, manga1 in enumerate(managa_data):

    # create the cleaned manga
    manga_temp = {}
    manga_temp["id"] = manga1["id"]
    manga_temp["title"] = manga1["title"]
    manga_temp["matches"] = []
    for match in manga1["matches"]:
        manga_temp["matches"].append({"id": match["id"], "title": match["title"], "score": match["score"]})

    # Append to the clean data out vector if not added
    managa_data_out["result"].append(manga_temp)


# finally write to file the result
with open(file_out, 'w') as outfile:
    outfile.write(json.dumps(managa_data_out))

# nice final debug print that we finished
t1 = time.time()
print("it took " + str(round(t1 - t0, 2)) + " seconds")



