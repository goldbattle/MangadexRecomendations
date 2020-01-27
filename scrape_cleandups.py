# Import libraries
import time
import json


# script parameters
file_in = "mangas_raw.json"
file_out = "mangas_raw.json"


# the main json object we have
with open(file_in) as json_file:
    managa_data = json.load(json_file)

# cleaned data file with no dups
managa_data_out = []

# loop through each index page, and extract the mangas
t0 = time.time()
for ct1, manga1 in enumerate(managa_data):

    # check if this has already been added to our out vector
    found = False
    for ct2, manga2 in enumerate(managa_data_out):
        if manga1["id"] == manga2["id"]:
            found = True
            break

    # Append to the clean data out vector if not added
    if not found:
        managa_data_out.append(manga1)


# finally write to file the result
with open(file_out, 'w') as outfile:
    outfile.write(json.dumps(managa_data_out, indent=4))

# nice final debug print that we finished
t1 = time.time()
print("reduced " + str(len(managa_data)) + " to only " + str(len(managa_data_out)) + " mangas")
print("it took " + str(round(t1 - t0, 2)) + " seconds")



