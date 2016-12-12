import os
import folium
import pandas as pd

print(folium.__version__)

import numpy as np

def map_locations(lons, lats, names, stars):

    locations = list(zip(lats, lons))
    popups = ['{}, Rating = {}'.format(name, stars) for name, stars in zip(names, stars)]

    from folium.plugins import MarkerCluster

    m = folium.Map(location=[np.mean(lats), np.mean(lons)],
                      tiles='Cartodb Positron', zoom_start=1)

    m.add_child(MarkerCluster(locations=locations, popups=popups))

    m.save('1000_MarkerCluster.html')

def locations():
    df = pd.read_csv('D:/Projects/Yelp/dataset/business.csv',  low_memory=False)
    df2 = df[['latitude', 'longitude', 'name', 'stars']]
    lons = df2.tail(20).longitude.tolist()
    lats = df2.tail(20).latitude.tolist()
    names = df2.tail(20).name.tolist()
    stars = df2.tail(20).stars.tolist()
    map_locations(lons, lats, names, stars)
    # for index, row in df2.iterrows():
    #     print row['latitude'], row['longitude']
    # print df2.head(10).to_string()
    # df

locations()
