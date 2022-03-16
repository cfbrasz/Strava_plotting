import os
import pandas as pd
import numpy as np

def get_location_info(location=1, zoom=0):
  "Return latitude and longitude to center maps on, location name, and map width to use"
  if location == 1: # Centered on Cambridge
    latCenter=42.38
    lonCenter=-71.10
    locName = 'boston'
    latWid = 0.18
    if zoom:
      latWid = 0.1
  if location == 2: # Centered on Somerville
    latCenter=42.395
    lonCenter=-71.10
    locName = 'somerville'
    latWid = 0.18
    if zoom:
      latWid = 0.1
  if location == 3: # Adirondacks
    latCenter=44.3
    lonCenter=-74.3
    locName = 'ADK'
    latWid = 0.7

  latMin = latCenter - latWid/2
  latMax = latCenter + latWid/2

  longScale = np.cos(latCenter*np.pi/180)
  # 1 degree of longitude is shorter than 1 degree of latitude by scale factor cos(latitude
  #   angle)

  # Make bounds for longitude longer by 1/scale factor so that total distance in
  # longitudinal direction equals total distance in latitude
  lonWid = latWid/longScale
  lonMin = lonCenter - lonWid/2
  lonMax = lonCenter + lonWid/2

 
  return latCenter, lonCenter, locName, latMin, latMax, lonMin, lonMax


def mkdir_if_needed(f):    
  if not os.path.exists(f):
    os.makedirs(f)

def check_inbounds(route_df, threshold_angle_diff=1, location=1):
  "Check whether first point of path is within threshold_angle_diff degrees latitude and longitude from target point for specified location to decide whether to plot it."
  lat1 = route_df['latitude'][0]
  lon1 = route_df['longitude'][0]

  latTarget, lonTarget, _, _,_,_,_ = get_location_info(location)

  return (abs(lat1 - latTarget) < threshold_angle_diff) and (abs(lon1 - lonTarget) < threshold_angle_diff)


