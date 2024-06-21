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
    'newinputAsset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/toExportYY',  # BACIA_778_mixed_V244
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
        '0': 'solkanGeodatin',        
    }
}
classMapB = [ 0, 3, 4, 5, 6, 9,11,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62]
classNew =  [27, 4, 4, 4, 4, 4,12,12,12,21,21,21,21,21,22,22,22,22,33,29,22,33,12,33,21,33,33,21,21,21,21,21,21,21,21,21,21,49,50,21]

listaNameBacias = [
    '744','741','7422','745','746','7492','751','752','753',
    '755','759','7621','7622', '763','764','765','766',
    '767', '771', '772','773','7741','776','7742','775', 
    '777', '778','76111','76116','7612','7613','7615','7616',
    '7617','7618','7619','756','757','758', '7614', '7421', 
    '754', '741', '7422', '7621', '764'
]

lstBands = ['classification_' + str(yy) for yy in range(param['year_first'], param['year_end'] + 1)]
print(" lista de bandas ", lstBands)

cont = 0
cont = gerenciador(cont, param) 
processExport = False
metadados = {}
bioma5kbuf = ee.FeatureCollection(param['asset_caat_buffer']).geometry()
imgColExp = ee.ImageCollection(param['inputAsset']).filter(
                                            ee.Filter.eq('version', 30)).select(lstBands)
numMaps = imgColExp.size().getInfo()
print(f' We have {numMaps} imagens maps by basin in this asset')
print("lista de bandas da imagem min \n ", imgColExp.first().bandNames().getInfo())

assetLayerFF = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/toExportYY/layer_florest_correcao_mais_2023_V3'
imgColExpNew = ee.Image(assetLayerFF).unmask(0)
print(f' We have {imgColExp.size().getInfo()} imagens maps by basin in this asset')
print(f" and {imgColExpNew.bandNames().getInfo()} bandas ")
# sys.exit()
for cc, id_bacia in enumerate(listaNameBacias):
    print(f" ======= #{cc} == BACIA {id_bacia}===============")
    geomBacia = ee.FeatureCollection(param['asset_bacias_buffer']).filter(
                                ee.Filter.eq('nunivotto3', id_bacia)).first().geometry()

    imgBacia_parte1 = imgColExp.filter(ee.Filter.eq('id_bacia', id_bacia)).first()
    rasterBacia = ee.Image().byte()
    layerFF22 = None
    # print("loading ", imgBacia_parte1.get('system:index').getInfo())    
    for bandsAct in lstBands:
        print("processing " + bandsAct)
        rasterYY = imgBacia_parte1.select(bandsAct)
        if bandsAct == 'classification_2022':
            layerFF22 = rasterYY.eq(3)
        elif bandsAct == 'classification_2023':
            print("change year 23")
            rasterYY = rasterYY.remap(classMapB, classNew).where(layerFF22.eq(1), layerFF22.multiply(3))

        rasterBacia = rasterBacia.addBands(rasterYY.rename(bandsAct))

    rasterBacia = rasterBacia.select(lstBands).clip(geomBacia).set(
                        'version', 31, 'biome', 'CAATINGA',
                        'collection', '9.0', 'id_bacia', id_bacia,
                        'sensor', 'Landsat', 'source','geodatin', 
                        'from', 'mixed', 'joinFF', 'GTB', 'janela', 5, 
                        'system:footprint', geomBacia
                    )
                        
    nameExp = f"BACIA_{id_bacia}_mixed_V31"
    processoExportar(rasterBacia,  nameExp, geomBacia)