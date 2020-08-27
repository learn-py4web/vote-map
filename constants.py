# Used in maps edit mode.
MAX_MAP_RESULTS = 25
MAX_VIEW_RESULTS = 25
ENOUGH_RESULTS = 1 # Don't search beyond a good radius

# Square size
SQSIZE = 0.1 # degrees

DMAX = 0.5 # Maximum size of area inspected to be able to edit.
DGOOD = 0.2

# Reads zip code database.
import json
import os
APP_FOLDER = os.path.dirname(__file__)
ZIP_FILE = os.path.join(APP_FOLDER, "data", "zips.json")
with open(ZIP_FILE, "r") as f:
    ZIPCODE_LOCATIONS = json.load(f)
