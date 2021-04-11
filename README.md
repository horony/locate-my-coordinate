# locate-my-coordinate
Python scripts to locate and categorize geojson files. I used these to visualize/analyze movement patterns a tracked through my own mobile phone.

# locate_coordinate_region.py
Takes a list of geojson files, locates their coordinates (using shapefiles of the European Union) and aggregates this data. I use this script in which country or city I spend the most days in 2020. 

# paint_coordinate_to_map.py
Takes a list of geojson files and generates a HTML map visualizing all coordinates (e.g. in a heatmap) utilizing the folium package.
