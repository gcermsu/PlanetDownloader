'''
Script to list Planets images that interesects an AOI in a given date range.
'''

import json
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
from shapely.geometry import Polygon
import geopandas as gpd

# Define filters to search for Planet images
def planet_filter(geometry, start_date, end_date, cloud_cover):

    geometry_filter = {
    "type": "GeometryFilter",
    "field_name": "geometry",
    "config": geometry
    }

    date_range_filter = {
    "type": "DateRangeFilter",
    "field_name": "acquired",
    "config": {
        "gte": start_date,
        "lte": end_date
    }}

    cloud_cover_filter = {
    "type": "RangeFilter",
    "field_name": "cloud_cover",
    "config": {
        "lte": cloud_cover
    }}

    # combine our geo, date, cloud filters
    combined_filter = {
    "type": "AndFilter",
    "config": [geometry_filter, date_range_filter, cloud_cover_filter]
    }

    return combined_filter

def load_planet_images(API_KEY, combined_filter, item_type="PSScene"):

    search_request = {
    "item_types": [item_type],
    "filter": combined_filter
    }

    search_result = \
    requests.post(
        'https://api.planet.com/data/v1/quick-search',
        auth=HTTPBasicAuth(API_KEY, ''),
        json=search_request)

    geojson = search_result.json()

    return geojson

def planet_images(area_of_interest, start_date, end_date, cloud_cover, area_coverage, api_key, msi_tile):

    # load information about the area of interest
    polygon_roi = Polygon(area_of_interest['coordinates'][0])
    gdf_roi = gpd.GeoDataFrame(index=[0], crs="EPSG:3857", geometry=[polygon_roi])
    roi_area = gdf_roi.geometry.area.sum()

    # Define the filters for the search
    combined_filter = planet_filter(area_of_interest, start_date + 'T00:00:00.000Z', end_date + 'T00:00:00.000Z', cloud_cover)
    planet_assets = load_planet_images(api_key, combined_filter)

    # Load image dates
    dates = [feature['properties']['acquired'] for feature in planet_assets['features']]
    dates = [date.split('T')[0] for date in dates]

    for i in range(len(planet_assets['features'])):
        planet_assets['features'][i]['properties']['acquired'] = dates[i]

    # Group the images by the date
    grouped_images = {}

    for i in range(len(planet_assets['features'])):
        date = planet_assets['features'][i]['properties']['acquired']
        if date not in grouped_images:
            grouped_images[date + '_' + msi_tile] = [planet_assets['features'][i]]
        else:
            grouped_images[date + '_' + msi_tile].append(planet_assets['features'][i])

    filtered_dates = {}

    for i in grouped_images:

        # Access the images of the same date
        assets_dates = grouped_images[i]

        # For each image, calculate the intersection area with the ROI
        gdf_list = []

        for j in range(len(grouped_images[i])):
            img_polygon = Polygon(assets_dates[j]['geometry']['coordinates'][0])
            gdf = gpd.GeoDataFrame(index=[j], crs="EPSG:3857", geometry=[img_polygon])
            gdf_list.append(gdf)

        merged_polygon = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True)).to_crs("EPSG:3857")
        single_polygon = gpd.GeoDataFrame(index=[0], crs="EPSG:3857", geometry=[merged_polygon.union_all()])

        intersection = gpd.overlay(gdf_roi, single_polygon, how='intersection')
        area_int = intersection.geometry.area.sum()

        percentage_intersection = (area_int / roi_area) * 100

        if percentage_intersection > area_coverage:
            filtered_dates[i] = grouped_images[i]

    return filtered_dates, grouped_images