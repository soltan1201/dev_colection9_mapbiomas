#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
# SCRIPT DE CLASSIFICACAO POR BACIA
# Produzido por Geodatin - Dados e Geoinformacao
# DISTRIBUIDO COM GPLv2
'''

import ee 
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

class reformatIds(object):
    sizeFeatColROIs = 0
    def __init__(self, sizeFeatC):
        sizeFeatColROIs = sizeFeatC

    def reformat_Idproperty(self):
        pass


param = {    
    'asset_output': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/roisGradesgroupedBuf',
    'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrograficaCaatbuffer5k',
    'asset_shpGrade': 'projects/mapbiomas-arida/ALERTAS/auxiliar/basegrade30KMCaatinga',
    'assetROIgrade': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/roisGradesgrouped'  
}



#========================METODOS=============================
def GetPolygonsfromFolder():
    dictAsset = {'id': param['assetROIgrade']}
    getlistPtos = ee.data.getList(dictAsset)

    lstidGrades = []
    for idAsset in tqdm(getlistPtos):         
        path_ = idAsset.get('id').split('/')[-1]        
        # gradeROIs_{idGrade}_wl"
        nameGrade = path_.split("_")[1]
        lstidGrades.append(str(nameGrade))

    ic(f"we have in the folder {len(lstidGrades)}")

    return lstidGrades


def getPathCSV():
    # get dir path of script 
    mpath = os.getcwd()
    # get dir folder before to path scripts 
    pathparent = str(Path(mpath).parents[0])
    print("path parents ", pathparent)
    # folder results of CSVs ROIs
    mpath_bndImp = pathparent + '/dados/regJSON/'
    print("path of CSVs Rois is \n ==>",  mpath_bndImp)
    return mpath_bndImp


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


nfolder = 'ROIS_Bacias_Grade'
nameBacias = [
    '7421','7422','745','7492','751','752','753','755','756','757','758','7622','764',
    '765','766','772','773', '7741','7742','775','776','777','76111','76116','7612',
    '7614','7615','7616','7617','7618','7619', '7613','778', '771','767','763','7621',
    '759','754','746','744','741'
]

print("lista de todas as bacias ", nameBacias) 
def removeId_nonDuplicate(dict_search, newlst):
    keysBacia = [kk for kk in dict_search.keys()]
    novalista =  copy.deepcopy(newlst)
    for nb in keysBacia:
        lst_tmp =  dict_search[nb]
        novalista = [item for item in novalista if item not in lst_tmp ]

    return novalista

dict_bacGrade = {}
bacias = ee.FeatureCollection(param['asset_bacias_buffer']);
grades = ee.FeatureCollection(param['asset_shpGrade']);
print(" =======================================================================")
print(" ================ Building the dict key basin and list Grade ===========")
print(" .......................................................................")
for cc, nbacia in enumerate(nameBacias):
    print(f" == {cc} == processing bacia {nbacia} ====== ")
    featBacia = bacias.filter(ee.Filter.eq('nunivotto3', nbacia)).geometry()
    # feature collection com todas as 
    gradesBacia = grades.filterBounds(featBacia);
    lstCodId = gradesBacia.reduceColumns(ee.Reducer.toList(), ['id']).get('list').getInfo()
    print(f"        we have {len(lstCodId)} grades ")

    listaCondsId = removeId_nonDuplicate(dict_bacGrade, lstCodId)
    dict_bacGrade[nbacia] = listaCondsId


# we have know how many grades ROIs have in the folder 
lstAllgradeSaved = GetPolygonsfromFolder()
# sys.exit()
regBaciaDict = {}

cont = 0
for kBac, lstIds in dict_bacGrade.items():
    print(f"# {cont}, bacia => <{kBac}> , we 🫵 have size {len(lstIds)}")
    lstGradetmp = []
    featROIsbasin = ee.FeatureCollection([])
    for cc, idGrade in  enumerate(lstIds):
        addingFeat = False
        for gradeS in lstAllgradeSaved:
            if str(gradeS) == str(idGrade):
                addingFeat= True
                print(f"         --- {idGrade} founded --")

        if addingFeat:
            idAssetnameFeat = param['assetROIgrade'] + f"/gradeROIs_{idGrade}_wl"
            print(f"     {cc} ===> 🚨 loading...  gradeROIs_{idGrade}_wl")
            feattmp = ee.FeatureCollection(idAssetnameFeat)
            # sizefeat = feattmp.size().getInfo()
            # print("         have = ", sizefeat )
            featROIsbasin = featROIsbasin.merge(feattmp)
            lstGradetmp.append(idGrade)
        else:
            print(f" THIS {idGrade} DON´T EXIT IN THE FOLDER ")

    regBaciaDict[kBac] = lstGradetmp
    nameExp = f"bassinG_ROIs_{kBac}_wl"
    processoExportar(featROIsbasin, nameExp, cont)

    cont += 1

pathjsonRF = 'regDictBaciakeyGradelst.json'
with open(pathjsonRF, 'w') as fp:
    json.dump(regBaciaDict, fp)
ic(" -- regDictBaciakeyGradelst.json saved ")