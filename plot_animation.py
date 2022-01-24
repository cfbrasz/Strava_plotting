import gpxpy
import gpxpy.gpx

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob
import sys

# Usage:
# python3 plot_animation.py [Nstart] [frameSkip] [zoomIn]
# Plots all frames for an animation of cumulative activities in chronological order
# Always includes activities starting from the earliest
# Nstart lets you start with a later frame (but again, that frame will include
# all activities from the first one up through that one, Nstart)
# frameSkip is the frequency with which frames of the animation are saved
# relative to the number of activities.
# Default frameSkip of 10 means one frame per 10 activities
# zoomIn = 1 or 0 (default 0), slightly tighter frame

# Downloaded Strava data with https://support.strava.com/hc/en-us/articles/216918437-Exporting-your-Data-and-Bulk-Export

# Used https://pypi.org/project/fit2gpx/ to convert .fit.gz files from Garmin
# into gpx files

# Followed
# https://towardsdatascience.com/data-science-for-cycling-how-to-read-gpx-strava-routes-with-python-e45714d5da23
# to load data

Nstart=0
#Nstart=1200
frameSkip=1
args = sys.argv
if len(args) > 1:
  Nstart = int(args[1])
if len(args) > 2:
  frameSkip = int(args[2])

zoomIn=0
if len(args) > 3:
  zoomIn = int(args[3])

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

filenames = glob.glob(basefolder + '*.gpx')
nFiles = len(filenames)

N = nFiles # Final frame includes all files/activities

location=1

# Bounds for Cambridge plot
latWid = 0.2
latWid = 0.18
if zoomIn:
  latWid = 0.1
  suf += '_zoom'
latCenter = 42.38
latMin = latCenter - latWid/2
latMax = latCenter + latWid/2
lonCenter = -71.1
locName = 'boston'

longScale = np.cos(latCenter*np.pi/180)
# 1 degree of longitude is shorter than 1 degree of latitude by scale factor cos(latitude
#   angle)

# Make bounds for longitude longer by 1/scale factor so that total distance in
# longitudinal direction equals total distance in latitude
longWid = latWid/longScale
lonMin = lonCenter - longWid/2
lonMax = lonCenter + longWid/2

def check_inbounds(route_df, threshold_angle_diff=1, location=1):
  "Check whether first point of path is within threshold_angle_diff degrees latitude and longitude from target point for specified location to decide whether to plot it."
  lat1 = route_df['latitude'][0]
  lon1 = route_df['longitude'][0]

  if location == 1: # Centered on Cambridge
    latTarget=42.36
    lonTarget=-71.10
  if location == 2: # Adirondacks
    latTarget=44.3
    lonTarget=-74.3

  return (abs(lat1 - latTarget) < threshold_angle_diff) and (abs(lon1 - lonTarget) < threshold_angle_diff)

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
for i in range(0,N,skipFiles):
  print("Opening file %d of %d" % (i+1, N))
  gpx_filename = filenames[i]
  #print(gpx_filename)

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
  max_diff_lat = max(df_diff['latitude'][1:])
  max_diff_long = max(df_diff['longitude'][1:])
  passDistThreshold=1
  if (max_diff_lat > diff_threshold) or (max_diff_long > diff_threshold):
    print("File with sequential points further than threshold apart")
    passDistThreshold=0
    #print(gpx_filename)
    #print(max_diff_lat, max_diff_long)
  longs += [route_df['longitude']]
  lats += [route_df['latitude']]
  activity_type = track.type
  activity_types += [activity_type] 

  includePlot += [check_inbounds(route_df, location=location) and passDistThreshold]

# Now plot the cumulative combinations of activities for each frame of the
# animation
for i in range(Nstart,N,frameSkip):
  Ncurrent = i
  print("Plotting files 1 through %d of %d" % (i+1, N))
  fig=plt.figure(figsize=(8,8))
  for j in range(0,Ncurrent,skipFiles):
    jIndex = j // skipFiles # In debug mode, need to divide index to match the lists created earlier
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
