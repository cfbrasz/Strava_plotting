import gpxpy
import gpxpy.gpx

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob
import sys

import utils

# Usage:
# python3 plot_mult_routes.py [N] [Nstart] [zoomIn]
# N is the upper limit of the activity number to include
# N=-1 includes all activites (and is the default value)
# Start from Nstart (default 0) and include activities through N
# zoomIn = 1 or 0 (default 0), slightly tighter frame

# Downloaded Strava data with https://support.strava.com/hc/en-us/articles/216918437-Exporting-your-Data-and-Bulk-Export

# Used https://pypi.org/project/fit2gpx/ to convert .fit.gz files from Garmin
# into gpx files

# Followed
# https://towardsdatascience.com/data-science-for-cycling-how-to-read-gpx-strava-routes-with-python-e45714d5da23
# to load data

N=-1
Nstart=0
suf=''

args = sys.argv
if len(args) > 1:
  N = int(args[1])
  suf+='_N%d' % N

if len(args) > 2:
  Nstart = int(args[2])
  suf+='_Nstart%d' % Nstart

zoomIn=0
if len(args) > 3:
  zoomIn = int(args[3])

debug=1 # Only analyze 1/10 of the files in debug mode
checkBadFiles=0 # Plot the activities that fail the diff_threshold requirement (they should have long unphysical line segments)
diff_threshold=0.005 # threshold difference between lat or long for 2 points
# Further points are probably errant
if checkBadFiles:
  suf += '_highDiffs'

basefolder = 'exported_data/activities_gpx/'
outfolder = 'plots/'
utils.mkdir_if_needed(outfolder)

filenames = glob.glob(basefolder + '*.gpx')
nFiles = len(filenames)

if N < 0 or N > nFiles:
  N = nFiles

plt.figure(figsize=(8,8))

if zoomIn:
  suf += '_zoom'

location=3
# 1: Cambridge
# 2: Somerville
# 3: Adirondacks

# Get coordinates for plotting
latCenter, lonCenter, locName, latMin, latMax, lonMin, lonMax = utils.get_location_info(location=location, zoom=zoomIn)


skipFiles=1 # skipFiles=1: plot every file
# skipFiles = 10: plot every 10th file
if debug:
  skipFiles=10
  suf+='_skip%d' % skipFiles

for i in range(Nstart,N,skipFiles):
  print("Opening file %d of %d" % (i+1, N))
  gpx_filename = filenames[i]

  with open(gpx_filename, 'r') as gpx_file:
    gpx = gpxpy.parse(gpx_file)

  pts = gpx.tracks[0].segments[0].points

  route_info = []

  for track in gpx.tracks:
    for segment in track.segments:
      for point in segment.points:
        route_info.append({
          'latitude': point.latitude,
          'longitude': point.longitude,
          'elevation': point.elevation,
          'time': point.time
        }) 

  activity_type = track.type
  c='C5' # brown if not matching - don't think I have any others though
  alphaC=0.3
  if activity_type == 'running':
    # Not giving correct solution here to keep code simple. See plot_animation
    # for true solution to this problem with tcx files. (Can get same
    # functionality as this script by choosing frameStart=-1 to generate final
    # heat map)
    activity_type = 'Ride'

  if activity_type == 'Ride':
    c = 'C0' # Blue
    alphaC=0.15
  elif activity_type == 'Run':
    c = 'C3' # Red
  elif activity_type == 'Hike' or activity_type == 'Walk':
    c = 'C2' # Green

  route_df = pd.DataFrame(route_info)
  df_diff = abs(route_df.diff()) # Difference from one point to the next
  if len(df_diff):
    max_diff_lat = max(df_diff['latitude'][1:])
    max_diff_long = max(df_diff['longitude'][1:])
    includePlot=1
    if checkBadFiles:
      includePlot=0
    if (max_diff_lat > diff_threshold) or (max_diff_long > diff_threshold):
      print("File with sequential points further than threshold apart")
      print(gpx_filename)
      print(max_diff_lat, max_diff_long)
      if checkBadFiles:
        includePlot=1 # Only plot the activities that fail threshold with checkBadFiles = 1
      else:
        includePlot=0


    # Don't really need to check if inbounds, and it doesn't seem to save time
    # anyway
    #if utils.check_inbounds(route_df, location=location):
    if 1:
      if includePlot:
        plt.plot(route_df['longitude'], route_df['latitude'], c=c, lw=0.5, alpha=alphaC)
    else:
      print("File out of bounds")

plt.xlim([lonMin, lonMax])
plt.ylim([latMin, latMax])
ax = plt.gca()
if 0: # Set to 1 to generate interactive plot instead of saving. (Can use this to find your routes)
  plt.show()
else:
  ax.axes.xaxis.set_visible(False)
  ax.axes.yaxis.set_visible(False) 
  plt.savefig(outfolder + 'routes_%s%s.png' % (locName, suf), format='png', dpi=300, bbox_inches='tight')
