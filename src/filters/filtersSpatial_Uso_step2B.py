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
    'output_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/SpatialV3/',
    # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/FrequencyV3',
    'input_assetT': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/TemporalV3',
    'input_assetExp': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/toExport',
    # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Gap-fillV2/',
    'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/SpatialV3',
    'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrograficaCaatbuffer5k',            
    'last_year' : 2023,
    'first_year': 1985,
    'janela': 5,
    'step': 1,
    'versionOut' : 24,
    'versionInp' : 23,
    'numeroTask': 6,
    'numeroLimit': 42,
    'conta' : {
        '0': 'caatinga01',   # 
        '2': 'caatinga02',
        '4': 'caatinga03',
        '6': 'caatinga04',
        '8': 'caatinga05',        
        '10': 'solkan1201',    
        '12': 'solkanGeodatin',
        '14': 'diegoUEFS',
        '16': 'superconta'   
    }
}
lst_bands_years = ['classification_' + str(yy) for yy in range(param['first_year'], param['last_year'] + 1)]
# print("lst_bands_years " , lst_bands_years[:26])   ano 2010
def apply_spatialFilterConn (name_bacia, nmodel):
    # classe_uso = 21
    classe_nat = 4
    frequencyNat = False
    geomBacia = ee.FeatureCollection(param['asset_bacias_buffer']).filter(
                                ee.Filter.eq('nunivotto3', name_bacia)).first().geometry()

    if 'Temporal' in param['input_asset']:
        name_imgClass = 'filterTP_BACIA_'+ name_bacia + f"_GTB_J{param['janela']}_V" + str(param['versionInp'])
    else:
        name_imgClass = 'filterSPU_BACIA_'+ name_bacia + "_GTB_V" + str(param['versionInp'])
    print('   => ', name_imgClass)
    imgClassExp = ee.Image(param['input_asset'] + "/" + name_imgClass)#.clip(geomBacia)  'filter', 'spatial_use'
    print("image Class ", imgClassExp.get('system:index').getInfo())
    if frequencyNat:
        print("carregando frequency Natural ")
        frecuencia = 'frequence'
    else:
        frecuencia = 'frequence_natUso'

    imgClass = ee.ImageCollection(param['input_assetExp']).filter(
                            ee.Filter.eq('version', param['versionInp'] - 1)).filter(
                                # ee.Filter.eq('janela', param['janela'])).filter(
                                    # ee.Filter.eq('filter', 'spatial_use')).filter(
                                        ee.Filter.eq('id_bacia', name_bacia )).first()
    # print(imgClass.size().getInfo())
    print('  show metadata imgClass', imgClass.get('system:index').getInfo())
    # print(imgClass.aggregate_histogram('system:index').getInfo())
    # sys.exit()   

    for cc, yband_name in enumerate(lst_bands_years[:]):
        if cc == 0:
            # print(f"adding {yband_name}  band")
            class_output = imgClass.select(yband_name)
            
        elif cc < 27:  # ano 2010  
            print(f"adding {yband_name}  band")          
            class_output = class_output.addBands(imgClass.select(yband_name))
        else:
            yband_before = lst_bands_years[cc - 1]            
            if yband_name == 'classification_2023': 
                print("run 2023")                
                change_uso_YY = imgClass.select(yband_before).eq(classe_nat).subtract(
                                    imgClassExp.select(yband_name).eq(classe_nat))
                
                mask_Uso_kernel = change_uso_YY.eq(1).focalMin(2).focalMax(4)
                maskPixelsRem = change_uso_YY.updateMask(mask_Uso_kernel.eq(0))
                class_tmp = imgClassExp.select(yband_name).where(maskPixelsRem.eq(1), classe_nat)
                
                # class_output = class_output.addBands(class_tmp.rename(yband_name))
                # sys.exit()
            else:        
                print(f"adding {yband_name}  band") 
                change_uso_YY = class_output.select(yband_before).eq(classe_nat).subtract(
                                imgClass.select(yband_name).eq(classe_nat))
            
                mask_Uso_kernel = change_uso_YY.eq(1).focalMin(2).focalMax(4)
                maskPixelsRem = change_uso_YY.updateMask(mask_Uso_kernel.eq(0))
                class_tmp = imgClass.select(yband_name).where(maskPixelsRem.eq(1), classe_nat)

            class_output = class_output.addBands(class_tmp.rename(yband_name))

         
    nameExp = 'filterSPU_BACIA_'+ str(name_bacia) + "_" + nmodel + "_V" + str(param['versionOut'])

    # class_output = class_output.set('version', param['versionSP'])
    class_output = class_output.select(['classification_2023']).clip(geomBacia).set(
                        'version', param['versionOut'] + 1, 'biome', 'CAATINGA',
                        'collection', '9.0', 'id_bacia', name_bacia,
                        'sensor', 'Landsat', 'source','geodatin', 
                        'filter', 'spatial_use', 'from', 'temporal',
                        'model', nmodel, 'janela', param['janela'], 
                        'system:footprint', geomBacia
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
        return 0
    
    cont += 1    
    return cont


listaNameBacias = [
    # '744','741','7422','745','746','7492','751','752','753',
    # '755','759','7621','7622', '763','764','765','766',
    # '767', '771', '772','773','7741','776','7742','775', 
    # '777', '778','76111','76116','7612','7613','7615','7616',
    # '7617','7618','7619','756','757','758', '7614', '7421', '754',
    '741', '7422', '7621', '764'
]
# listaNameBacias = [
#     # '756','757','758','754',
#     '7614', '7421'
# ]
# listaNameBacias = [
#     '752', '766', '753', '776', '764', '765', '7621', '744', 
#     '756','757','758','754','7614', '7421'
# ]
changeAcount = True
lstqFalta =  []
cont = 0
input_asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Gap-fill/'
# input_asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Spatial/'
# if changeAcount:
#     cont = gerenciador(cont)
version = 22
modelo = 'GTB'
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
            # cont = gerenciador(cont)            
            print("----- PROCESSING BACIA {} -------".format(idbacia))        
            apply_spatialFilterConn(idbacia, modelo)
            


if knowMapSaved:
    print("lista de bacias que faltam \n ",listBacFalta)
    print("total ", len(listBacFalta))