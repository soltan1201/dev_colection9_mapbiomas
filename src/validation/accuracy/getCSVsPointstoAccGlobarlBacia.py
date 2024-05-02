#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
'''

import ee 
import gee
import json
import csv
import sys
import collections
collections.Callable = collections.abc.Callable
try:
    ee.Initialize()
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


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

cont = 0
# cont = gerenciador(cont, param)


#exporta a imagem classificada para o asset
def processoExportar(ROIsFeat, nameT, porAsset):  

    if porAsset:
        optExp = {
          'collection': ROIsFeat, 
          'description': nameT, 
          'assetId':"users/mapbiomascaatinga04/" + nameT          
        }
        task = ee.batch.Export.table.toAsset(**optExp)
        task.start() 
        print("salvando ... " + nameT + "..!")
    else:
        optExp = {
            'collection': ROIsFeat, 
            'description': nameT, 
            'folder':"ptosAccCol9"          
            }
        task = ee.batch.Export.table.toDrive(**optExp)
        task.start() 
        print("salvando ... " + nameT + "..!")
        # print(task.status())
    


#nome das bacias que fazem parte do bioma
nameBacias = [
      '741', '7421','7422','744','745','746','751','752',  # '7492',
      '753', '754','755','756','757','758','759','7621','7622','763',
      '764','765','766','767','771','772','773', '7741','7742','775',
      '776','76111','76116','7612','7613','7614','7615',  # '777','778',
      '7616','7617','7618','7619'
] 

param = {
    'lsBiomas': ['CAATINGA'],
    'asset_bacias': 'projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga',
    'assetBiomas' : 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil',
    'assetpointLapig': 'projects/mapbiomas-workspace/VALIDACAO/mapbiomas_85k_col3_points_w_edge_and_edited_v2',    
    'limit_bacias': "users/CartasSol/shapes/bacias_limit",
    'assetCol': "projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVP" ,
    'asset_Map' : "projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1",
    # 'assetCol6': path_asset + "class_filtered/maps_caat_col6_v2_4",
    'classMapB': [3, 4, 5, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45],
    'classNew': [3, 4, 3, 3,12,12,21,21,21,21,21,22,22,22,22,33,29,22,33,12,33, 21,33,33,21,21,21,21,21,21,21],
    'inBacia': True,
    'pts_remap' : {
        "FORMAÇÃO FLORESTAL": 3,
        "FORMAÇÃO SAVÂNICA": 4,        
        "MANGUE": 3,
        "RESTINGA HERBÁCEA": 3,
        "FLORESTA PLANTADA": 18,
        "FLORESTA INUNDÁVEL": 3,
        "CAMPO ALAGADO E ÁREA PANTANOSA": 12,
        "APICUM": 12,
        "FORMAÇÃO CAMPESTRE": 12,
        "AFLORAMENTO ROCHOSO": 29,
        "OUTRA FORMAÇÃO NÃO FLORESTAL":12,
        "PASTAGEM": 15,
        "CANA": 18,
        "LAVOURA TEMPORÁRIA": 18,
        "LAVOURA PERENE": 18,
        "MINERAÇÃO": 22,
        "PRAIA E DUNA": 22,
        "INFRAESTRUTURA URBANA": 22,
        "VEGETAÇÃO URBANA": 22,
        "OUTRA ÁREA NÃO VEGETADA": 22,
        "RIO, LAGO E OCEANO": 33,
        "AQUICULTURA": 33,
        "NÃO OBSERVADO": 27  
    },
    'anoInicial': 1985,
    'anoFinal': 2022,  # 2019
    'numeroTask': 6,
    'numeroLimit': 2,
    'conta' : {
        '0': 'caatinga04'              
    },
    'lsProp': ['ESTADO','LON','LAT','PESO_AMOS','PROB_AMOS','REGIAO','TARGET_FID','UF'],
    "amostrarImg": False,
    'isImgCol': False
}

def change_value_class(feat):
    ## Load dictionary of class
    dictRemap =  {
        "FORMAÇÃO FLORESTAL": 3,
        "FORMAÇÃO SAVÂNICA": 4,        
        "MANGUE": 3,
        "RESTINGA HERBÁCEA": 3,
        "FLORESTA PLANTADA": 18,
        "FLORESTA INUNDÁVEL": 3,
        "CAMPO ALAGADO E ÁREA PANTANOSA": 12,
        "APICUM": 12,
        "FORMAÇÃO CAMPESTRE": 12,
        "AFLORAMENTO ROCHOSO": 29,
        "OUTRA FORMAÇÃO NÃO FLORESTAL":12,
        "PASTAGEM": 15,
        "CANA": 18,
        "LAVOURA TEMPORÁRIA": 18,
        "LAVOURA PERENE": 18,
        "MINERAÇÃO": 22,
        "PRAIA E DUNA": 22,
        "INFRAESTRUTURA URBANA": 22,
        "VEGETAÇÃO URBANA": 22,
        "OUTRA ÁREA NÃO VEGETADA": 22,
        "RIO, LAGO E OCEANO": 33,
        "AQUICULTURA": 33,
        "NÃO OBSERVADO": 27  
    }
    pts_remap = ee.Dictionary(dictRemap) 

    prop_select = [
        'BIOMA', 'CARTA','DECLIVIDAD','ESTADO','JOIN_ID','PESO_AMOS'
        ,'POINTEDITE','PROB_AMOS','REGIAO','TARGET_FID','UF', 'LON', 'LAT']
    
    feat_tmp = feat.select(prop_select)
    for year in range(1985, 2023):
        nam_class = "CLASS_" + str(year)
        set_class = "CLASS_" + str(year)
        valor_class = ee.String(feat.get(nam_class))
        feat_tmp = feat_tmp.set(set_class, pts_remap.get(valor_class))
    
    return feat_tmp


def getPointsAccuraciaFromIC (imClass, isImgCBa, ptosAccCorreg, modelo, version, exportByBasin, exportarAsset):

    #lista de anos
    list_anos = [str(k) for k in range(param['anoInicial'], param['anoFinal'] + 1)]
    print('lista de anos', list_anos)
    # update properties 
    lsAllprop = param['lsProp'].copy()
    for ano in list_anos:
        band = 'CLASS_' + str(ano)
        lsAllprop.append(band)
    # featureCollection to export colected 
    pointAll = ee.FeatureCollection([])

    ftcol_bacias = ee.FeatureCollection(param['asset_bacias'])

    sizeFC = 0
    for cc, _nbacia in enumerate(nameBacias[:]):    
        nameImg = 'mapbiomas_collection90_Bacia_v5' 
        print("processando img == " + nameImg + " em bacia *** " + _nbacia)
        baciaTemp = ftcol_bacias.filter(ee.Filter.eq('nunivotto3', _nbacia)).geometry()    

        pointTrueTemp = ptosAccCorreg.filterBounds(baciaTemp)
        ptoSize = pointTrueTemp.size().getInfo()
        print(cc, " - ", _nbacia, " pointTrueTemp ", ptoSize)  
        sizeFC += ptoSize
    
        if isImgCBa:
            mapClassBacia = ee.Image(imClass.filter(ee.Filter.eq('id_bacia', _nbacia)).first())
        else:
            mapClassBacia = ee.Image(imClass)
        
        pointAccTemp = mapClassBacia.sampleRegions(
            collection= pointTrueTemp, 
            properties= lsAllprop, 
            scale= 30, 
            tileScale= 1, 
            geometries= True
        )
        pointAccTemp = pointAccTemp.map(lambda Feat: Feat.set('bacia', _nbacia))
        if exportByBasin:
            if modelo != '':
                name = 'occTab_corr_Caatinga_' + _nbacia + "_" + modelo + "_" + str(version) + "_Col9" 
            else:
                name = 'occTab_corr_Caatinga_' + _nbacia + "_" + str(version) + "_Col9" 
            processoExportar(pointAccTemp, name, exportarAsset)
        else:
            pointAll = ee.Algorithms.If(  
                        ee.Algorithms.IsEqual(ee.Number(ptoSize).eq(0), 1),
                        pointAll,
                        ee.FeatureCollection(pointAll).merge(pointAccTemp)
                    )
    if not exportByBasin:
        if modelo != '':
            name = 'occTab_corr_Caatinga_Col9_' + modelo + "_" + str(version) + "_Col9" 
        else:
            name = 'occTab_corr_Caatinga_Col9_' + str(version) + "_Col9" 
        processoExportar(pointAll, name, exportarAsset)
        print()
        print("numero de ptos ", sizeFC)


expPointLapig = False
knowImgcolg = True
param['isImgCol'] = True
param['inBacia'] = True
version = 7
bioma250mil = ee.FeatureCollection(param['assetBiomas'])\
                    .filter(ee.Filter.eq('Bioma', 'Caatinga')).geometry()
## os pontos só serão aqueles que representam a Caatinga 
ptsTrue = ee.FeatureCollection(param['assetpointLapig']).filterBounds(bioma250mil)
pointTrue = ptsTrue.map(lambda feat: change_value_class(feat))
print("Carregamos {} points ".format(9738))  # pointTrue.size().getInfo()
print("know the first points ", pointTrue.first().getInfo())
# print(pointTrue.aggregate_histogram('CLASS_2020').getInfo())
# lsNameClass = [kk for kk in param['pts_remap'].keys()]
# lsValClass = [kk for kk in param['pts_remap'].values()]

if expPointLapig:
    processoExportar(ptsTrue, param['assetpointLapig'].split("/")[-1], False)
    processoExportar(pointTrue, param['assetpointLapig'].split("/")[-1] + '_reclass', False)
    
# sys.exit()


########################################################
#   porBacia -----  Image
#              |--  ImageCollection -> min() -> Image
#   porBioma -----  Image
#              |--  ImageCollection -> min() -> Image
#######################################################

if param['isImgCol']:
    mapClass = ee.ImageCollection(param['assetCol'])
    getid_bacia = mapClass.first().get('id_bacia').getInfo()
    print(f"we load bacia {getid_bacia}")
    
    if knowImgcolg:
        print(f"versions quantity = {mapClass.aggregate_histogram('version').getInfo()}")
    if getid_bacia:         
        nameBands = 'classification'
        prefixo = ""
        for model in ['GTB']:   # ,'RF'
            mapClassYYMod = mapClass.filter(
                                ee.Filter.eq('version', version)).filter(
                                    ee.Filter.eq('classifier', model))
            print(f"########## 🔊 FILTERED BY VERSAO {version} AND MODEL {model} 🔊 ###############") 
            print(" 🚨 número de mapas bacias ", mapClassYYMod.size().getInfo()) 
            # sys.exit()               
            # getPointsAccuraciaFromIC (imClass, isImgCBa, ptosAccCorreg, modelo, version, exportByBasin, exportarAsset)
            getPointsAccuraciaFromIC (mapClassYYMod, True, pointTrue, model, version, True, False)

    else:
        print(f"########## 🔊 FILTERED BY VERSAO {version} 🔊 ###############")              
        mapClassYY = mapClass.filter(ee.Filter.eq('version', version))
        print(" 🚨 número de mapas bacias ", mapClass.size().getInfo())
        immapClassYY = ee.Image().byte()
        for yy in range(1985, 2023):
            nmIm = 'CAATINGA-' + str(yy) + '-' + str(version)
            imTmp = mapClassYY.filter(ee.Filter.eq('system:index', nmIm)).first().rename("classification_" + str(yy))
            if yy == 1985:
                immapClassYY = imTmp.byte()
            else:
                immapClassYY = immapClassYY.addBands(imTmp.byte())
        ## imageCollection converted in image Maps
        ### call to function samples  #######
        getPointsAccuraciaFromIC (immapClassYY, False, pointTrue, '', '', True, False)

else:
    print("########## 🔊 LOADING MAP RASTER ###############")
    mapClassRaster = ee.Image(param['assetCol']).byte()
    ### call to function samples  #######
    getPointsAccuraciaFromIC (mapClassRaster, False, pointTrue, '', '', True, False)

