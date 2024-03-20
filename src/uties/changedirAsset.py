#-*- coding utf-8 -*-
import ee
import gee 
import sys
import json
from tqdm import tqdm
import random
from datetime import date
import pandas as pd
import collections
collections.Callable = collections.abc.Callable

try:
    ee.Initialize()
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

def gerenciador(conta):    
    #0, 18, 36, 54]
    #=====================================#
    # gerenciador de contas para controlar# 
    # processos task no gee               #
    #=====================================#
    print("activando conta de >> {} <<".format(conta))        
    gee.switch_user(conta)
    gee.init()        
    gee.tasks(n= 2, return_list= True)       



# ee.data.renameAsset(sourceId, destinationId, callback)
asset_output = 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/mosaics-harmonicoCaat'
asset_input = 'projects/mapbiomas-arida/mosaic_harmonic'
changeConta = False

if changeConta: 
    gerenciador('solkan1201')

imgCol = ee.ImageCollection(asset_input)
lstIds = imgCol.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list').getInfo()

for cc, masset in enumerate(lstIds):
    print(cc, ' => move ', masset, " to ImageCollection in NEXGENTMAP")
    sourceId = asset_input + '/' + masset
    destinationId = asset_output + '/' + masset
    # moving file from repository Arida to Nextgenmap
    ee.data.renameAsset(sourceId, destinationId)


print('========================================')
print("            finish process              ")