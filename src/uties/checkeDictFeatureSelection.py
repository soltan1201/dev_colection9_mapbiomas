#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
'''

import os
import sys
import json
import copy
from pathlib import Path
from icecream import ic


bandNames = [
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

bandasComunsCorr = [
    'slope', 'blue_median_1', 'blue_median_wet_1', 'blue_median_dry_1', 'blue_min_1', 'blue_stdDev_1', 'green_median_1', 
    'green_median_wet_1', 'green_median_dry_1', 'green_min_1', 'green_stdDev_1', 'green_median_texture_1', 'red_median_1', 
    'red_median_wet_1', 'red_median_dry_1', 'red_min_1', 'red_stdDev_1', 'nir_median_1', 'nir_median_wet_1', 'nir_median_dry_1', 
    'nir_min_1', 'nir_stdDev_1', 'swir1_median_1', 'swir1_median_wet_1', 'swir1_median_dry_1', 'swir1_min_1', 'swir1_stdDev_1', 
    'swir2_median_1', 'swir2_median_wet_1', 'swir2_median_dry_1', 'swir2_min_1', 'swir2_stdDev_1', 'slopeA_1', 'ratio_median', 
    'rvi_median', 'ndwi_median', 'awei_median', 'iia_median', 'gcvi_median', 'gemi_median', 'cvi_median', 'gli_median', 
    'shape_median', 'afvi_median', 'avi_median', 'bsi_median', 'brba_median', 'dswi5_median', 'lswi_median', 'mbi_median', 
    'ui_median', 'osavi_median', 'ri_median', 'brightness_median', 'wetness_median', 'nir_contrast_median', 
    'red_contrast_median', 'ratio_median_dry', 'rvi_median_dry', 'ndwi_median_dry', 'awei_median_dry', 'iia_median_dry', 
    'gcvi_median_dry', 'gemi_median_dry', 'cvi_median_dry', 'gli_median_dry', 'shape_median_dry', 'afvi_median_dry', 
    'avi_median_dry', 'bsi_median_dry', 'brba_median_dry', 'dswi5_median_dry', 'lswi_median_dry', 'mbi_median_dry', 
    'ui_median_dry', 'osavi_median_dry', 'ri_median_dry', 'brightness_median_dry', 'wetness_median_dry', 
    'nir_contrast_median_dry', 'red_contrast_median_dry', 'ratio_median_wet', 'rvi_median_wet', 
    'ndwi_median_wet', 'awei_median_wet', 'iia_median_wet', 'gcvi_median_wet', 'gemi_median_wet', 
    'cvi_median_wet', 'gli_median_wet', 'shape_median_wet', 'afvi_median_wet', 'avi_median_wet', 
    'bsi_median_wet', 'brba_median_wet', 'dswi5_median_wet', 'lswi_median_wet', 'mbi_median_wet', 
    'ui_median_wet', 'osavi_median_wet', 'ri_median_wet', 'brightness_median_wet', 'wetness_median_wet', 
    'nir_contrast_median_wet', 'red_contrast_median_wet'
]

bandas_imports = []
for bandInt in bandNames:
    for bndCom in bandasComunsCorr:
        if bandInt == bndCom:
            bandas_imports.append(bandInt)

def correct_listSpectralMaxList(listatmp):
    newlist = []
    for ibnd in listatmp:
        if 'blue' in ibnd and '_1' not in ibnd:
            newlist.append(ibnd + '_1')
        elif 'green' in ibnd and '_1' not in ibnd:
            newlist.append(ibnd + '_1')
        elif 'red' in ibnd and '_1' not in ibnd:
            newlist.append(ibnd + '_1')
        elif 'nir' in ibnd and '_1' not in ibnd:
            newlist.append(ibnd + '_1')
        elif 'swir1' in ibnd and '_1' not in ibnd:
            newlist.append(ibnd + '_1')
        elif 'swir2' in ibnd and '_1' not in ibnd:
            newlist.append(ibnd + '_1')
        else:
            newlist.append(ibnd)

    return newlist



def getPathCSV (nfolder):
    # get dir path of script 
    mpath = os.getcwd()
    # get dir folder before to path scripts 
    pathparent = str(Path(mpath).parents[0])
    # folder of CSVs ROIs
    roisPath = '/dados/' + nfolder
    mpath = pathparent + roisPath
    print("path of CSVs Rois is \n ==>",  mpath)
    return mpath

lstYearsAll = [str(kk) for kk in range(1985, 2023)]
nameBacias = [
    '741','7421','7422','744','745','746','7492','751','752','753',
    '754','755','756','757','758','759','7621','7622','763','764',
    '765','766','767','771','772','773', '7741','7742','775','776',
    '777','778','76111','76116','7612','7614','7615','7616','7617',
    '7618','7619', '7613'
]

def cleaninglstBands (lstFt):
    lstfeatures = []
    for feat in lstFt:
        if '_1' not in feat and '_2' not in feat:
            lstfeatures.append(feat)

    return lstfeatures

pathJson = getPathCSV("regJSON/")
a_file = open(pathJson + "rest_lst_features_selected_bndC8.json", "r")
dictFeatureImp = json.load(a_file)
lstMaxSpectInd = []
dictBa = {}
for kkey, lstFeat in dictFeatureImp.items():
    partes = kkey.split("_")
    bacia = partes[0]
    year = partes[1]
    lstKeyBa = [kk for kk in dictBa.keys()]
    if bacia not in lstKeyBa:
        dictBa[bacia] = [year]
    else:
        lsttmp = dictBa[bacia]
        lsttmp.append(year)
        dictBa[bacia] = lsttmp

    if len(lstFeat) > len(lstMaxSpectInd):
        lstMaxSpectInd = lstFeat
print("size  lstMaxSpectInd ", len(lstMaxSpectInd))
# correguindo todas as bandas com error _1 ==> banda correta
lstMaxSpectInd = correct_listSpectralMaxList(lstMaxSpectInd)
# sys.exit()

for kkey, lstYYear in dictBa.items():
    print(f"bacia {kkey} => {len(lstYYear)}")
    lstBandsMax = []
    for yyear in lstYYear:
        keyBasin = kkey + "_" + str(yyear)
        lstFeatSpace = dictFeatureImp[keyBasin]
        if len(lstFeatSpace) > len(lstBandsMax):
            lstBandsMax = lstFeatSpace
    if len(lstBandsMax) < 150:
        lstBandsMax = copy.deepcopy(lstMaxSpectInd)

    for yyear in lstYYear:
        keyBasin = kkey + "_" + str(yyear)
        lstFeatSpace = dictFeatureImp[keyBasin]

        # research spectrals index that not in lstBandsMax
        for bndSpect in lstBandsMax:
            if bndSpect not in lstFeatSpace:
                lstFeatSpace.append(bndSpect)
        
        # filtrando com a lista maior bandas_imports
        lstSelected = []
        for bndImp in bandas_imports:
            cc = 0
            while cc < len(lstFeatSpace):        
                bndFS = lstFeatSpace[cc]
                if bndImp == bndFS:
                    lstSelected.append(bndImp)
                    cc = 3000
                cc += 1
        print("⛔ ========== Feature Spectral selected =========== ⛔")
        # print(lstresto)
        print(f"===== ✍️ writting {len(lstSelected)} in dict =======")
        # corregindo as bandas do features Space
        dictFeatureImp[keyBasin] = lstSelected






newPathjsonRF = pathJson + "filt_lst_features_selected_spIndC9.json"
with open(newPathjsonRF, 'w') as fp:
    json.dump(dictFeatureImp, fp)
ic(" -- 🔊 filt_lst_features_selected_spIndC9.json saved ")