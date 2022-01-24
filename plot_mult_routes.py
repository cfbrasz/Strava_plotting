import gpxpy
import gpxpy.gpx

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob
import sys

# Usage:
# python3 plot_mult_routes.py [N] [Nstart] [zoomIn]
# N is the number of activities to include
# N<0 includes all activites (and is the default value)
# Start from Nstart (default 0)
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

debug=0 # Only analyze 1/10 of the files in debug mode
checkBadFiles=0 # Plot the activities that fail the diff_threshold requirement (they should have long unphysical line segments)
diff_threshold=0.005 # threshold difference between lat or long for 2 points
# Further points are probably errant
if checkBadFiles:
  suf += '_highDiffs'

basefolder = 'exported_data/activities_gpx/'
outfolder = 'plots/'

filenames = glob.glob(basefolder + '*.gpx')
nFiles = len(filenames)

if N < 0 or N > nFiles:
  N = nFiles

plt.figure(figsize=(8,8))

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

if location == 2:
  # Adirondacks hikes
  latMin = 44
  latMax = 44.7
  lonMin = -75.1
  lonMax = -73.6

  locName = 'ADK'

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

skipFiles=1 # skipFiles=1: plot every file
# skipFiles = 10: plot every 10th file
if debug:
  skipFiles=10
  suf+='_skip%d' % skipFiles

for i in range(Nstart,N,skipFiles):
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

  activity_type = track.type
  c='C5' # brown if not matching - don't think I have any others though
    alphaC=0.3
    if activity_type == 'Ride':
      c = 'C0' # Blue
      alphaC=0.15
    elif activity_type == 'Run':
      c = 'C3' # Red
    elif activity_type == 'Hike' or activity_type == 'Walk':
      c = 'C2' # Green

  route_df = pd.DataFrame(route_info)
  df_diff = abs(route_df.diff()) # Difference from one point to the next
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


  if check_inbounds(route_df, location=location):
    if includePlot:
      plt.plot(route_df['longitude'], route_df['latitude'], c=c, lw=0.5, alpha=alphaC)
  else:
    print("File out of bounds")

plt.xlim([lonMin, lonMax])
plt.ylim([latMin, latMax])
ax = plt.gca()
ax.axes.xaxis.set_visible(False)
ax.axes.yaxis.set_visible(False) 
if 0: # Set to 1 to generate interactive plot instead of saving
  plt.show()
else:
  plt.savefig(outfolder + 'routes_%s%s.png' % (locName, suf), format='png', dpi=300, bbox_inches='tight')
