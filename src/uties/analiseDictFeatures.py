#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
'''

from pathlib import Path
import os
import json
from icecream import ic
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
dictSust = {
    '765': "763", 
    '766': "777", 
    '767': "764", 
    '778': "777", 
    '76111': "758", 
    '76116': "758", 
    '7612': "754", 
    '7614': "754", 
    '7615': '744', 
    '7616': "7617", 
    '7618':"7617", 
    '7619':"744", 
    '7613':"754"
}
def cleaninglstBands (lstFt):
    lstfeatures = []
    for feat in lstFt:
        if '_1' not in feat and '_2' not in feat:
            lstfeatures.append(feat)

    return lstfeatures

pathJson = getPathCSV("regJSON/")
a_file = open(pathJson + "lst_features_selected_bndC8.json", "r")
dictFeatureImp = json.load(a_file)
# print("dict Features ",dictFeatureImp.keys())

dictBa = {}

for kkey, lstFeat in dictFeatureImp.items():
    partes = kkey[1:].split("_")
    bacia = partes[0]
    year = partes[1]
    lstKeyBa = [kk for kk in dictBa.keys()]

    if bacia not in lstKeyBa:
        dictBa[bacia] = [year]
    else:
        lsttmp = dictBa[bacia]
        lsttmp.append(year)
        dictBa[bacia] = lsttmp

newDictFeatImpt = {}    
lstFaltantes = [
    '765', '766', '767', '778', '76111', '76116', 
    '7612', '7614', '7615', '7616', '7618', '7619', '7613'
]
newlstFeat = dictFeatureImp['/741_2022']
# run and clean lstFeatures 
for nbacia in nameBacias:
    try:
        lstYears = dictBa[nbacia]
        print(f"bacia => {nbacia}  <> {len(lstYears)}")
        for nyear in lstYearsAll:
            fKey = '/' + nbacia + '_' + nyear
            if nyear in lstYears:
                lstbndFeat = dictFeatureImp[fKey]
                newlstFeat = cleaninglstBands(lstbndFeat)
                newDictFeatImpt[fKey[1:]] = newlstFeat
            else:
                newDictFeatImpt[fKey[1:]] = newlstFeat
    except:
        lstFaltantes.append(nbacia)
        lstYears = dictBa[dictSust[nbacia]]
        print(f"bacia => {nbacia} sustitui {dictSust[nbacia]} <> {len(lstYears)}")
        for nyear in lstYearsAll:
            fKey = '/' + dictSust[nbacia] + '_' + nyear
            otherKey = nbacia + '_' + nyear
            if nyear in lstYears:
                lstbndFeat = dictFeatureImp[fKey]
                newlstFeat = cleaninglstBands(lstbndFeat)
                newDictFeatImpt[otherKey] = newlstFeat 
            else:
                newDictFeatImpt[otherKey] = newlstFeat
        
print("as Bacias que faltam ", lstFaltantes)
print(f"old dict have  {len(dictFeatureImp.keys())} ")
print(f"The new dict have  {len(newDictFeatImpt.keys())} ")

# for kkey, lstFe in newDictFeatImpt.items():
#     print(f" kkey {kkey} : {lstFe[:10]} ")

newPathjsonRF = pathJson + "rest_lst_features_selected_bndC8.json"
with open(newPathjsonRF, 'w') as fp:
    json.dump(newDictFeatImpt, fp)
ic(" -- rest_lst_features_selected_bndC8.json saved ")