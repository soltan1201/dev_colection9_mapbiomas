#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Produzido por Geodatin - Dados e Geoinformacao
DISTRIBUIDO COM GPLv2
@author: geodatin
"""
import os
import glob 
import sys
import pandas as pd
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


buildingTables = True
modelos = ["GTB","RF"]
nameBacias = [
      '741', '7421','7422','744','745','746','751','752',  # '7492',
      '753', '754','755','756','757','758','759','7621','7622','763',
      '764','765','766','767','771','772','773', '7741','7742','775',
      '776','76111','76116','7612','7613','7614','7615',  # '777','778',
      '7616','7617','7618','7619'
]


def getPathCSV (nfolders):
    # get dir path of script 
    mpath = os.getcwd()
    # get dir folder before to path scripts 
    pathparent = str(Path(mpath).parents[0])
    # folder of CSVs ROIs
    roisPathAcc = pathparent + '/dados/' + nfolders
    return pathparent, roisPathAcc


# accuracy_score
# 
def calculing_metricsAcc (dfTmp, showMatConf):
    if showMatConf:
        conf_matrix = confusion_matrix(dfTmp['reference'], dfTmp['classification'])
        print(conf_matrix)   
    precision = precision_score(dfTmp['reference'], dfTmp['classification'], average='macro')
    reCall = recall_score(dfTmp['reference'], dfTmp['classification'], average='macro')
    f1Score = f1_score(dfTmp['reference'], dfTmp['classification'], average='macro')
    acc = accuracy_score(dfTmp['reference'], dfTmp['classification'])
    accbal = balanced_accuracy_score(dfTmp['reference'], dfTmp['classification'])
    jaccard = jaccard_score(dfTmp['reference'], dfTmp['classification'], average='macro')

    if showMatConf:
        print("  uniques values references ", dfTmp['reference'].unique())
        print(" uniques values predictions ", dfTmp['classification'].unique())
        print("Acuracia ", acc)
        print("Acuracia balance", accbal)
        print("precision ", precision)
        print("reCall ", reCall)
        print("f1 Score ", f1Score)
        print("Jaccard ", jaccard)

    return acc, accbal, precision, reCall, f1Score, jaccard


def calculing_metrics_AccBacia(row):  
    vers = row['version']
    model = row['Models']
    nbacia = row['Bacia']
    yyear = row['Years']
    colRef = "CLASS_" + str(yyear)
    colPre = "classification_" + str(yyear)

    df_tmpV = dfacc[dfacc['bacia'] == int(nbacia)]  # (dfacc['version'] == vers) & 
    print("df_tmpV ", df_tmpV.shape)
    print("dfacc ", dfacc.shape)
    print(dfacc[['version','models','bacia']].head())
    print(df_tmpV['models'].value_counts())
    print("bacia ", nbacia)

    df_tmp = dfacc[(dfacc['version'] == vers) & (dfacc['models'] == model) & (
                                            dfacc['bacia'] == str(nbacia))][[colRef, colPre]]           

    df_tmp.columns = ['reference', 'classification']
    if showPrints:        
        print("dataframe filtrada ", df_tmp.head())
    
    Acc, AccBal, precis, recall, f1score, jaccardS = calculing_metricsAcc (df_tmp, True)
    row["Accuracy"] = Acc
    row["Accuracy_Bal"] = AccBal
    row["Precision"] = precis
    row["ReCall"] = recall
    row["F1-Score"] = f1score
    row["Jaccard"] = jaccardS
    # sys.exit()
    return row

def calculing_metrics_AccYear(row):  
    vers = row['version']
    model = row['Models']
    yyear = row['Years']
    colRef = "CLASS_" + str(yyear)
    colPre = "classification_" + str(yyear)
    df_tmp = dfacc[(dfacc['version'] == vers) & (dfacc['models'] == model)][[colRef, colPre]]           

    df_tmp.columns = ['reference', 'classification']
    if showPrints:        
        print(df_tmp.head())
    Acc, AccBal, precis, recall, f1score, jaccardS = calculing_metricsAcc (df_tmp, False)
    row["Accuracy"] = Acc
    row["Accuracy_Bal"] = AccBal
    row["Precision"] = precis
    row["ReCall"] = recall
    row["F1-Score"] = f1score
    row["Jaccard"] = jaccardS

    return row

base_path, input_path_CSVs = getPathCSV('acc/ptosAccCol9/')
print("path the base ", base_path)
print("path of CSVs from folder ", input_path_CSVs)

lstRef = ['CLASS_' + str(kk) for kk in range(1985, 2023)]
lstPred = ['classification_' + str(kk) for kk in range(1985, 2023)]
lYears = [kk for kk in range(1985, 2023)]

lst_paths = glob.glob(input_path_CSVs + '/*')
classificador = "GTB"
lst_df = []
for path in lst_paths[:]:       
    partes = path.split('_')
    classificador = partes[-3]
    bacia = partes[-4]
    version = partes[-2]
    namecol = path.split("/")[-1]
    print(f"collection = <{namecol}> | model << {classificador} >> | bacia << {bacia} >> | vers {version}" )
    df_CSV = pd.read_csv(path)
    df_CSV = df_CSV.drop(['system:index', ".geo"], axis=1)
    print("size table = ", df_CSV.shape)

    df_CSV['bacia'] = [str(bacia)] * df_CSV.shape[0]
    df_CSV['models'] = [classificador] * df_CSV.shape[0]
    df_CSV['version'] = [version] * df_CSV.shape[0]
    # print(df_CSV[['bacia','models','CLASS_1999','classification_1999']].head(2))
    # add to list ofs Dataframes 
    lst_df.append(df_CSV)

dfacc = pd.concat(lst_df, axis= 0)
print("size dataframe modifies ", dfacc.shape)
print("colunas \n ", dfacc.columns)
print("=================================================")
print(dfacc.head(10))
print("=================================================")
# sys.exit()
showPrints = True
classInic = [3,4, 9,10,12,15,18,22,27,29,33]
classFin  = [3,4,12,12,12,15,18,22,27,22,33]
# concat_df['class'] = concat_df['class'].replace([0,1,2,3,4],[0,1,0,0,1])
# Remap column values in inplace
for cc, colRef in enumerate(lstRef):
    dfacc[colRef] = dfacc[colRef].replace(classInic, classFin) 
    dfacc = dfacc[dfacc[colRef] != 27]
    if showPrints:
        print("==> ", cc + 1, " uniques values references ", dfacc[colRef].unique())
        print("        uniques values predictions ", dfacc[lstPred[cc]].unique())
        print(dfacc[colRef].value_counts())

# sys.exit()
# Make Dataframe by Year and by Basin
lstmodels = []
lstVersion = []
lstBacias = []
lstYear = []
for vers in ['5']:
    for nmodel in modelos:
        lstVersion += [vers] * len(nameBacias) * len(lYears)
        lstmodels += [nmodel] * len(nameBacias) * len(lYears)        
        for nbacia in nameBacias:
            lstBacias += [nbacia] * len(lYears)
            lstYear += lYears

print("Adding metrics Acc in the dictionary by Year")
dictAcc = {
    "version": lstVersion,
    "Models": lstmodels,
    "Bacia" : lstBacias,    
    "Years": lstYear    
}
dfAccYYBa = pd.DataFrame.from_dict(dictAcc)
print("size data frame by bacia", dfAccYYBa.shape)
print("modelos ", dfAccYYBa["Models"].unique())
print(dfAccYYBa.head())


# Make Dataframe by Year
lstmodels = []
lstVersion = []
lstYear = []
for vers in ['5']:
    for model in modelos:
        lstVersion += [vers] * len(lYears) 
        lstmodels += [model] * len(lYears)       
        lstYear += lYears

print("Adding metrics Acc in the dictionary by Year")
dictAcc = {    
    "Models": lstmodels,
    "version": lstVersion,
    "Years": lstYear
}
dfAccYY = pd.DataFrame.from_dict(dictAcc)
print("size data frame by Year", dfAccYY.shape)
print("modelos ", dfAccYY["Models"].unique())
print(dfAccYY.head())

dfAccYYBa = dfAccYYBa.progress_apply(calculing_metrics_AccBacia, axis= 1)
print("show the first row from table dfAccYYBa")
print(dfAccYYBa.head())
print("the size table is ", dfAccYYBa.shape)


dfAccYY = dfAccYY.progress_apply(calculing_metrics_AccYear, axis= 1)
print("show the first row from table dfAccYY")
print(dfAccYYBa.head())
print("the size table is ", dfAccYYBa.shape)

pathOutpout = base_path + '/dados/accTables/'
nameTablesGlob = "regMetricsAccGlobalCol9.csv"        
nameTablesbacias = "regMetricsAccBaciasCol9.csv"
print("====== SAVING GLOBAL ACCURACY BY YEARS =========== ")
dfAccYY.to_csv(pathOutpout + nameTablesGlob)
print("====== SAVING Basin ACCURACY BY YEARS =========== ")
dfAccYYBa.to_csv(pathOutpout + nameTablesbacias)
print("************************************************")