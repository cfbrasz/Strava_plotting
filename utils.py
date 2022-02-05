import os
import pandas as pd
import numpy as np

def mkdir_if_needed(f):    
  if not os.path.exists(f):
    os.makedirs(f)

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


