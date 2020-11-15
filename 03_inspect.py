# Import libraries
import time
import json
import os
import string
import operator
import gzip

# import our specific functions
from functions import manga_utils
from functions import manga_compator
from functions import manga_obj

# files in and out and settings
dir_inout = "output_test/"
file_in = "output_test/mangas_compressed.json"
file_out = "temp.json"

# Open the manga json file and load
manga_data = manga_utils.read_raw_manga_data_files(dir_inout)
print("loaded " + str(len(manga_data)) + " mangas")

# manga_data = []
# print("opening " + file_in)
# with open(file_in) as json_file:
#     manga_data_json = json.load(json_file)
# for manga_json in manga_data_json:
#     manga_data.append(manga_obj.MangaObj(manga_json))


# loop through and find a specific manga
ids_to_find = [42681, 51414]
# ids_to_find = [51414]
out_data = []
for idx, manga in enumerate(manga_data):
    if manga.id in ids_to_find:
        print("found manga %d, saving.." % manga.id)
        out_data.append(manga.__dict__)


# finally output into a temp tile
with open(file_out, 'w') as outfile:
    json.dump(out_data, outfile, indent=2, sort_keys=False)


# Finally get the compressed representation
dir_inout = "output_temp/"
# create output direction if not exists
if not os.path.exists(os.path.dirname(dir_inout)):
    os.makedirs(os.path.dirname(dir_inout))
dict_compressed = manga_utils.get_compressed_representation_string(manga_data)
with open(dir_inout + "mangas_compressed.json", 'w') as outfile:
    json.dump(dict_compressed, outfile, sort_keys=False)
print("outputted to " + dir_inout + "mangas_compressed.json")