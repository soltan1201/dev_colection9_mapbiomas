#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
# SCRIPT DE CLASSIFICACAO POR BACIA
# Produzido por Geodatin - Dados e Geoinformacao
# DISTRIBUIDO COM GPLv2
'''

import ee 
import gee
import copy
import sys
import json
import os
import glob
from icecream import ic
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
    'assetROIgradeBa': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/roisGradesgroupedBuf',
    'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrograficaCaatbuffer5k',
    'asset_shpGrade': 'projects/mapbiomas-arida/ALERTAS/auxiliar/basegrade30KMCaatinga',
    'assetROIgrade': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/roisGradesgrouped',
    'asset_output': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/roisGradesgroupBuf',
    'assetROIs': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/cROIsN2clusterNN',
    'assetROIsExt': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/cROIsN2manualNN',
    'numeroTask': 6,
    'numeroLimit': 42,
    'conta' : {
        '0': 'caatinga01',
        '7': 'caatinga02',
        '14': 'caatinga03',
        '21': 'caatinga04',
        '28': 'caatinga05',        
        '35': 'solkan1201',
        # '36': 'rodrigo',
        # '35': 'diegoGmail',    
    },
}
def gerenciador(cont):
    #0, 18, 36, 54]
    #=====================================#
    # gerenciador de contas para controlar# 
    # processos task no gee               #
    #=====================================#
    numberofChange = [kk for kk in param['conta'].keys()]    
    if str(cont) in numberofChange:

        print("conta ativa >> {} <<".format(param['conta'][str(cont)]))        
        gee.switch_user(param['conta'][str(cont)])
        gee.init()        
        gee.tasks(n= param['numeroTask'], return_list= True)       
         
    
    elif cont > param['numeroLimit']:        
        return 0   
    
    cont += 1 
    return cont


def changeClassFeat(feat):

    dictClass = {
        3: 3,
        4: 4,
        9: 12,
        15: 15,
        12: 12,
        18: 18,
        21: 21,
        33: 33,
        41: 18,
        25: 22,
        39: 18,
        48: 18,
        30: 70,
        24: 22,
        20: 18,
        32: 70    
    }
    dictClass = ee.Dictionary(dictClass)
    return feat.set('class', dictClass.get(feat.get('class')))

#========================METODOS=============================
def GetPolygonsfromFolder(pathAsset):
    dictAsset = {'id': pathAsset}
    getlistPtos = ee.data.getList(dictAsset)
    lstidGrades = []
    for idAsset in tqdm(getlistPtos):         
        path_ = idAsset.get('id')
        lstidGrades.append(path_)

    ic(f"we have in the folder {len(lstidGrades)}")
    return lstidGrades

#exporta a imagem classificada para o asset
def processoExportar(ROIsFeat, nameB, idPos):
    optExp = {
        'collection': ROIsFeat,
        'description': nameB,
        'assetId': param['asset_output'] + "/" + nameB,
        # 'priority': 8000
    }
    task = ee.batch.Export.table.toAsset(**optExp)
    task.start() 
    print(f" # {idPos} salvando ... " + nameB + " in asset ..!")


knowDistClass = True
cont = gerenciador(0) 
# we have know how many grades ROIs have in the folder 
lstAllgradeSaved = GetPolygonsfromFolder(param['asset_output'])
lstAllClass = []
for cc, assetpath in enumerate(lstAllgradeSaved):
    feattmp = ee.FeatureCollection(assetpath).filter(ee.Filter.inList('class', [30,32]).Not())
    name = assetpath.split("/")[-1]
    
    if knowDistClass:        
        lstCC = feattmp.reduceColumns(ee.Reducer.toList(),['class']).get('list')
        lstCC = ee.List(lstCC).distinct().getInfo()
        print(f"{cc} processing {name}    >>>> {lstCC} ")
        for cc in lstCC:
            if cc not in lstAllClass:
                lstAllClass.append(cc)

    else:
        feattmpClean = feattmp.map(lambda feat: changeClassFeat(feat))        
        processoExportar(feattmpClean, name, cc)
        cont = gerenciador(cont) 

print("all class ", lstAllClass)    