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
    'asset_ROIs_autGrade': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/cROIsN5allBND'},
    'asset_ROIs_autGradeNormal': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/cROIsGradeallBNDNormal'},
    'asset_output': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/roisGradesgrouped',
    'anoInicial': 1985,
    'anoFinal': 2022,
    'numeroTask': 6,
    'numeroLimit': 600,
    'conta': {
        '0': 'caatinga01',
        '100': 'caatinga05',
        '200': 'caatinga02',
        '300': 'caatinga04',
        '400': 'caatinga03',
        '500': 'solkan1201',
        '600': 'solkanGeodatin',
        # '20': 'solkanGeodatin'
    },
    'showFilesCSV' : False,
    'showAssetFeat': True
}

nameBacias = [
    '741','7421','7422','744','745','746','7492','751','752','753',
    '754','755','756','757','758','759','7621','7622','763','764',
    '765','766','767','771','772','773', '7741','7742','775','776',
    '777','778','76111','76116','7612','7614','7615','7616','7617',
    '7618','7619', '7613'
]


#========================METODOS=============================
def GetPolygonsfromFolder(dictAsset, mergeGrade):
    
    getlistPtos = ee.data.getList(dictAsset)
    ColectionPtos = []
    # print("bacias vizinhas ", nBacias)
    lstROIsAg = [ ]
    for idAsset in tqdm(getlistPtos):         
        path_ = idAsset.get('id')        
        name = path_.split("/")[-1]
        if mergeGrade:
            if 'gradeROIs_' in name:
                ColectionPtos.append(name) 
                if param['showAssetFeat']:
                    print("Reading ", name)

        else:
            if 'gradeROIs_' in name:
                ColectionPtos.append(name)
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
def processoExportar(ROIsFeat, nameB, nfolder, exportD, idPos):
    if exportD:
        optExp = {
            'collection': ROIsFeat, 
            'description': nameB, 
            'folder': nfolder          
            }
        task = ee.batch.Export.table.toDrive(**optExp)
        task.start() 
        print("salvando ... " + nameB + "..!")    
    else:
        optExp = {
            'collection': ROIsFeat,
            'description': nameB,
            'assetId': param['asset_output'] + "/" + nameB,
            # 'priority': 8000
        }
        task = ee.batch.Export.table.toAsset(**optExp)
        task.start() 
        print(f" # {idPos} salvando ... " + nameB + " in asset ..!")


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


def getDictRegionCounting(lstAssetfromFolder, posCodReg):
    dictCount = {}
    for cc, nameFeat in enumerate(lstAssetfromFolder[:]):          
        partes = nameFeat.split("_")
        codReg = partes[posCodReg]
        lstKey = dictCount.keys()
        # addiconar a lista novos anos 
        if codReg in lstKey:
            lsttmp = dictCount[codReg]
            lsttmp.append(nameFeat)
            dictCount[codReg] = lsttmp
        else:
            dictCount[codReg] = [nameFeat]
    
    count = 0
    if param['showAssetFeat']:
        for kk, lstVal in dictCount.items():
            print(f"# {count} => region {kk} = > {len(lstVal)}")
            count += 1
    return dictCount

cont = 0
joinGrade = True
byBacia = False
cont = gerenciador(cont, param)
# iterando com cada uma das folders FeatC do asset
KeysFolder =  'asset_ROIs_autGradeNormal' #'asset_ROIs_autGrade'   # ,'asset_ROIs_cluster', 'asset_ROIs_manual', 'asset_ROIs_automaticN5'
lstAssetFolder = GetPolygonsfromFolder(param[KeysFolder], joinGrade)
print(f"we have {len(lstAssetFolder)} features ROIs ")
# codigo region se encontra na posição 1 gradeROIs_991_2023_wl
dictRegCount = getDictRegionCounting(lstAssetFolder, 1)
sys.exit()


lstKeysB = [kk for kk in dictRegCount.keys()]
if byBacia:
    restante = []
    for region in nameBacias:
        if nbacia not in lstKeysB:
            restante.append(nbacia)

    print("we 🫵 need to research in basin ", restante )
    print(len(restante))

else:

    for cc, idRegion in enumerate(lstKeysB):
        featTempReg = ee.FeatureCollection([])
        lstNameFeat = dictRegCount[idRegion]
        for nameFeat in tqdm(lstNameFeat):
            featCtmp = ee.FeatureCollection(param[KeysFolder]['id'] + "/" + nameFeat)
            # print(f"show {nameFeat} the number of samples {featCtmp.size().getInfo()}")
            featTempReg = featTempReg.merge(featCtmp)
        cont = gerenciador(cont, param)
        # featTempReg = featTempReg.flatten()
        nameExport = 'gradeROIs_' + idRegion + "_wl"
        processoExportar(featTempReg, nameExport, None, False, cc)