#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
# https://code.earthengine.google.com/0c432999045898bb6e40c1fb7238d32f
'''

import ee
import os 
import gee
import json
import csv
import copy
import sys
import math
import arqParametros as arqParams 
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

param = {      
    'output_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Spatial/',
    # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/Frequency/',
    # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Temporal/',
    'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Gap-fill/',
    # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/Spatial/',
    'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrograficaCaatbuffer5k',            
    'last_year' : 2023,
    'first_year': 1985,
    # 'versionTP' : '9',
    # 'versionSP' : '7',
    'versionGP' : 9,
    'numeroTask': 6,
    'numeroLimit': 42,
    'conta' : {
        '0': 'caatinga01',
        '7': 'caatinga02',
        '14': 'caatinga03',
        '21': 'caatinga04',
        '28': 'caatinga05',        
        '35': 'solkan1201',     
    }
}
lst_bands_years = ['classification_' + str(yy) for yy in range(param['first_year'], param['last_year'] + 1)]

def buildingLayerconnectado(imgClasse):
    lst_band_conn = ['classification_' + str(yy) + '_conn' for yy in range(param['first_year'], param['last_year'] + 1)]
    # / add connected pixels bands
    imageFilledConnected = imgClasse.addBands(
                                imgClasse.connectedPixelCount(10, True).rename(lst_band_conn))

    return imageFilledConnected


def apply_spatialFilterConn (name_bacia):
    min_connect_pixel = 6
    geomBacia = ee.FeatureCollection(param['asset_bacias_buffer']).filter(
                ee.Filter.eq('nunivotto3', name_bacia)).first().geometry()

    # name_imgClass = 'filterTP_BACIA_'+ name_bacia  + "_V" + param['versionTP']
    name_imgClass = 'filterGF_BACIA_'+ name_bacia  + "_V" + str(param['versionGP'])
    # name_imgClass = 'filterSP_BACIA_'+ name_bacia  + "_V" + param['versionTP']

    imgClass = ee.Image(param['input_asset'] + name_imgClass)#.clip(geomBacia) 
    numBands = len(imgClass.bandNames().getInfo())

    if numBands <= 38:
        imgClass = buildingLayerconnectado(imgClass)

    for cc, yband_name in enumerate(lst_bands_years[:]):
        moda_kernel = imgClass.select(yband_name).focal_mode(1, 'square', 'pixels')
        moda_kernel = moda_kernel.updateMask(imgClass.select(yband_name+'_conn').lte(min_connect_pixel))

        if cc == 0:
            class_output = imgClass.select(yband_name).blend(moda_kernel)
        else:
            class_tmp = imgClass.select(yband_name).blend(moda_kernel)
            class_output = class_output.addBands(class_tmp)
    
    nameExp = 'filterSP_BACIA_'+ str(name_bacia) + "_V" + str(param['versionGP'])

    # class_output = class_output.set('version', param['versionSP'])
    class_output = class_output.clip(geomBacia).set(
                        'version', param['versionGP'], 'biome', 'CAATINGA',
                        'collection', '8.0', 'id_bacia', name_bacia,
                        'sensor', 'Landsat', 'source','geodatin',
                        'system:footprint', geomBacia# imgClass.get('system:footprint')
                    )
    processoExportar(class_output,  nameExp, geomBacia)

#exporta a imagem classificada para o asset
def processoExportar(mapaRF,  nomeDesc, geom_bacia):
    
    idasset =  param['output_asset'] + nomeDesc
    optExp = {
        'image': mapaRF, 
        'description': nomeDesc, 
        'assetId':idasset, 
        'region': geom_bacia.getInfo()['coordinates'],
        'scale': 30, 
        'maxPixels': 1e13,
        "pyramidingPolicy":{".default": "mode"}
    }
    task = ee.batch.Export.image.toAsset(**optExp)
    task.start() 
    print("salvando ... " + nomeDesc + "..!")
    # print(task.status())
    for keys, vals in dict(task.status()).items():
        print ( "  {} : {}".format(keys, vals))



#============================================================
#========================METODOS=============================
#============================================================
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
        cont = 0
    
    cont += 1    
    return cont


listaNameBacias = [
    '741','7421','7422','744','745','746','7492', '751', 
    '752', '753','755','758','759','7621','7622','763','764','765',
    '766','767','771','773', '778','76111','76116',
    '7612','7614','7615','7616','7617','7618','7619', '7613',
    '754','756','757','772','7741','776','7742','775','777',
]
changeAcount = False
lstqFalta =  []
cont = 0
input_asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Gap-fill/'
# input_asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Spatial/'
if changeAcount:
    cont = gerenciador(cont)
version = 9
listBacFalta = []
knowMapSaved = False
for cc, idbacia in enumerate(listaNameBacias[:]):   
    if knowMapSaved:
        try:
            nameMap = 'filterGF_BACIA_'+ str(idbacia) + "_V" + str(version)
            # nameMap = 'filterSP_BACIA_'+ str(idbacia) + "_V" + str(version)
            print(nameMap)
            imgtmp = ee.Image(input_asset + nameMap)
            print(f" {cc} loading ", nameMap, " ", len(imgtmp.bandNames().getInfo()), "bandas ")
        except:
            listBacFalta.append(idbacia)
    else: 
        if idbacia not in lstqFalta:            
            print("----- PROCESSING BACIA {} -------".format(idbacia))        
            apply_spatialFilterConn(idbacia)
            cont = gerenciador(cont)


if knowMapSaved:
    print("lista de bacias que faltam \n ",listBacFalta)
    print("total ", len(listBacFalta))