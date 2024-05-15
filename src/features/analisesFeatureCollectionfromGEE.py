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
import pandas as pd
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
    'asset_ROIs_automatic': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/coletaROIsv1N245'},
    'asset_ROIs_automatic': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/cROIsN5allBND'},
    'asset_ROIs_grades': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/roisGradesgrouped'},
    'asset_ROIS_bacia_grade': {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/roisGradesgroupedBuf'},
    'asset_ROIS_joinsBaGr': {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/roisJoinsbyBaciaNN'},
    'asset_ROISall_joins': {'id': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/roisJoinedBaGrNN'},
    'anoInicial': 1985,
    'anoFinal': 2022,
    'numeroTask': 6,
    'numeroLimit': 4,
    'conta' : {
        '0': 'solkanGeodatin'              
    },
    'showFilesCSV' : False,
    'showAssetFeat': False
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
lstFeatSpIndex = [
    "swir1_stdDev_1","nir_stdDev_1","green_stdDev_1","ratio_median_dry","gli_median_wet","dswi5_median_dry",
    "ri_median","osavi_median","swir2_min","shape_median","mbi_median_dry","wetness_median_dry","green_median_texture_1",
    "iia_median_wet","slopeA_1","brba_median_dry","nir_median","lswi_median_wet","red_min","rvi_median","green_min",
    "gcvi_median_dry","shape_median_dry","cvi_median_dry","blue_median_dry","mbi_median","nir_median_dry_contrast",
    "swir2_median_wet","ui_median_wet","red_median_wet","avi_median","nir_stdDev","swir1_stdDev","red_median_dry",
    "gemi_median","osavi_median_dry","blue_median_dry_1","swir2_median_dry_1","brba_median","ratio_median",
    "gli_median_dry","blue_min_1","wetness_median","green_median_wet","blue_median_wet_1","brightness_median_wet",
    "blue_min","blue_median","red_median_contrast","swir1_min_1","evi_median","blue_stdDev_1","lswi_median_dry",
    "blue_median_wet","cvi_median","red_stdDev_1","shape_median_wet","red_median_dry_1","swir2_median_wet_1",
    "dswi5_median_wet","red_median_wet_1","afvi_median","ndwi_median","avi_median_wet","gli_median","evi_median_wet",
    "nir_median_dry","gvmi_median","cvi_median_wet","swir2_min_1","iia_median","ndwi_median_dry","green_min_1",
    "ri_median_dry","osavi_median_wet","green_median_dry","ui_median_dry","red_stdDev","nir_median_wet_1",
    "swir1_median_dry_1","red_median_1","nir_median_dry_1","swir1_median_wet","blue_stdDev","bsi_median",
    "swir1_median","swir2_median","gvmi_median_dry","red_median","gemi_median_wet","lswi_median",
    "brightness_median_dry","awei_median_wet","nir_min","afvi_median_wet","nir_median_wet","evi_median_dry",
    "swir2_median_1","ndwi_median_wet","ratio_median_wet","swir2_stdDev","gcvi_median","ui_median","rvi_median_wet",
    "green_median_wet_1","ri_median_wet","nir_min_1","rvi_median_1","swir1_median_dry","blue_median_1","green_median_1",
    "avi_median_dry","gvmi_median_wet","wetness_median_wet","swir1_median_1","dswi5_median","swir2_stdDev_1",
    "awei_median","red_min_1","mbi_median_wet","brba_median_wet","green_stdDev","green_median_texture","swir1_min",
    "awei_median_dry","swir1_median_wet_1","gemi_median_dry","nir_median_1","red_median_dry_contrast","bsi_median_1",
    "bsi_median_2","nir_median_contrast","green_median_dry_1","afvi_median_dry","gcvi_median_wet","iia_median_dry",
    "brightness_median","green_median","swir2_median_dry"
]



#========================METODOS=============================

def getInfofromAssetROIs(fcROIs, nbacia, yyear):
    dictStatFeat = {
        'min': [],
        'max': [],
        'mean': [],
        'total_sd': [],
        'valid_count': [],
        'total_count': [],
        'bacia': [],
        'year': [],
        'spectralInd': []
    }
    for bndInd in lstFeatSpIndex:
        dictStat  = fcROIs.aggregate_stats(bndInd).getInfo()
        print(f"show dict stat {bndInd} \n = ", dictStat)
        dictStatFeat['min'] += [dictStat['min']]
        dictStatFeat['max'] += [dictStat['max']]
        dictStatFeat['mean'] += [dictStat['mean']]
        dictStatFeat['total_sd'] += [dictStat['total_sd']]
        dictStatFeat['valid_count'] += [dictStat['valid_count']]
        dictStatFeat['total_count'] += [dictStat['total_count']]
        dictStatFeat['bacia'] += [nbacia]
        dictStatFeat['year'] += [yyear]
        dictStatFeat['spectralInd'] += [bndInd]
    
    print("done ")
    return dictStatFeat

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

changeAcount = False
saveStatcsv = True
# get dir path of script 
npath = os.getcwd()
# get dir folder before to path scripts 
npath = str(Path(npath).parents[0])
print("path of CSVs Rois is \n ==>",  npath)

# sys.exit()
# lstPathCSV = glob.glob(npath + "*.csv")
# lstNameFeat = []
# for xpath in tqdm(lstPathCSV):
#     nameCSV = xpath.split("/")[-1][:-4]
#     if param['showFilesCSV']:
#         print(" => " + nameCSV)
#     lstNameFeat.append(nameCSV)

cont = 0
if changeAcount:
    cont = gerenciador(cont, param)
lstNameFeat = []

# sys.exit()
if saveStatcsv: 
    # iterando com cada uma das folders FeatC do asset
    # 'asset_ROIs_cluster', 'asset_ROIs_manual', asset_ROIs_grades, asset_ROIS_bacia_grade
    # asset_ROIS_joinsBaGr ,asset_ROISall_joins
    lstKeysFolder = ['asset_ROISall_joins']   
    for assetKey in lstKeysFolder:
        endpath = npath + '/dados/statROIs/'
        lstAssetFolder = GetPolygonsfromFolder(param[assetKey])
        list_baciaYearFaltan = []
        totalReaded = len(lstAssetFolder)
        for cc, assetFeats in enumerate(lstAssetFolder[:]):        
            nameFeat = assetFeats.split("/")[-1]
            print("loading FeatureCollection => ", assetFeats)
            
            ROIs = ee.FeatureCollection(assetFeats)       
              
            partes = nameFeat.split('_')
            # joined_ROIs_741_1985_wl
            nameBacia = partes[-3]
            nyear = int(partes[-2])
            print(f" {cc}/{totalReaded} file {nameFeat} ==>  {ROIs.size().getInfo()}")
            dictStatGeral = getInfofromAssetROIs(ROIs, nameBacia, nyear)

            nameExp = 'stat_' + nameFeat + '.csv'
            dfStat = pd.DataFrame.from_dict(dictStatGeral)
            dfStat.to_csv(endpath + nameExp, index_label= 'Index')
