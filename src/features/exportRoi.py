#!/usr/bin/env python3
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

try:
    ee.Initialize()
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise
# sys.setrecursionlimit(1000000000)


param = {    
    'asset_ROIs_manual': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/ROIs/coletaROIsv7N2manual'},
    'asset_ROIs_cluster': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/ROIs/coletaROIsv6N2cluster'},
    'anoInicial': 1985,
    'anoFinal': 2022,
    'numeroTask': 6,
    'numeroLimit': 4,
    'conta' : {
        '0': 'caatinga04'              
    },

}

#lista de anos
list_anos = [k for k in range(param['anoInicial'],param['anoFinal'] + 1)]
print('lista de anos', list_anos)

#nome das bacias que fazem parte do bioma (38 bacias)
nameBacias = [
      '732','741','742','743','744', '745','746','747','751','752',
      '753', '754','755','756','757','758','759','762','763','765',
      '766','767','771','772','773', '774', '775','776','777',
      '7611','7612','7613','7614','7615','7616', '7617','7618','7619'
]

#========================METODOS=============================
def GetPolygonsfromFolder(dictAsset):
    
    getlistPtos = ee.data.getList(dictAsset)
    ColectionPtos = []
    # print("bacias vizinhas ", nBacias)
    lstROIsAg = [ ]
    for idAsset in getlistPtos:         
        path_ = idAsset.get('id')        
        ColectionPtos.append(path_) 
        name = path_.split("/")[-1]
        print("Reading ", name)
        
    return ColectionPtos


#========================METODOS=============================
def gerenciador(cont, param):
    #0, 18, 36, 54]
    #=====================================#
    # gerenciador de contas para controlar# 
    # processos task no gee               #
    #=====================================#
    numberofChange = [kk for kk in param['conta'].keys()]

    if str(cont) in numberofChange:
        
        gee.switch_user(param['conta'][str(cont)])
        gee.init()        
        gee.tasks(n= param['numeroTask'], return_list= True)        
    
    elif cont > param['numeroLimit']:
        cont = 0
    
    cont += 1    
    return cont

#exporta a imagem classificada para o asset
def processoExportar(ROIsFeat, nameB, nfolder):
    
    optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'folder': nfolder          
        }
    task = ee.batch.Export.table.toDrive(**optExp)
    task.start() 
    print("salvando ... " + nameB + "..!")    


lstKeysFolder = ['asset_ROIs_cluster', 'asset_ROIs_manual']
for assetKey in lstKeysFolder:
    lstAssetFolder = GetPolygonsfromFolder(param[assetKey])
    list_baciaYearFaltan = []
    cont = 0
    cont = gerenciador(cont, param)
    for assetFeats in lstAssetFolder[:]:
        print("loading FeatureCollection => ", assetFeats)
        nameFeat = assetFeats.split("/")[-1]
        try: 
            ROIs = ee.FeatureCollection(assetFeats)            
            processoExportar(ROIs, nameFeat, assetKey.replace('asset_', 'Col9_'))               
        except:
            # list_baciaYearFaltan.append(nameFeat)
            # arqFaltante.write(nameFeat + '\n')
            print("faltando ... " + nameFeat)

    # arqFaltante.close()