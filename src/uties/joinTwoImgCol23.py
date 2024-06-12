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

def processoExportar(mapaRF,  nomeDesc, geom_bacia):    
    idasset =  param['output_asset'] + nomeDesc
    optExp = {
        'image': mapaRF, 
        'description': nomeDesc, 
        'assetId':idasset, 
        'region': geom_bacia.getInfo()['coordinates'],
        'scale': 30, 
        'maxPixels': 1e13,
        "pyramidingPolicy":{".default": "mode"}
    }
    task = ee.batch.Export.image.toAsset(**optExp)
    task.start() 
    print("salvando ... " + nomeDesc + "..!")



param = {
    'asset_caat_buffer': 'users/CartasSol/shapes/caatinga_buffer5km',
    'output_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/toExport/', 
    'inputAsset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/toExport',
    'newinputAsset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/toExport',  # BACIA_778_mixed_V244
    'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrograficaCaatbuffer5k',
    'biome': 'CAATINGA', #configure como null se for tema transversal
    'version': 25,
    'collection': 9.0,
    'year_first': 1985,
    'year_end': 2023,
    'source': 'geodatin',
    'setUniqueCount': True,
    'theme': None, 
    'numeroTask': 0,
    'numeroLimit': 42,
    'conta' : {
        '0': 'caatinga01',   # 
        '7': 'caatinga02',
        '14': 'caatinga03',
        '21': 'caatinga04',
        '28': 'caatinga05',
        '35': 'solkan1201'    
    }
}

listaNameBacias = [
    '744','741','7422','745','746','7492','751','752','753',
    '755','759','7621','7622', '763','764','765','766',
    '767', '771', '772','773','7741','776','7742','775', 
    '777', '778','76111','76116','7612','7613','7615','7616',
    '7617','7618','7619','756','757','758', '7614', '7421', 
    '754', '741', '7422', '7621', '764'
]

lstBands = ['classification_' + str(yy) for yy in range(param['year_first'], param['year_end'])]
print(" lista de bandas ", lstBands)


cont = 0
processExport = False
metadados = {}
bioma5kbuf = ee.FeatureCollection(param['asset_caat_buffer']).geometry()
imgColExp = ee.ImageCollection(param['inputAsset']).filter(
                                            ee.Filter.eq('version', 22)).select(lstBands)
numMaps = imgColExp.size().getInfo()
print(f' We have {numMaps} imagens maps by basin in this asset')
print("lista de bandas da imagem min \n ", imgColExp.first().bandNames().getInfo())

imgColExpNew = ee.ImageCollection(param['inputAsset']).filter(
                                            ee.Filter.eq('version', 24))
print(f' We have {imgColExpNew.size().getInfo()} imagens maps by basin in this asset')
print(f" and {imgColExpNew.first().bandNames().getInfo()} bandas ")

for id_bacia in listaNameBacias:
    geomBacia = ee.FeatureCollection(param['asset_bacias_buffer']).filter(
                                ee.Filter.eq('nunivotto3', id_bacia)).first().geometry()

    imgBacia_parte1 = imgColExp.filter(ee.Filter.eq('id_bacia', id_bacia)).first()
    # print("loading ", imgBacia_parte1.get('system:index').getInfo())    
    
    imgBacia_parte2 = imgColExpNew.filter(ee.Filter.eq('id_bacia', id_bacia)).first()
    # print("loading ", imgBacia_parte2.get('system:index').getInfo())    

    imgBacia_parte1 = imgBacia_parte1.addBands(imgBacia_parte2.select('classification_2023'))      
    # print(f" and {imgBacia_parte1.first().bandNames().getInfo()} bandas ")

    imgBacia_parte1 = imgBacia_parte1.set(
                        'version', 25, 'biome', 'CAATINGA',
                        'collection', '9.0', 'id_bacia', id_bacia,
                        'sensor', 'Landsat', 'source','geodatin', 
                        'from', 'mixed', 'model', 'GTB', 'janela', 5, 
                        'system:footprint', geomBacia
                    )
    cont = gerenciador(cont, param) 
    nameExp = f"BACIA_{id_bacia}_mixed_V25"
    processoExportar(imgBacia_parte1,  nameExp, geomBacia)