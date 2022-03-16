import gpxpy
import gpxpy.gpx

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob
import sys

from natsort import natsorted
import utils

# Usage:
# python3 plot_animation.py [frameStart] [frameSkip] [zoomIn] [dateStart]
# Plots all frames for an animation of cumulative activities in chronological order
# Always includes activities starting from the earliest, UNLESS dateStart is
# specified (or hardcoded in). dateStart is the starting date for the animation, and
# can be written in the format 'yyyy-mm-dd' (or any format that pd.Timestamp
# recognizes)
# frameStart lets you start plotting a later frame (but again, that frame will include
# all activities from the beginning (or dateStart) through that one, frameStart)
# frameStart=-1 skips to the final frame, if you just want to see your final
# heat map
# frameSkip is the frequency with which frames of the animation are saved
# relative to the number of activities.
# Default frameSkip of 10 means one frame per 10 activities
# zoomIn = 1 or 0 (default 0), slightly tighter frame

# To adapt this to your location, add or replace a location in utils.py and
# specify the latitude and longitude for your map to center on as well as the
# width of your map

# Downloaded Strava data with https://support.strava.com/hc/en-us/articles/216918437-Exporting-your-Data-and-Bulk-Export

# Used https://pypi.org/project/fit2gpx/ to convert .fit.gz files from Garmin
# into gpx files

# tcx files from a Samsung watch took a bit more effort to convert to gpx - see
# the Github readme

# Followed
# https://towardsdatascience.com/data-science-for-cycling-how-to-read-gpx-strava-routes-with-python-e45714d5da23
# to load data

# Update this (here and in utils.py) to adapt to other locations
location=2
# 1: Cambridge
# 2: Somerville
# 3: Adirondacks

frameStart=0
frameSkip=1
args = sys.argv
if len(args) > 1:
  frameStart = int(args[1])
if len(args) > 2:
  frameSkip = int(args[2])

zoomIn=0
if len(args) > 3:
  zoomIn = int(args[3])

dateStart=None
#dateStart='2022-01-01'
#dateStart='2021-07-11'
if len(args) > 4:
  dateStart = args[4]
if dateStart is not None:
  dateStart_timestamp = pd.Timestamp(dateStart)

debug=0 # Only analyze 1/10 of the files in debug mode
diff_threshold=0.005 # threshold difference between lat or long for 2 consecutive points in activity
# Further points are probably errant and look bad on map

basefolder = 'exported_data/activities_gpx/'
outfolder = 'plots/'
if zoomIn:
  outfolder += 'vary_N_zoom/'
else:
  outfolder += 'vary_N/'
suf=''

df = pd.read_csv('exported_data/activities.csv', parse_dates=['Activity Date'])
activity_types_csv = df["Activity Type"]
start_time_pd = df["Activity Date"]
if dateStart is not None:
  i_dateStart = df[start_time_pd.ge(dateStart_timestamp)].index[0]
else:
  i_dateStart = 0 
print('Starting file number:', i_dateStart)
if frameStart > -1 and frameStart < i_dateStart:
  # frameStart = -1 will be set to the last frame later
  frameStart = i_dateStart
filenumber_csv = df["Activity ID"].to_numpy(dtype='int')

# Note: fit files have different numbers in their filenames, but they convert
# correctly to use the Activity ID above
# tcx files do not convert their file name to the activity ID, so get their
# numbers from the filename below

filename_csv = df["Filename"]
filenumber_csv_alt = filename_csv.str.slice(11,21) # Works for now while activity IDs are 10 digits, though the first digit got up to 7 so might need to update this
# Get subset of rows which are tcx files:
tcx_files = (filename_csv.str.slice(start=-6) == 'tcx.gz').to_numpy(dtype='bool')

filenames = np.array([basefolder + '%d' % num + '.gpx' for num in filenumber_csv])
# Need to replace filenames for tcx files:
names_to_replace = np.nonzero(tcx_files)[0]
filenames[names_to_replace] = basefolder + filenumber_csv_alt[names_to_replace] + '.gpx'

utils.mkdir_if_needed(outfolder)

# Use activities.csv to give true chronological order - fit and tcx files have
# differing numbers that make them out of order relative to gpx files
#filenames = natsorted(glob.glob(basefolder + '*.gpx'))
nFiles = len(filenames)

N = nFiles # Final frame includes all files/activities
# Allow user to skip to final frame with the input frameStart=-1
if frameStart < 0:
  frameStart = N-1

if zoomIn:
  suf += '_zoom'

# Get coordinates for plotting
latCenter, lonCenter, locName, latMin, latMax, lonMin, lonMax = utils.get_location_info(location=location, zoom=zoomIn)

# 1/skipFiles gives the fraction of files that are processed (One out of every ten
# for skipFiles=10)
skipFiles=1
if debug:
  skipFiles=10
  suf+='_skip%d' % skipFiles
  frameSkip=10

longs = []
lats = []
includePlot = []
activity_types = []

# First assemble lists of coordinates from all files to be plotted
for i in range(i_dateStart,N,skipFiles):
  # File number i corresponds to row i+2 in csv file (csv row numbering starts at 1 and
  # has a header row)
  print("Opening file %d of %d" % (i+1, N))
  gpx_filename = filenames[i]
  filenumber = gpx_filename[29:39]

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

  route_df = pd.DataFrame(route_info)
  df_diff = abs(route_df.diff()) # Difference from one point to the next
  if len(df_diff):
    max_diff_lat = max(df_diff['latitude'][1:])
    max_diff_long = max(df_diff['longitude'][1:])
    passDistThreshold=1
    if (max_diff_lat > diff_threshold) or (max_diff_long > diff_threshold):
      print("File with sequential points further than threshold apart")
      passDistThreshold=0
      # Ignore routes that have sequential points failing this threshold
    longs += [route_df['longitude']]
    lats += [route_df['latitude']]
    activity_type = track.type
    # TCX files don't get activity type right, so grab from activities csv file
    if activity_type == 'running':
      activity_type = activity_types_csv[i]
      print('i=%d, activity ID (differs from name)=%s, filename=%s, type=%s' % (i, filenumber_csv[i], gpx_filename, activity_type))
    activity_types += [activity_type] 

    # Note: can remove the check_inbounds here and just plot all routes if you
    # want to make your plot interactive and find where other routes are in
    # coordinates
    # plot_mult_routes.py is setup like this
    includePlot += [utils.check_inbounds(route_df, location=location) and passDistThreshold]

# Now plot the cumulative combinations of activities for each frame of the
# animation
for i in range(frameStart,N,frameSkip):
  Ncurrent = i
  print("Plotting files %d through %d of %d" % (i_dateStart, i+1, N))
  fig=plt.figure(figsize=(8,8))
  for j in range(i_dateStart,Ncurrent,skipFiles):
    jIndex = (j-i_dateStart) // skipFiles # In debug mode, need to divide index to match the lists created earlier
    activity_type = activity_types[jIndex]
    c='C5' # brown if not matching - don't think I have any others though
    alphaC=0.3
    if activity_type == 'Ride':
      c = 'C0' # Blue
      alphaC=0.15
    elif activity_type == 'Run':
      c = 'C3' # Red
    elif activity_type == 'Hike' or activity_type == 'Walk':
      c = 'C2' # Green

    if includePlot[jIndex]:
      plt.plot(longs[jIndex], lats[jIndex], c=c, lw=0.5, alpha=alphaC)
  plt.xlim([lonMin, lonMax])
  plt.ylim([latMin, latMax])
  ax = plt.gca()
  ax.axes.xaxis.set_visible(False)
  ax.axes.yaxis.set_visible(False) 
  suf='_N%d' % i
  plt.savefig(outfolder + 'routes_%s%s.png' % (locName, suf), format='png', dpi=300, bbox_inches='tight')
  plt.close()
