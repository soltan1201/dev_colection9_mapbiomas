#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
'''

import ee
import os 
import gee
import json
import csv
import copy
import sys
import math
import copy
from tqdm import tqdm 
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


class processo_GEDIfilter(object):

    options = {
            'output_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Estavel/',
            # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Gap-fillV2/',
            'inputAsset8': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
            'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrograficaCaatbuffer5k',
            'asset_gedi': 'users/potapovpeter/GEDI_V27',
            'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/toExport/',
            # 'asset_bacias_buffer' : 'projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga',
            'classMapB' : [3, 4, 5, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62],
            'classNew'  : [3, 4, 3, 3,12,12,21,21,21,21,21,22,22,22,22,33,29,22,33,12,33, 21,33,33,21,21,21,21,21,21,21,21,21,21, 4,12,21],
            'year_inic': 1985,
            'year_end': 2023,
            'version_int': 25,
            'version_out': 26
        }


    def __init__(self, nameBacia,  modelo):
        self.id_bacias = nameBacia
        self.geom_bacia = ee.FeatureCollection(self.options['asset_bacias_buffer']).filter(
                                                    ee.Filter.eq('nunivotto3', nameBacia)).first().geometry()   
        print("geometria ", len(self.geom_bacia.getInfo()['coordinates']))
        self.lstbandNames = ['classification_' + str(yy) for yy in range(self.options['year_inic'], self.options['year_end'] + 1)]
        self.years = [yy for yy in range(self.options['year_end'], self.options['year_inic'] - 1,  -1)]
        # print("lista de years \n ", self.years)

        rasterGEDI = ee.ImageCollection(self.options['asset_gedi']).filterBounds(
                                            self.geom_bacia).mosaic().clip(self.geom_bacia);
        self.maskGEDI = rasterGEDI.gte(7).unmask(0);
        self.model = modelo
        self.classFlorest = 3
        self.classSavana = 4
        #filterGF_BACIA_745_GTB_V30
        # self.name_imgClass = 'filterGF_BACIA_' + nameBacia + '_'+ modelo + '_V' + str(self.version )
        # self.imgClass = ee.Image(self.options['input_asset'] + self.name_imgClass)
        # BACIA_741_mixed_V23
        self.name_imgClass = 'BACIA_' + nameBacia + '_mixed_V' + str(self.options['version_int'])
        self.imgClass = ee.Image(self.options['input_asset'] + self.name_imgClass)

        print("processing image ", self.name_imgClass)        
        # print("todas as bandas \n === > ", self.imgClass.bandNames().getInfo()) 
        
        
    def dictionary_bands(self, key, value):
        imgT = ee.Algorithms.If(
                        ee.Number(value).eq(2),
                        self.imgClass.select([key]).byte(),
                        ee.Image().rename([key]).byte().updateMask(self.imgClass.select(0))
                    )
        return ee.Image(imgT)

    def applyFilter(self, paraIncluir):

        lstImgMap = None
        previousImage = None        
        ###########  CORREGINDO DE 2023 PARA 1985 ############################
        imgRasterbase = ee.Image().byte()
        for yyear in tqdm(self.years):
            bandActive = 'classification_' + str(yyear)
            # print(f" # {cc}  processing >> {bandActive}")
            currentImage = self.imgClass.select(bandActive)
            if paraIncluir:
                masktoChange = self.maskGEDI.eq(1).multiply(currentImage.eq(int(self.classSavana)))
                rasterTemp = currentImage.where(masktoChange.eq(1), self.classFlorest)  # setar 3 class
            else:
                masktoChange = self.maskGEDI.eq(0).multiply(currentImage.eq(int(self.classFlorest)))
                rasterTemp = currentImage.where(masktoChange.eq(1), self.classSavana)  # setar 3 class            
            imgRasterbase = imgRasterbase.addBands(rasterTemp)              

        imgRasterbase = imgRasterbase.select(self.lstbandNames)

        # print("show bandas from raster filtered ", imgRasterbase.bandNames().getInfo())
        return imgRasterbase

    def processing_layers_florest(self, toInclusive):
        # apply the gap fill
        imageFilled = self.applyFilter(toInclusive)
        print("passou")
        # print(imageFilled.bandNames().getInfo())

        if 'toExport' in self.options['input_asset']:
            name_toexport = f'BACIA_{self.id_bacias}_mixed_V{self.options['version_out']}'
        else:
            name_toexport = 'filterET_BACIA_'+ str(self.id_bacias) + '_' +  self.model + "_V" + str(self.option['version_out'])
        imageFilled = ee.Image(imageFilled).set(
                            'version', int(self.options['version_out']), 
                            'biome', 'CAATINGA',
                            'source', 'geodatin',
                            'model', self.model,
                            'type_filter', 'estavel',
                            'collection', '9.0',
                            'id_bacia', self.id_bacias,
                            'sensor', 'Landsat',
                            'system:footprint' , self.imgClass.get('system:footprint')
                        )
        
        self.processoExportar(imageFilled, name_toexport)

    #exporta a imagem classificada para o asset
    def processoExportar(self, mapaRF,  nomeDesc):    

        idasset =  self.options['output_asset'] + nomeDesc
        optExp = {
            'image': mapaRF, 
            'description': nomeDesc, 
            'assetId':idasset, 
            'region':self.geom_bacia.getInfo()['coordinates'],
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
    'bioma': "CAATINGA", #nome do bioma setado nos metadados  
    'numeroTask': 6,
    'numeroLimit': 42,
    'conta' : {
        '0': 'caatinga01',   # 
        '3': 'caatinga02',
        '9': 'caatinga03',
        '12': 'caatinga04',
        '15': 'caatinga05',        
        '18': 'solkan1201',    
        # '30': 'solkanGeodatin',
        '21': 'diegoUEFS',
        '24': 'superconta'     
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
    '744','741','7422','745','746','7492','751','752','753',
    '755','759','7621','7622', '763','764','765','766','767', 
    '771', '772','773','7741','776','7742','775','777', '778',
    '76116','7612','7613','7615','7616','7617','7618',
    '7619','754','756','757','758','7614','7421','76111'
]
listaNameB = []
listExclusao = ['755','753','751','741']
addFlorest = False
models = "GTB"  # "RF", "GTB"
versionMap= 30
cont = 20
for idbacia in listaNameBacias[:]:    
    if idbacia not in listaNameB:
        print("-----------------------------------------")
        print("----- PROCESSING BACIA {} -------".format(idbacia))
        cont = gerenciador(cont)
        aplicando_gapfill = processo_GEDIfilter(idbacia, models) # added band connected is True
        if idbacia in listExclusao:
            addFlorest = True
        aplicando_gapfill.processing_layers_florest(addFlorest)