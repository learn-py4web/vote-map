# Used in maps edit mode.
MAX_MAP_RESULTS = 25
MAX_VIEW_RESULTS = 25

# Square size
SQSIZE = 0.1 # degrees

DMAX = 0.5 # Maximum size of area inspected to be able to edit.

# Reads zip code database.
import json
import os
APP_FOLDER = os.path.dirname(__file__)
ZIP_FILE = os.path.join(APP_FOLDER, "data", "us-zip-code-latitude-and-longitude.json")
with open(ZIP_FILE, "r") as f:
    zip_list = json.load(f)
ZIPCODE_LOCATIONS = {}
for el in zip_list:
    r = el["fields"]
    ZIPCODE_LOCATIONS[r["zip"]] = (r["latitude"], r["longitude"])
