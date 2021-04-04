#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 21:34:38 2020

Script processes geojson-data and utilizes folium to paint the coordinates on a html-map
"""

# import libraries
import folium
from folium.plugins import TimestampedGeoJson
import pandas as pd
import os
import glob

"""
import and prepare data
"""

# import all geojson-files which should be evaluated from local directory
files = glob.glob("geojson/*.geojson")
list_of_lists = []

# parse imported geojson-files
for json_file in files:
    
    list_dummy = []
    data = pd.read_json(json_file)
    num_rows = data.shape[0]
    i = 0
    
    while i < num_rows:
        
        lon = data['features'][i]['geometry']['coordinates'][0]
        lat = data['features'][i]['geometry']['coordinates'][1]
        timestamp = data['features'][i]['properties']['time']
        print(timestamp)
        list_dummy = [timestamp, lon, lat]
        list_of_lists.append(list_dummy)
        i = i + 1;

# convert parsed data to pandas dataframe   
df = pd.DataFrame(list_of_lists)
df.columns = ['timestamp', 'lon', 'lat']

df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values(by='timestamp', ascending=True)

def create_geojson_features(df):
    print('> Creating GeoJSON features...')
    new_features = []
    for _, row in df.iterrows():
        feature = {
            'type': 'Feature',
            'geometry': {
                'type':'Point', 
                'coordinates':[row['lon'],row['lat']]
            },
            'properties': {
                'time': row['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
                'style': {'color' : 'red'},
                'icon': 'circle',
                'iconstyle':{
                    #'fillColor': 'red',
                    'opacity': 0.2 ,
                    #'fillOpacity': 0.5,
                    'stroke': 'false',
                    'radius': 1
                }
            }
        }
        new_features.append(feature)
    return new_features

# initialize map 
map_center = [50.1109221, 8.6821267] # frankfurt
created_map = folium.Map(location=map_center, zoom_start=12, tiles='cartodbdark_matter')

features = create_geojson_features(df)

TimestampedGeoJson(
        {'type': 'FeatureCollection', 'features': features}
        , period='PT1H'
        , add_last_point=True
        , auto_play=True
        , loop=True
        , max_speed=1
        , loop_button=True
        , duration=None # P1M
        , time_slider_drag_update=True
    ).add_to(created_map)

# Define target directory and safe html map
os.chdir("/home/lennart/Schreibtisch/python_scripts/maps/")
created_map.save("mymap.html")