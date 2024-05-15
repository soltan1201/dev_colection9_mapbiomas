#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Produzido por Geodatin - Dados e Geoinformação
DISTRIBUIDO COM GPLv2
@author: geodatin
"""
import os
import glob 
import sys
import math
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
from sklearn import metrics
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import precision_score, recall_score
# from sklearn.metrics import 
from sklearn.metrics import f1_score, jaccard_score
tqdm.pandas()


nameBacias = [
      '741', '7421','7422','744','745','746','751','752',  # '7492',
      '753', '754','755','756','757','758','759','7621','7622','763',
      '764','765','766','767','771','772','773', '7741','7742','775',
      '776','76111','76116','7612','7613','7614','7615',  # '777','778',
      '7616','7617','7618','7619'
]
modelos = ['GTB','RF']
posclass = ['Gap-fill', 'Spatial', 'Temporal', 'toExport']
modelos += posclass
# get dir path of script 
npath = os.getcwd()
# get dir folder before to path scripts 
npath = str(Path(npath).parents[1])
print("path of CSVs Rois is \n ==>",  npath)
pathcsvsMC = os.path.join(npath,'dados')
pathcsvsMC = os.path.join(pathcsvsMC, 'conf_matrix')

lstfilesCSVs = glob.glob(pathcsvsMC + '/*.csv')
for model in modelos:
    lstDF_models = []
    for cc, pathfile in enumerate(lstfilesCSVs):        
        if model in pathfile:
            
            namefile = pathfile.split("/")[-1]
            partes = namefile.split("_")
            nbacia = partes[1]
            yyear = partes[-2]
            version = partes[-1].replace('.csv', '')
            if model in ['GTB','RF'] and len(partes) == 5:
                print(f"file {cc} | model {model} | year {yyear} | pathfile {pathfile.split("/")[-1]}")
                dftmp = pd.read_csv(pathfile)
            else:
                print(f"file {cc} | m POS- CLASS {model} | year {yyear} | pathfile {pathfile.split("/")[-1]}")
                dftmp = pd.read_csv(pathfile)
            dftmp['bacia'] = [nbacia] * dftmp.shape[0]
            dftmp['model'] = [model] * dftmp.shape[0]
            dftmp['version'] = [version] * dftmp.shape[0]
            dftmp['year'] = [yyear] * dftmp.shape[0]
            print(dftmp)
            lstDF_models.append(dftmp)

    nametable = 'Matrices_Confusion_model_' + model + '.csv'
    dfModels = pd.concat(lstDF_models, axis=0, ignore_index=True)
    pathExp = npath + '/dados/globalTables/' + nametable
    dfModels.to_csv(pathExp)
    print(f" we save the table {nametable} with {dfModels.shape} shapes")