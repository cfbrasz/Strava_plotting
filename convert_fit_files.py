# Copied from https://pypi.org/project/fit2gpx/ 

from fit2gpx import StravaConverter

DIR_STRAVA = 'exported_data'

# Step 1: Create StravaConverter object 
# - Note: the dir_in must be the path to the central unzipped Strava bulk export folder 
# - Note: You can specify the dir_out if you wish. By default it is set to 'activities_gpx', which will be created in main Strava folder specified.

strava_conv = StravaConverter(
    dir_in=DIR_STRAVA
)

# Step 2: Unzip the zipped files
strava_conv.unzip_activities()

# Step 3: Add metadata to existing GPX files
strava_conv.add_metadata_to_gpx()

# Step 4: Convert FIT to GPX
strava_conv.strava_fit_to_gpx()
