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

# loop through each index page, and extract the mangas
t0 = time.time()
for ct1, manga1 in enumerate(managa_data):

    # create the cleaned manga
    manga_temp = {}
    manga_temp["m_ids"] = []
    manga_temp["m_titles"] = []
    manga_temp["scores"] = []
    for match in manga1["matches"]:
        manga_temp["m_ids"].append(match["id"])
        manga_temp["m_titles"].append(match["title"])
        manga_temp["scores"].append(round(match["score"], 3))

    # Append to the clean data out vector if not added
    managa_data_out[manga1["id"]] = manga_temp


# finally write to file the result
with open(file_out, 'w') as outfile:
    outfile.write(json.dumps(managa_data_out))

# nice final debug print that we finished
t1 = time.time()
print("it took " + str(round(t1 - t0, 2)) + " seconds")



