from tcx2gpx import TCX2GPX
import glob
import shutil
import utils

folder='exported_data/activities/'
filenames = glob.glob(folder + '*.tcx')

outfolder=folder[:-1] + '_gpx/'
utils.mkdir_if_needed(outfolder)

# Convert all tcx files to gpx
# Note that the activity type may not be correct - in my case, using a Samsung
# watch, all TCX files have activity type "running"
# Current workaround is to use the activities.csv summary file to get activity
# type for TCX files.

for f in filenames:
  gps_object = TCX2GPX(tcx_path=f)
  gps_object.convert()
  f_converted = f[:-3] + 'gpx'
  print("Copying " + f_converted)
  shutil.copy2(f_converted, outfolder)
