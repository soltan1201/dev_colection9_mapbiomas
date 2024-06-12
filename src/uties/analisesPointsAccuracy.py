#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
'''

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


#exporta a imagem classificada para o asset
def processoExportar(ROIsFeat, nameT):  

    optExp = {
        'collection': ROIsFeat, 
        'description': nameT, 
        'assetId':"projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/" + nameT          
    }
    task = ee.batch.Export.table.toAsset(**optExp)
    task.start() 
    print("salvando ... " + nameT + "..!")
    

#nome das bacias que fazem parte do bioma
nameBacias = [
    '7421','741', '7422','744','745','746','751', '752', '7492',
    '753', '754','755','756','757','758','759','7621','7622','763',
    '764','766','771','772','773', '7742','775',  '7741',
    '76111','76116','7612','7613','7614','7615',  '777','778',
    '7616','7617','7618', '7619', '765', '767', '776',
    # '7741', '776'
] 

param = {
    'lsBiomas': ['CAATINGA'],
    'asset_bacias': 'projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga',
    'assetBiomas' : 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil',
    'asset_caat_buffer': 'users/CartasSol/shapes/caatinga_buffer5km',
    'assetpointLapig23': 'projects/mapbiomas-workspace/VALIDACAO/mapbiomas_85k_col3_points_w_edge_and_edited_v2',
    'assetpointLapig24': 'projects/mapbiomas-workspace/VALIDACAO/mapbiomas_85k_col3_points_w_edge_and_edited_v3',    
    'assetpointLapig23rc': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/mapbiomas_85k_col3_points_w_edge_and_edited_v2_Caat_reclass',
    'assetpointLapig24rc': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/mapbiomas_85k_col3_points_w_edge_and_edited_v3_Caat_reclass',
    'limit_bacias': "users/CartasSol/shapes/bacias_limit",
    'assetCol': "projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVX" ,
    'assetColprob': "projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVP" ,
    'assetFilters': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/SpatialV3',
    'classMapB': [3, 4, 5, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,39,40,41,46,47,48,49,50,62],
    'classNew':  [3, 4, 3, 3,12,12,21,21,21,21,21,22,22,22,22,33,29,22,33,12,33,21,21,21,21,21,21,21, 3,12,21],
    'classesMapAmp':  [3, 4, 3, 3,12,12,15,18,18,18,21,22,22,22,22,33,29,22,33,12,33,18,18,18,18,18,18,18, 3,12,18],
    'inBacia': True,
    'anoInicial': 1985,
    'anoFinal': 2022,  # 2019
    'numeroTask': 6,
    'numeroLimit': 2,
    'changeAcount': False,
    'conta' : {
        '0': 'solkanGeodatin'              
    },
    'lsProp': ['ESTADO','LON','LAT','PESO_AMOS','PROB_AMOS','REGIAO','TARGET_FID','UF'],
    "amostrarImg": False,
    'isImgCol': False
}



def change_value_class(feat):
    ## Load dictionary of class
    dictRemap =  {
        "FORMAÇÃO FLORESTAL": 3,
        "FORMAÇÃO SAVÂNICA": 4,        
        "MANGUE": 3,
        "RESTINGA HERBÁCEA": 3,
        "FLORESTA PLANTADA": 18,
        "FLORESTA INUNDÁVEL": 3,
        "CAMPO ALAGADO E ÁREA PANTANOSA": 12,
        "APICUM": 12,
        "FORMAÇÃO CAMPESTRE": 12,
        "AFLORAMENTO ROCHOSO": 29,
        "OUTRA FORMAÇÃO NÃO FLORESTAL":12,
        "PASTAGEM": 15,
        "CANA": 18,
        "LAVOURA TEMPORÁRIA": 18,
        "LAVOURA PERENE": 18,
        "MINERAÇÃO": 22,
        "PRAIA E DUNA": 22,
        "INFRAESTRUTURA URBANA": 22,
        "VEGETAÇÃO URBANA": 3,
        "OUTRA ÁREA NÃO VEGETADA": 22,
        "RIO, LAGO E OCEANO": 33,
        "AQUICULTURA": 33,
        "NÃO OBSERVADO": 27  
    }
    pts_remap = ee.Dictionary(dictRemap) 

    prop_select = [
        'BIOMA', 'CARTA','DECLIVIDAD','ESTADO','JOIN_ID','PESO_AMOS'
        ,'POINTEDITE','PROB_AMOS','REGIAO','TARGET_FID','UF', 'LON', 'LAT']
    
    feat_tmp = feat.select(prop_select)
    for year in range(1985, 2023):
        nam_class = "CLASS_" + str(year)
        set_class = "CLASS_" + str(year)
        valor_class = ee.String(feat.get(nam_class))
        feat_tmp = feat_tmp.set(set_class, pts_remap.get(valor_class))
    
    return feat_tmp



expPointLapig = False
knowImgcolg = True
param['isImgCol'] = True
param['inBacia'] = True
version = 22
biomaCaat250mil = ee.FeatureCollection(param['asset_caat_buffer']).geometry()

if expPointLapig:
    ## os pontos só serão aqueles que representam a Caatinga 
    ptsTrue23 = ee.FeatureCollection(param['assetpointLapig23']).filterBounds(biomaCaat250mil)
    print("Know size table ptsTrue ", ptsTrue23.size().getInfo())
    print("know how many class points in Caatinga ", ptsTrue23.aggregate_histogram('CLASS_2022').getInfo())

    # sys.exit()
    pointTrue23 = ptsTrue23.map(lambda feat: change_value_class(feat))
    print("Carregamos {} points ".format(pointTrue23.size().getInfo()))  # pointTrue.size().getInfo()
    print("know the first points ", pointTrue23.first().getInfo())

    processoExportar(ptsTrue23, param['assetpointLapig23'].split("/")[-1] + "_Caat")
    processoExportar(pointTrue23, param['assetpointLapig23'].split("/")[-1] + '_Caat_reclass')

    # process to year 2024
    ptsTrue24 = ee.FeatureCollection(param['assetpointLapig24']).filterBounds(biomaCaat250mil)
    print("Know size table ptsTrue ", ptsTrue24.size().getInfo())
    print("know how many class points in Caatinga ", ptsTrue24.aggregate_histogram('CLASS_2022').getInfo())

    # sys.exit()
    pointTrue24 = ptsTrue24.map(lambda feat: change_value_class(feat))
    print("Carregamos {} points ".format(pointTrue24.size().getInfo()))  # pointTrue.size().getInfo()
    print("know the first points ", pointTrue24.first().getInfo())

    processoExportar(ptsTrue24, param['assetpointLapig24'].split("/")[-1] + "_Caat")
    processoExportar(pointTrue24, param['assetpointLapig24'].split("/")[-1] + '_Caat_reclass')

else:
    ptsTrue23rc = ee.FeatureCollection(param['assetpointLapig23rc'])
    print("Carregamos {} points ".format(ptsTrue23rc.size().getInfo()))  # pointTrue.size().getInfo()
    # print("know how many class points in Caatinga ", ptsTrue23rc.aggregate_histogram('CLASS_2022').getInfo())

    ptsTrue24rc = ee.FeatureCollection(param['assetpointLapig24rc'])
    print("Carregamos {} points revisão 2024".format(ptsTrue24rc.size().getInfo()))  # pointTrue.size().getInfo()
    # print("know how many class points in Caatinga ", ptsTrue24rc.aggregate_histogram('CLASS_2022').getInfo())

    for yy in range(1985, 2022, 2):
        yearBand = 'CLASS_' + str(yy)
        dictPtos23 = ptsTrue23rc.aggregate_histogram(yearBand).getInfo()
        dictPtos24 = ptsTrue24rc.aggregate_histogram(yearBand).getInfo()
        lstKeys = [kk for kk in dictPtos24.keys()]
        print(f"------------ YEAR {yy} -----------------")
        for cclass in lstKeys:
            print(f" class {cclass} | points23 {dictPtos23[cclass]}   | points24 {dictPtos24[cclass]} | teste {dictPtos23[cclass] - dictPtos24[cclass]}")
