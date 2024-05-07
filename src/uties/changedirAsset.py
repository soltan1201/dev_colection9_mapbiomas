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

def sendFilenewAsset(idSource, idTarget):
    # moving file from repository Arida to Nextgenmap
    ee.data.renameAsset(idSource, idTarget)

listaNameBacias = [
    '741','7421','7422','744','745','746','7492','751','752','753',
    '754','755','756','757','758','759','7621','7622','763','764',
    '765','766','767','771', '772','773','7741','776','7742','775',
    '777','778','76111','76116','7612','7613','7614','7615','7616',
    '7617','7618','7619'
]

# ee.data.renameAsset(sourceId, destinationId, callback)
asset_output = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Gap-fill'
asset_input = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Gap-fills'
changeConta = False
fromImgCol = False
if changeConta: 
    gerenciador('solkan1201')
if fromImgCol:
    imgCol = ee.ImageCollection(asset_input)
    lstIds = imgCol.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list').getInfo()

    for cc, masset in enumerate(lstIds):
        print(cc, ' => move ', masset, " to ImageCollection in NEXGENTMAP")
        sendFilenewAsset(asset_input + '/' + masset, asset_output + '/' + masset)

else:
    lstFails = []
    for cc, nbacia in enumerate(listaNameBacias):
        # filterGF_BACIA_741_V5
        nameImage = 'filterGF_BACIA_' + nbacia + '_V5'
        print(cc, ' => move ', nameImage, " to ImageCollection in NEXGENTMAP")        
        try:
            # imgtmp = ee.Image(asset_input + '/' + nameImage)
            # print(" list name bands ", imgtmp.bandNames().getInfo())
            sendFilenewAsset(asset_input + '/' + nameImage, asset_output + '/' + nameImage)
        except:
            lstFails.append(nbacia)

    if len(lstFails):
        print(f" we added the basin {len(lstFails)} to list fails ")
        print(lstFails)
    else:
        print(" ----- We don´t have basin in list fails --------")

print('========================================')
print("            finish process              ")