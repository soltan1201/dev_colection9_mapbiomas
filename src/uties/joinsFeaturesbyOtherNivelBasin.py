#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
# SCRIPT DE CLASSIFICACAO POR BACIA
# Produzido por Geodatin - Dados e Geoinformacao
# DISTRIBUIDO COM GPLv2
'''

import ee 
import gee
import sys
import os
import glob
from pathlib import Path
from tqdm import tqdm
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
    'asset_ROIs_manual': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/cROIsN2manualNN'},
    'asset_ROIs_cluster': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/cROIsN2clusterNN'},
    'asset_ROIs_automaticN245': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/cROIsN245_allBND'},
    'asset_ROIs_automaticN5': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/cROIsN5allBND'},
    'anoInicial': 1985,
    'anoFinal': 2022,
    'numeroTask': 6,
    'numeroLimit': 4,
    'conta' : {
        '0': 'caatinga02'              
    },
    'showFilesCSV' : False,
    'showAssetFeat': False
}

nameBacias = [
    '741','7421','7422','744','745','746','7492','751','752','753',
    '754','755','756','757','758','759','7621','7622','763','764',
    '765','766','767','771','772','773', '7741','7742','775','776',
    '777','778','76111','76116','7612','7614','7615','7616','7617',
    '7618','7619', '7613'
]


#========================METODOS=============================
def GetPolygonsfromFolder(dictAsset):
    
    getlistPtos = ee.data.getList(dictAsset)
    ColectionPtos = []
    # print("bacias vizinhas ", nBacias)
    lstROIsAg = [ ]
    for idAsset in tqdm(getlistPtos):         
        path_ = idAsset.get('id')        
        ColectionPtos.append(path_) 
        name = path_.split("/")[-1]
        if param['showAssetFeat']:
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


def getDictBasinN5(lstAssetfromFolder):
    dictCount = {}

    for cc, assetFeats in enumerate(lstAssetfromFolder[:]):        
        nameFeat = assetFeats.split("/")[-1]    
        partes = nameFeat.split("_")

        codBasinN5 = partes[0]
        if len(codBasinN5) >= 5:
            codBasinN5 = codBasinN5[:-2]  
            if codBasinN5 == '761':
                codBasinN5 = partes[0][:-1]              

        else:
            codBasinN5 = codBasinN5[:-1]
        
        year = int(partes[1])
        
        lstKey = dictCount.keys()
        if codBasinN5 in lstKey:
            lsttmp = dictCount[codBasinN5]
            lsttmp.append(nameFeat)
            dictCount[codBasinN5] = lsttmp
        else:
            dictCount[codBasinN5] = [nameFeat]

        if codBasinN5 == '774':
            print("# ", cc, " loading FeatureCollection => ", nameFeat, " ==> ", codBasinN5)

    return dictCount


def getDictBasinN245(lstAssetfromFolder):
    dictCount = {}

    for cc, assetFeats in enumerate(lstAssetfromFolder[:]):        
        nameFeat = assetFeats.split("/")[-1]    
        partes = nameFeat.split("_")
        codBasin = partes[0]
        lstKey = dictCount.keys()
        if codBasin in lstKey:
            lsttmp = dictCount[codBasin]
            lsttmp.append(nameFeat)
            dictCount[codBasin] = lsttmp
        else:
            dictCount[codBasin] = [nameFeat]

    return dictCount

cont = 0
# cont = gerenciador(cont, param)
# iterando com cada uma das folders FeatC do asset
lstKeysFolder = 'asset_ROIs_automaticN245'   # ,'asset_ROIs_cluster', 'asset_ROIs_manual', 'asset_ROIs_automaticN5'
lstAssetFolder = GetPolygonsfromFolder(param[lstKeysFolder])

if lstKeysFolder == 'asset_ROIs_automaticN5':
    dictBasin = getDictBasinN5(lstAssetFolder)

elif lstKeysFolder == 'asset_ROIs_automaticN245':
    dictBasin = getDictBasinN245(lstAssetFolder)

count = 0
for nky, lstVal in dictBasin.items():
    print(f"# {count} =>  {nky} ==> {len(lstVal)}")
    count += 1

lstKeysB = dictBasin.keys()
restante = []
for nbacia in nameBacias:
    if nbacia not in lstKeysB:
        restante.append(nbacia)

print("we need to research in basin ", restante )
print(len(restante))