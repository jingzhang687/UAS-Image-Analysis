# -*- coding: utf-8 -*-
"""
Created on Fri Aug 2 10:00:00 2019
Edited on Wed Oct 16 2024
@author: Jing Zhang

Objective: Crop individual plot from UAS Geotiff

Goals: 1) Read the GeoTiff raster
       2) Crop the images based on the grid and output them as GeoTiff with updated metadata 
       3) Convert the cropped GeoTiff images to JPEG and save their crs and transform information 
          in another file for future use
"""
######################################################
import os
import rasterio as rio

'''
Set up working directory, where the Crop GeoTiff will be stored
'''
wd = 'C:\\Research-Data-2024\\Strawberry\\Plot-size-RGB-UAS\\20240529' 
os.chdir(wd)
os.getcwd()
'''
Return a list of files under the working directory
& Pass the GeoTiff filename to filename
'''
GT_fname = 'C:\\Data-share-Rob-2024\\CC24_Strawberry\\UAV\\05292024\\metashape_ortho.tif'

'''
Read some important information from the GeoTiff
'''
raster = rio.open(GT_fname)
raster.profile

'''
Load more packages 
'''
from rasterio.plot import show
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np

poly_fname='W:/Strawberry-HTP-files-in-working/SHP/Field-plots.shp'

"""
Crop the rasters based on polygon
"""
from shapely.geometry import mapping
poly = gpd.read_file(poly_fname)

extent_geojson_list = []
for i in range(len(poly)):
    extent_geojson = mapping(poly['geometry'][i])
    extent_geojson_list.append (extent_geojson)

raster_crop_list = []
raster_crop_affine_list = []
from rasterio.mask import mask
for i in range(len(extent_geojson_list)):
    raster_crop, raster_crop_affine = mask(raster,
                                        [extent_geojson_list[i]],
                                        crop=True)
    raster_crop_list.append(raster_crop)
    raster_crop_affine_list.append(raster_crop_affine)
raster_crop_meta = raster.meta.copy() # make a copy of the metadata from the original file

"""
Output GeoTiff
"""

for i in range(len(raster_crop_list)):
    raster_crop_meta.update({"driver": "GTiff",
                 "height": raster_crop_list[i].shape[1],
                 "width": raster_crop_list[i].shape[2],
                 "transform": raster_crop_affine_list[i]})
    with rio.open("Strawberry-20240529_"+str(i+1)+".tif", "w", **raster_crop_meta) as dest:
        dest.write(raster_crop_list[i])
##### Close file connection
raster.close()

"""
Output JPEG - GPS information was stored in raster_crop_affine_list
"""
lists = os.listdir()
from osgeo import gdal
options_list = [
    '-ot Byte',
    '-b 1',
    '-b 2',
    '-b 3',
    '-mask 4',
    '-of JPEG',
    '-scale min_val max_val'
    #'-scale'     # adjust the contrast
    #'-scale'  # keep the original color tone
]
options_string = " ".join(options_list)
for i in range(len(lists)):
    gdal.Translate("Strawberry-20240529_"+(str(lists[i]).split('.')[0]).split('_')[-1]+".jpeg", 
    lists[i], 
    options=options_string)

