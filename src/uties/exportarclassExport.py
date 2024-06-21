#!/usr/bin/env python2
# -*- coding: utf-8 -*-

##########################################################
## CRIPT DE EXPORTAÇÃO DO RESULTADO FINAL PARA O ASSET  ##
## DE mAPBIOMAS                                         ##
## Produzido por Geodatin - Dados e Geoinformação       ##
##  DISTRIBUIDO COM GPLv2                               ##
#########################################################

import ee 
import gee
import json
import csv
import sys
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


def gerenciador(cont, paramet):
    #0, 18, 36, 54]
    #=====================================#
    # gerenciador de contas para controlar# 
    # processos task no gee               #
    #=====================================#
    numberofChange = [kk for kk in paramet['conta'].keys()]
    
    if str(cont) in numberofChange:

        print("conta ativa >> {} <<".format(paramet['conta'][str(cont)]))        
        gee.switch_user(paramet['conta'][str(cont)])
        gee.init()        
        gee.tasks(n= paramet['numeroTask'], return_list= True)        
    
    elif cont > paramet['numeroLimit']:
        return 0
    
    cont += 1    
    return cont


param = {
    'asset_caat_buffer': 'users/CartasSol/shapes/caatinga_buffer5km',
    'outputAsset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/toExport', 
    'inputAsset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/toExport',
    # 'newinputAsset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/toExport',  # BACIA_778_mixed_V244
    # projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/toExport/BACIA_7742_mixed_V26
    'biome': 'CAATINGA', #configure como null se for tema transversal
    'version': 26,
    'collection': '9.0',
    'source': 'geodatin',
    'setUniqueCount': True,
    'theme': None, 
    'numeroTask': 0,
    'numeroLimit': 42,
    'conta' : {
        '0': 'caatinga01',   # 
        '6': 'caatinga02',
        '12': 'caatinga03',
        '18': 'caatinga04',
        '24': 'caatinga05',        
        '32': 'solkan1201',    
        '38': 'solkanGeodatin'
    }
}

nameBacias = [
    '744','741','7421', '7422','745','746','7492','751','752',
    '753','755','758','759','7621','7622','764','765','766',
    '767','771','7741','772','7742','773','775', '777', '778',
    '76111','76116','7612','7614','7615','7616','7617','7618','7619', 
    '7613','756','757','763','776', '754',
]
countFix = 0
processExport = True
metadados = {}
bioma5kbuf = ee.FeatureCollection(param['asset_caat_buffer']).geometry()

lstBands = ['classification_' + str(yyear) for yyear in range(1985, 2023)]
lstImg = ee.List([])
for cc, id_bacias in enumerate(nameBacias):    
    nameImg = f'BACIA_{id_bacias}_mixed_V26'
    countFix = gerenciador(countFix, param)
    try:
        imgExpss = ee.Image(param['inputAsset'] + '/' + nameImg).select(lstBands)
        nameimg23 = f'BACIA_{id_bacias}_mixed_V27'
        imgExpss23 = ee.Image(param['inputAsset'] + '/' + nameimg23).select('classification_2023')
        print(f"merge {cc} === {nameImg} >>> {imgExpss.get('system:index').getInfo()}")
        imgExpss = imgExpss.addBands(imgExpss23)

        nameImgv28 = f'BACIA_{id_bacias}_mixed_V28'
        imgExpss = imgExpss.clip(bioma5kbuf).set('biome', param['biome'])\
                    .set('version', 28)\
                    .set('collection', param['collection'])\
                    .set('source', param['source'])\
                    .set('theme',None)\
                    .set('system:footprint', bioma5kbuf)
        
        optExp = {   
            'image': imgExpss.byte(), 
            'description': nameImgv28, 
            'assetId': param['outputAsset'] + '/' + nameImgv28, 
            'region': bioma5kbuf.getInfo()['coordinates'], #
            'scale': 30, 
            'maxPixels': 1e13,
            "pyramidingPolicy": {".default": "mode"}
        }
        task = ee.batch.Export.image.toAsset(**optExp)
        task.start() 
        print("salvando ... banda  " + name + "..!")
    except:
        print("bacia ", nameimg23)



