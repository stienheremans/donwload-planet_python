# -*- coding: utf-8 -*-

from openpyxl import Workbook, load_workbook
import pandas as pd
import json
from osgeo import ogr
import geopandas as gpd
import geojson
import os
import requests
from requests.auth import HTTPBasicAuth
import time
import pathlib
import numpy as np


## set up requests to work with api
PLANET_API_KEY = 'c7e872b7d5054e3e839d74ef1b241655'

orders_url = 'https://api.planet.com/compute/ops/orders/v2'

auth = HTTPBasicAuth(PLANET_API_KEY, '')
headers = {'content-type': 'application/json'}


# define helpful functions for submitting, polling, and downloading an order
def place_order(request, auth):
    response = requests.post(orders_url, data=json.dumps(request), auth=auth, headers=headers)
    print(response)
    
    if not response.ok:
        raise Exception(response.content)

    order_id = response.json()['id']
    print(order_id)
    order_url = orders_url + '/' + order_id
    return order_url

def poll_for_success(order_url, auth, num_loops=50):
    count = 0
    while(count < num_loops):
        count += 1
        r = requests.get(order_url, auth=auth)
        response = r.json()
        state = response['state']
        print(state)
        success_states = ['success', 'partial']
        if state == 'failed':
            raise Exception(response)
        elif state in success_states:
            break
        
        time.sleep(10)
        
def download_order(order_url, auth, overwrite=False):
    r = requests.get(order_url, auth=auth)
    print(r)

    response = r.json()
    results = response['_links']['results']
    results_urls = [r['location'] for r in results]
    results_names = [r['name'] for r in results]
    results_paths = [pathlib.Path(os.path.join('data', n)) for n in results_names]
    print('{} items to download'.format(len(results_urls)))
    
    for url, name, path in zip(results_urls, results_names, results_paths):
        if overwrite or not path.exists():
            print('downloading {} to {}'.format(name, path))
            r = requests.get(url, allow_redirects=True)
            path.parent.mkdir(parents=True, exist_ok=True)
            open(path, 'wb').write(r.content)
        else:
            print('{} already exists, skipping {}'.format(path, name))
            
    return dict(zip(results_names, results_paths))


 # make GeoJSON from shapefile
driver = ogr.GetDriverByName('ESRI Shapefile')
shp_path = "F:/Postdoc 2020-2024/Projects/Graslandonderzoek/1. Inputs/Study sites bboxes/Turnhout_bbox.shp"
file = gpd.read_file(shp_path)
file.to_file("F:/Postdoc 2020-2024/Projects/Graslandonderzoek/2. Methodology/Part 1 - Creating time series/C - Planet data/GeoJSON/Turnhout_gras.json", driver="GeoJSON")

with open("F:/Postdoc 2020-2024/Projects/Graslandonderzoek/2. Methodology/Part 1 - Creating time series/C - Planet data/GeoJSON/Turnhout_gras.json") as f:
    gj = geojson.load(f)
features = gj['features'][0]
  
geometry = {
        "type": "Polygon",
        "coordinates": [
        [
                []
                
        ]
    ]
}
# replace coordinates in the empty json file created above by the actual coordinates from the geojson file
geometry["coordinates"] = features.geometry.coordinates
print(geometry)

# define the clip tool
clip = {
    "clip": {
        "aoi": geometry
    }
}
    

# Open the excel sheets with the selected images for download
filename  ="F:/Postdoc 2020-2024/Projects/Graslandonderzoek/2. Methodology/Part 1 - Creating time series/C - Planet data/Image lists/Planet_imgs_Turnhout_2018.xlsx"
wb = load_workbook(filename)

# Extract values from this sheet
data = wb['imgs_min_deviat'].values

# Get the first line in file as a header line
columns = next(data)[0:]

# Create a DataFrame based on the second and subsequent lines of data
sel_imgs = pd.DataFrame(data, columns=columns)
sel_imgs = sel_imgs.iloc[1:]

# Loop over images and download
for i in range(4,5):
    # define products part of order
    single_product = [
            {
                    "item_ids": [sel_imgs['im_id'][i]],
                    "item_type": "PSScene4Band",
                    "product_bundle": "analytic"
                    }
            ]  
    request_clip = {
            "name": "just clip",
            "products": single_product,
            "tools": [clip]
            }
    request_clip
    # create an order request with the clipping tool
    clip_order_url = place_order(request_clip, auth)
    poll_for_success(clip_order_url, auth)
    downloaded_files = download_order(clip_order_url, auth)
              



