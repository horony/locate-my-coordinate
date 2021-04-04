#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 23:18:10 2020

Script processes geojson-data and categorizes all data-points by EU NUTs regions
Result shows aggregates and counts regions by day (e.g. in 2020 3 days of region Frankfurt am Main)

"""

# import libraries
import pandas as pd
from shapely.geometry import Point
from datetime import datetime
import glob
import shapefile
from shapely.geometry import shape 

"""
import and prepare data
"""

# import all geojson-files which should be evaluated from local directory
files = glob.glob("geojson/*.geojson")

# parse imported geojson-files
list_of_lists = []

for json_file in files:
    
    list_dummy = []
    data = pd.read_json(json_file)
    num_rows = data.shape[0]
    i = 0
    
    while i < num_rows:       
        lon = data['features'][i]['geometry']['coordinates'][0] # longitude
        lat = data['features'][i]['geometry']['coordinates'][1] # latitude
        timestamp = data['features'][i]['properties']['time'] # timestamp
        timestamp =  datetime.strptime((timestamp.split('.')[0].replace('T',' ')), '%Y-%m-%d %H:%M:%S')
        list_dummy = [timestamp, lon, lat]
        list_of_lists.append(list_dummy) # append coordinates + timestamp to list of lists
        i = i + 1;

# convert parsed data to pandas dataframe
df = pd.DataFrame(columns=['load_ts','lon','lat'], data=list_of_lists)     
df = df.sort_values(by='load_ts')
coords_to_categorize = list_of_lists

# data cleaning of to exact data imported from runtastic
df.dtypes
df['load_ts_next'] = df['load_ts'].shift(-1)
df['load_dif']=(df['load_ts_next']-df['load_ts']).astype('timedelta64[s]')
df = df[df['load_dif'] > 1]
df = df.drop(['load_ts_next', 'load_dif'], axis = 1) 

# import needed EU NUTS shapefiles from local directory
# source: https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units/nuts
shp = shapefile.Reader('shapefiles/NUTS_RG_01M_2021_4326.shp')
all_shapes = shp.shapes()
all_records = shp.records()

"""
match geojson-Files with shapefiles 
"""

# define datafrane to iterate over
df = df[1:20]

# set up target dataframe
df_summary = pd.DataFrame(columns=["rec_year","rec_month","rec_day","nuts_level","country_short","nuts_name","shape_position","count"])

# start iteration
print('Iteration Start: ' + str(datetime.now()))
i = 0
for i, row in df.iterrows():
    point_to_check = [row['lon'],row['lat']]
    found_cnt = 0
    j = 0
    while j < len(all_shapes) and found_cnt < 4:
        boundary = all_shapes[j] # get a boundary polygon
        if Point(point_to_check).within(shape(boundary)): # make a point and see if it's in the polygon
           name = all_records[j][3] # get the second field of the corresponding record
           name = name.rstrip('\x00')
           level = all_records[j][1]
           ctry = all_records[j][0]
           ctry = ctry.rstrip('\x00')
           shapeposition = j
           
           ts = row['load_ts']
           year = ts.year
           month = ts.month
           day = ts.date()

           df_summary = df_summary.append({
             "rec_year": year,
             "rec_month": month,
             "rec_day": day,
             "nuts_level": level,
             "country_short": ctry,
             "nuts_name": name,
             "shape_position": shapeposition,
             "count": 1
              }, ignore_index=True)
           
           found_cnt = found_cnt + 1
           
        j = j+1
        
print('Iteration Ende: ' + str(datetime.now()))

df_summary = df_summary.drop_duplicates()
df_aggregate = df_summary.groupby(['rec_year','nuts_level','country_short','nuts_name'])['count'].sum()

"""
results output
"""
print(df_aggregate)