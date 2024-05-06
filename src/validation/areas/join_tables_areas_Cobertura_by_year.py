#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Produzido por Geodatin - Dados e Geoinformação
DISTRIBUIDO COM GPLv2
@author: geodatin
"""
import sys
import os 
import glob
import copy
import pandas as pd
from pathlib import Path
from tqdm import tqdm
tqdm.pandas()

def getPathCSV (nfolders):
    # get dir path of script 
    mpath = os.getcwd()
    # get dir folder before to path scripts 
    pathparent = str(Path(mpath).parents[1])
    # folder of CSVs ROIs
    roisPathAcc = pathparent + '/dados/' + nfolders
    return pathparent, roisPathAcc



classes = [3,4,12,15,18,21,22,29,33] # 
columnsInt = [
    'Forest Formation', 'Savanna Formation', 'Grassland', 'Pasture',
    'Agriculture', 'Mosaic of Uses', 'Non vegetated area', 'Rocky Outcrop', 'Water'
] # 
colors = [ 
    "#1f8d49", "#7dc975", "#d6bc74", "#edde8e", "#f5b3c8", 
    "#ffefc3", "#db4d4f",  "#FF8C00", "#0000FF"
] # 
# bacia_sel = '741'

dict_class = {
    '3': 'Forest Formation', 
    '4': 'Savanna Formation', 
    '12': 'Grassland', 
    '15': 'Pasture', 
    '18': 'Agriculture', 
    '21': 'Mosaic of Uses', 
    '22': 'Non vegetated area', 
    '29': 'Rocky Outcrop', 
    '33': 'Water'
}

dict_classNat = {
    '3': 'Natural', 
    '4': 'Natural', 
    '12': 'Natural', 
    '15': 'Antrópico', 
    '18': 'Antrópico', 
    '21': 'Antrópico', 
    '22': 'Antrópico', 
    '29': 'Natural', 
    '33': 'Natural'
}
dict_ColorNat = {
    'Natural': '#32a65e',
    'Antrópico': '#FFFFB2',
}
dict_colors = {}
for ii, cclass in enumerate(classes):
    dict_colors[dict_class[str(cclass)]] = colors[ii]
dict_colors['Natural'] = '#32a65e'
dict_colors['Antrópico'] = '#FFFFB2'
dict_colors['cobertura'] = '#FFFFFF'

def set_columncobertura(nrow):
    nclasse = nrow['classe']
    nrow['cobertura'] = dict_class[str(nclasse)]
    nrow['cob_level1'] = dict_classNat[str(nclasse)]
    nrow['cob_color'] = dict_colors[dict_class[str(nclasse)]]
    nrow['nat_color'] = dict_ColorNat[dict_classNat[str(nclasse)]]
    nrow['total'] = 'cobertura'
    return nrow



base_path, input_path_CSVs = getPathCSV('areaBacia')
print("path the base ", base_path)
print("path of CSVs from folder :  \n ==> ", input_path_CSVs)

# sys.exit()
showlstGerral = True
filesAreaCSV = glob.glob(input_path_CSVs + '/*.csv')
print("==================================================================================")
print("========== LISTA DE CSVs  NO FOLDER areasPrioritCSV ==============================")

if showlstGerral:
    for cc, namFile in enumerate(filesAreaCSV):
        print(f" #{cc}  >>  {namFile.split("/")[-1]}")
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print("==================================================================================")

lstDF = []
for pathLayerA in filesAreaCSV:
    nameFiles = pathLayerA.split("/")[-1]
    partes = nameFiles.replace("areaXclasse_CAATINGA_Col9.0_", "").split("_")
    name_model = partes[0]
    version = partes[2]
    nbacia = partes[-1].replace(".csv", "")
    print(f" ====== loading {nameFiles} ========") 
    dftmp = pd.read_csv(pathLayerA)
    dftmp = dftmp.drop(['system:index', '.geo'], axis='columns')
    dftmp["Models"] = name_model
    dftmp["Bacia"] = nbacia
    dftmp["version"] = version
    # print(dftmp.head(10))

    lstDF.append(dftmp)


ndfArea = pd.concat(lstDF, ignore_index= True)
print("columna ", ndfArea.columns)
# ndfArea = ndfArea.sort_values(by='year')
print(f" === 📲 We have now <<{ndfArea.shape[0]}>> row in the DataFrame Area ===")
print(ndfArea.head())
# get values uniques 
lstVers = [kk for kk in ndfArea['version'].unique()]
lstModels = [kk for kk in ndfArea['Models'].unique()]
lstClasses = [kk for kk in ndfArea['classe'].unique()]
lstYears = [kk for kk in ndfArea['year'].unique()]

# def get_Values_Areas()
lstInt = ['version','Models','year','classe','area']
dfTest = ndfArea[lstInt].groupby(['version','Models','year','classe'], as_index= False).agg('sum')
dfTest['Bacia'] = ['Caatinga'] * dfTest.shape[0]
print(" size dfTest ", dfTest.shape)
print(dfTest.head(10))

ndfAllArea = pd.concat([ndfArea, dfTest], ignore_index= True)

ndfAllArea = ndfAllArea.progress_apply(set_columncobertura, axis= 1)

print(" size dfAreaBiome = ", ndfAllArea.shape)
print(ndfAllArea.head())

nameexport = "/dados/globalTables/areaXclasse_CAATINGA_Col9.0.csv"
print("we going to export with name => ", nameexport)
ndfAllArea.to_csv(base_path + nameexport)
print(" -------- DONE ! --------------")
print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
print("==================================================================================")
