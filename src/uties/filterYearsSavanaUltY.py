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
import time
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


class processo_filterTemporal(object):

    options = {
            'output_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/SpatialV3/',
            # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/FrequencyV3',
            # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/merge/',
            'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/SpatialV3',
            # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/TemporalV3',
            'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrograficaCaatbuffer5k',            
            'last_year' : 2023,
            'first_year': 1985,
            'janela' : 10,
            'step': 1
        }

    def __init__(self):
        # self.id_bacias = nameBacia
        self.versoutput = 40
        self.versionInput = 39
        self.geom_bacia = ee.FeatureCollection(self.options['asset_bacias_buffer'])#.filter(
                                                    # ee.Filter.eq('nunivotto3', nameBacia)).first().geometry()              
        self.years = [yy for yy in range(self.options['first_year'], self.options['last_year'] + 1)]  # ,  - 1, -1
        # self.years = [kk for kk in years.sort(reverse= False)]
        self.lstbandNames = ['classification_' + str(yy) for yy in range(self.options['first_year'], self.options['last_year'] + 1)]      
  
        print("lista de anos ", self.years)
        self.periodoCentral = False

    def mask_3_years (self, valor, imagem):
        #### https://code.earthengine.google.com/1f9dd3ab081d243fa9d7962e06348579
        imagem = ee.Image(imagem)
        mmask = imagem.select([0]).eq(valor).And(
                    imagem.select([1]).eq(valor)).And(
                        imagem.select([2]).eq(valor)).unmask(0)    
        
        return mmask

    # https://code.earthengine.google.com/139c598e5c3d67ea2ea60a53b29c337c
    def applyTemporalFilter(self, id_bacias, nmodel): 
           
        # imgClass = ee.ImageCollection(self.options['input_asset']).filter(
        #                         ee.Filter.eq('id_bacia', id_bacias)).filter(
        #                             ee.Filter.eq('version',  self.versionInput)).first()#.filter(
                                        # ee.Filter.eq('model', nmodel)).first()    #.filter(  # self.options['step']
                                            # ee.Filter.eq('filter', 'spatial_use')).first()
        nameImgLoad = f"filterSP_BACIA_{id_bacias}_GTB_V{self.versionInput}"
        imgClass = ee.Image(self.options['input_asset'] + "/" + nameImgLoad )     
        # print(imgClass.size().getInfo())
        print("loading ", imgClass.get('system:index').getInfo()) 
        # sys.exit()
        lstBndSavBef = [ 'classification_' + str(YY) for YY in range(2013, 2017)]
        lstYearfinal = ['classification_' + str(year) for year in range(2017, 2023)]
        
        layersSavanBefore = imgClass.select(lstBndSavBef).eq(4).reduce(ee.Reducer.sum())  
        maskBefSav = layersSavanBefore.gt(3)  # pelo menos 3 anos         == 1
        maskAftSav = imgClass.select('classification_2023').eq(4) #savana do ultimo ano    == 1 
        layersUso = imgClass.select(lstYearfinal).eq(21).reduce(ee.Reducer.sum())        
        maskUsoSec = layersUso.gt(0) # qualquer ano com 21  === 1
        makeMaskNat_UsoNat = maskBefSav.rename('year_0').addBands(
                                        maskUsoSec.rename('year_1')).addBands(
                                            maskAftSav.rename('year_2'))
            
        maskFiltro = self.mask_3_years (1, makeMaskNat_UsoNat)
        
        imgOutput = ee.Image().byte()
        for cc, bandYear in enumerate(self.lstbandNames):
            # print("  => ", lstyear)
            if bandYear in lstYearfinal:   
                muda_imgem = imgClass.select(bandYear).where(maskFiltro.eq(1), 4)  # coloca a savana de volta 
                imgOutput = imgOutput.addBands(muda_imgem.rename(bandYear))
            else:                        
                imgOutput = imgOutput.addBands(imgClass.select(bandYear))
            
            # time.sleep(3)
        imgOutput = imgOutput.select(self.lstbandNames)   
        if id_bacias == '744':         
            print(" ver las bandas ", imgOutput.bandNames().getInfo())


        geom = self.geom_bacia.filter(ee.Filter.eq('nunivotto3', id_bacias)).first().geometry()
        imgOutput = imgOutput.set(
                            'version',  self.versoutput, 
                            'biome', 'CAATINGA',
                            'type_filter', 'spacial',
                            'collection', '9.0',
                            'id_bacia', id_bacias,
                            'janela', self.options['janela'],
                            'sensor', 'Landsat', 'model',nmodel ,
                            'system:footprint' , geom
                        )
        
        name_toexport = 'filterTP_BACIA_'+ str(id_bacias) + f"_{nmodel}_V" + str(self.versoutput)
        self.processoExportar(imgOutput, name_toexport, geom)    



    def processoExportar(self, mapaRF,  nomeDesc, geom_bacia):
        
        idasset =  self.options['output_asset'] + nomeDesc
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



param = {      
    'numeroTask': 6,
    'numeroLimit': 42,
    'conta' : {
        '0': 'caatinga01',
        '4': 'caatinga02',
        '6': 'caatinga03',
        '8': 'caatinga04',
        '10': 'caatinga05',        
        '12': 'solkan1201',    
        '14': 'solkanGeodatin',
        '16': 'diegoUEFS' ,
        '18': 'superconta'      
    }
}

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
   '754','744','741','7421', '7422','745','746','7492','751','752',
   '753','755','758','759','7621','7622','764','765','766',
   '767','771','772','7741','7742','773','775', '777', '778',
   '76111','76116','7612','7614','7615','7616','7617','7618','7619', 
   '7613','756','757','763','776'    
]


lstBacias = ['754', '7622','7741', '7615']
aplicando_TemporalFilter = processo_filterTemporal()
# sys.exit()

# for cc, lst in enumerate(aplicando_TemporalFilter.colectAnos):
#     print(1985 + cc, lst)
# 
# input_asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/SpatialV3/'
input_asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/TemporalV3/'
applyfilter = False
version = 34
janela = 5
cont = 0
modelo = "GTB"
listBacFalta = []
knowMapSaved = False
for cc, idbacia in enumerate(listaNameBacias[:]):   
    if knowMapSaved:
        try:
            if 'Spatial' in input_asset:
                nameMap = 'filterSPU_BACIA_' + idbacia + f"_{modelo}_V" + str(version)
            else:
                nameMap = 'filterTP_BACIA_'+ idbacia + f"_GTB_J{janela}_V" + str(version)
            print(input_asset + nameMap)
            imgtmp = ee.Image(input_asset + nameMap)
            print(f" {cc} loading ", nameMap, " ", len(imgtmp.bandNames().getInfo()), "bandas ")
            if cc == 0:
                print('show bands \n ', imgtmp.bandNames().getInfo())
        except:
            listBacFalta.append(idbacia)
    else: 
        if idbacia in lstBacias:
            # cont = gerenciador(cont)
            print("----- PROCESSING BACIA {} -------".format(idbacia))        
            aplicando_TemporalFilter.applyTemporalFilter(idbacia, modelo)


if knowMapSaved:
    print("lista de bacias que faltam \n ",listBacFalta)
    print("total ", len(listBacFalta))