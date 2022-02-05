import gpxpy
import gpxpy.gpx

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import utils

# Plot single route of gps data

basefolder = 'exported_data/activities_gpx/'
#basefolder = 'exported_data/activities/'

# Specify file number to be plotted
filenum = 1101776812

outfolder = 'plots/'
utils.mkdir_if_needed(outfolder)

gpx_filename = basefolder + str(filenum) + '.gpx'

with open(gpx_filename, 'r') as gpx_file:
  gpx = gpxpy.parse(gpx_file)

#print(len(gpx.tracks))

pts = gpx.tracks[0].segments[0].points
#print(pts[-1])

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

#print(route_info[:3])

route_df = pd.DataFrame(route_info)

plt.figure(figsize=(8,8))
plt.gca().set_aspect('equal')
# See plot_mult_routes and plot_animation: shouldn't use equal aspect ratio
# here, longitude and latitude are not equivalent distances so map will be
# short and fat

plt.plot(route_df['longitude'], route_df['latitude'])

plt.savefig(outfolder + 'route_%d.png' % filenum, format='png', dpi=300, bbox_inches='tight')


