#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Produzido por Geodatin - Dados e Geoinformacao
DISTRIBUIDO COM GPLv2
@author: geodatin
"""

import ee
import gee
import json
import copy
import csv
from tqdm import tqdm
import sys
import arqParametros as arqParam
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


class ClassMosaic_indexs_Spectral(object):

    feat_pts_true = ee.FeatureCollection([])
    # default options
    options = {
        'bnd_L': ['blue','green','red','nir','swir1','swir2'],
        'bnd_fraction': ['gv','npv','soil'],
        'bioma': 'CAATINGA',
        'classMapB': [3, 4, 5, 9, 12, 13, 15, 18, 19, 20, 21, 22, 23, 24, 25, 26, 29, 30, 31, 32, 33,
                      36, 39, 40, 41, 46, 47, 48, 49, 50, 62],
        'classNew':  [3, 4, 3, 3, 12, 12, 15, 18, 18, 18, 18, 22, 22, 22, 22, 33, 29, 22, 33, 12, 33,
                      18, 18, 18, 18, 18, 18, 18,  4,  4, 21],
        'asset_baciasN2': 'projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga',
        'asset_baciasN4': 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrografica_caatingaN4',
        'asset_cruzN245': 'projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga_BdivN245',
        'outAssetROIs': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/',
        'inputAssetStats': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/ROIs/stats_mosaics/all_statisticsL8',
        'assetMapbiomasGF': 'projects/mapbiomas-workspace/AMOSTRAS/col6/CAATINGA/classificacoes/classesV5',
        'assetMapbiomas50': 'projects/mapbiomas-workspace/public/collection5/mapbiomas_collection50_integration_v1',
        'assetMapbiomas60': 'projects/mapbiomas-workspace/public/collection6/mapbiomas_collection60_integration_v1',
        'assetMapbiomas71': 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1',
        'assetMapbiomas80': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
        'asset_mosaic_mapbiomas': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',
        'asset_fire': 'projects/ee-geomapeamentoipam/assets/MAPBIOMAS_FOGO/COLECAO_2/Colecao2_fogo_mask_v1',
        'asset_befFilters': 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/classification_Col71_S1v18',
        'asset_filtered': 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/class_filtered_Tp',
        'asset_alerts': 'users/data_sets_solkan/Alertas/layersClassTP',
        'asset_input_mask' : 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/masks/maks_layers',
        'asset_baseROIs_col9': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/',
        'asset_alerts_SAD': 'users/data_sets_solkan/Alertas/layersImgClassTP_2024_02',
        'asset_alerts_Desf': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_deforestation_secondary_vegetation_v2',
        'assetrecorteCaatCerrMA' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/recorteCaatCeMA',
        'asset_ROIs_manual': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/ROIs/coletaROIsv7N2manual'},
        'asset_ROIs_cluster': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/ROIs/coletaROIsv6N2cluster'}, 
        'asset_ROIs_automatic': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/coletaROIsv1N245'},
        'asset_Coincidencia': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/masks/maks_coinciden',
        'asset_estaveis': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/masks/maks_estaveis',
        'asset_fire_mask': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/masks/maks_fire_w5',
        'lsClasse': [3, 4, 12, 15, 18, 21, 22, 33, 29],
        'lsPtos': [3000, 2000, 3000, 1500, 1500, 1000, 1500, 1000, 1000],
        "anoIntInit": 1985,
        "anoIntFin": 2022,
        'janela': 3
    }
    lst_bandExt = [
        'blue_min','blue_stdDev','green_min','green_stdDev','green_median_texture', 
        'red_min', 'red_stdDev','nir_min','nir_stdDev', 'swir1_min', 'swir1_stdDev', 
        'swir2_min', 'swir2_stdDev'
    ]
    newlstNameBacin = [
        '741_0','7421_0','7422_0','745_0','751_0','752_0',
        '754_0','755_0','756_0','757_0','759_0', '7613_0', '76111_0',
        '7612_0','7614_0','7616_0','7622_0','763_0','764_0','765_0',
        '767_0','771_0','772_0','773_0','7742_0','775_0','776_0',
        '777_0','778_0',
        '744_0','746_0','7492_0','753_0','758_0','7621_0','766_0',
        '7741_0','7615_0','76116_0','7617_0','7618_0','7619_0',
        '744_1','746_1','7492_1','753_1','758_1','7621_1','766_1',
        '7741_1','7615_1','76116_1','7617_1','7618_1','7619_1',
    ]
    # featureBands = [
    #     'blue_median','blue_median_wet','blue_median_dry','blue_min','blue_stdDev', 
    #     'green_median','green_median_wet','green_median_dry','green_min','green_stdDev','green_median_texture', 
    #     'red_median','red_median_wet','red_median_dry','red_min', 'red_stdDev', 
    #     'nir_median','nir_median_wet','nir_median_dry','nir_min','nir_stdDev', 
    #     'swir1_median','swir1_median_wet','swir1_median_dry','swir1_min', 'swir1_stdDev', 
    #     'swir2_median', 'swir2_median_wet', 'swir2_median_dry','swir2_min', 'swir2_stdDev',
    #     'slope'
    # ]
    lst_properties = arqParam.allFeatures
    # MOSAIC WITH BANDA 2022 
    # https://code.earthengine.google.com/c3a096750d14a6aa5cc060053580b019
    def __init__(self, ):

        self.regionInterest = ee.FeatureCollection(self.options['asset_baciasN2'])#.geometry()
        simgMosaic = ee.ImageCollection(self.options['asset_mosaic_mapbiomas']
                                                    ).filter(ee.Filter.eq('biome', self.options['bioma'])
                                                        ).select(arqParam.featureBands)
        print(ee.Image(simgMosaic.first()).bandNames().getInfo())

        self.imgMosaic = simgMosaic.map(lambda img: self.process_re_escalar_img(img))                          
        # print("  ", self.imgMosaic.size().getInfo())
        print("see band Names the first ")
        print(" ==== ", ee.Image(self.imgMosaic.first()).bandNames().getInfo())
        print("all images ", self.imgMosaic.size().getInfo())
        print("==================================================")

        self.lst_year = [k for k in range(self.options['anoIntInit'], self.options['anoIntFin'] + 1)]
        # # @collection6 bruta: mapas de uso e cobertura Mapbiomas ==> para masquear as amostra fora de mascara
        # self.collection_bruta = ee.ImageCollection(self.options['assetMapbiomas71']).min()
        # self.img_mask = self.collection_bruta.unmask(100).eq(100).reduce(ee.Reducer.sum())
        # self.img_mask = self.img_mask.eq(0).selfMask()
        
        # @collection71: mapas de uso e cobertura Mapbiomas ==> para extrair as areas estaveis
        collection80 = ee.Image(self.options['assetMapbiomas80'])

        # # Remap todas as imagens mapbiomas
        lsBndMapBiomnas = []
        self.imgMapbiomas = ee.Image().toByte()

        for year in self.lst_year:
            band = 'classification_' + str(year)
            lsBndMapBiomnas.append(band)
            imgTemp = collection80.select(band).remap(
                self.options['classMapB'], self.options['classNew'])
            self.imgMapbiomas = self.imgMapbiomas.addBands(
                imgTemp.rename(band))



        self.imgMapbiomas = self.imgMapbiomas.select(lsBndMapBiomnas).clip(self.regionInterest.geometry())
        # self.imgMapbiomas = self.imgMapbiomas.updateMask(self.img_mask)

        self.baciasN2 = ee.FeatureCollection(self.options['asset_baciasN2'])
        # colectAnos = []

    def process_re_escalar_img (self, imgA):
        imgNormal = imgA.select(['slope'], ['slopeA']).divide(1500).toFloat()
        bandMos = copy.deepcopy(arqParam.featureBands)
        bandMos.remove('slope')
        imgEscalada = imgA.select(bandMos).divide(10000);

        return imgA.select(['slope']).addBands(imgEscalada.toFloat()).addBands(imgNormal)
        #return imgEscalada.toFloat().addBands(imgNormal)

    #region Bloco de functions de calculos de Indices 
    # Ratio Vegetation Index
    def agregateBandsIndexRATIO(self, img):
    
        ratioImgY = img.expression("float(b('nir_median') / b('red_median'))")\
                                .rename(['ratio_median']).toFloat()

        ratioImgwet = img.expression("float(b('nir_median_wet') / b('red_median_wet'))")\
                                .rename(['ratio_median_wet']).toFloat()  

        ratioImgdry = img.expression("float(b('nir_median_dry') / b('red_median_dry'))")\
                                .rename(['ratio_median_dry']).toFloat()        

        return img.addBands(ratioImgY).addBands(ratioImgwet).addBands(ratioImgdry)

    # Ratio Vegetation Index
    def agregateBandsIndexRVI(self, img):
    
        rviImgY = img.expression("float(b('red_median') / b('nir_median'))")\
                                .rename(['rvi_median']).toFloat() 
        
        rviImgWet = img.expression("float(b('red_median_wet') / b('nir_median_wet'))")\
                                .rename(['rvi_median_wet']).toFloat() 

        rviImgDry = img.expression("float(b('red_median_dry') / b('nir_median_dry'))")\
                                .rename(['rvi_median']).toFloat()       

        return img.addBands(rviImgY).addBands(rviImgWet).addBands(rviImgDry)
    
    def agregateBandsIndexNDVI(self, img):
    
        ndviImgY = img.expression("float(b('nir_median') - b('red_median')) / (b('nir_median') + b('red_median'))")\
                                .rename(['ndvi_median']).toFloat()    

        ndviImgWet = img.expression("float(b('nir_median_wet') - b('red_median_wet')) / (b('nir_median_wet') + b('red_median_wet'))")\
                                .rename(['ndvi_median_wet']).toFloat()  

        ndviImgDry = img.expression("float(b('nir_median_dry') - b('red_median_dry')) / (b('nir_median_dry') + b('red_median_dry'))")\
                                .rename(['ndvi_median_dry']).toFloat()     

        return img.addBands(ndviImgY).addBands(ndviImgWet).addBands(ndviImgDry)

    def agregateBandsIndexWater(self, img):
    
        ndwiImgY = img.expression("float(b('nir_median') - b('swir2_median')) / (b('nir_median') + b('swir2_median'))")\
                                .rename(['ndwi_median']).toFloat()       

        ndwiImgWet = img.expression("float(b('nir_median_wet') - b('swir2_median_wet')) / (b('nir_median_wet') + b('swir2_median_wet'))")\
                                .rename(['ndwi_median_wet']).toFloat()   

        ndwiImgDry = img.expression("float(b('nir_median_dry') - b('swir2_median_dry')) / (b('nir_median_dry') + b('swir2_median_dry'))")\
                                .rename(['ndwi_median_dry']).toFloat()   

        return img.addBands(ndwiImgY).addBands(ndwiImgWet).addBands(ndwiImgDry)
    
    def AutomatedWaterExtractionIndex(self, img):    
        aweiY = img.expression(
                            "float(4 * (b('green_median') - b('swir2_median')) - (0.25 * b('nir_median') + 2.75 * b('swir1_median')))"
                        ).rename("awei_median").toFloat() 

        aweiWet = img.expression(
                            "float(4 * (b('green_median_wet') - b('swir2_median_wet')) - (0.25 * b('nir_median_wet') + 2.75 * b('swir1_median_wet')))"
                        ).rename("awei_median_wet").toFloat() 

        aweiDry = img.expression(
                            "float(4 * (b('green_median_dry') - b('swir2_median_dry')) - (0.25 * b('nir_median_dry') + 2.75 * b('swir1_median_dry')))"
                        ).rename("awei_median_dry").toFloat()          
        
        return img.addBands(aweiY).addBands(aweiWet).addBands(aweiDry)
    
    def IndiceIndicadorAgua(self, img):    
        iiaImgY = img.expression(
                            "float((b('green_median') - 4 *  b('nir_median')) / (b('green_median') + 4 *  b('nir_median')))"
                        ).rename("iia_median").toFloat()
        
        iiaImgWet = img.expression(
                            "float((b('green_median_wet') - 4 *  b('nir_median_wet')) / (b('green_median_wet') + 4 *  b('nir_median_wet')))"
                        ).rename("iia_median_wet").toFloat()

        iiaImgDry = img.expression(
                            "float((b('green_median_dry') - 4 *  b('nir_median_dry')) / (b('green_median_dry') + 4 *  b('nir_median_dry')))"
                        ).rename("iia_median_dry").toFloat()
        
        return img.addBands(iiaImgY).addBands(iiaImgWet).addBands(iiaImgDry)
    
    def agregateBandsIndexEVI(self, img):
            
        eviImgY = img.expression(
            "float(2.4 * (b('nir_median') - b('red_median')) / (1 + b('nir_median') + b('red_median')))")\
                .rename(['evi_median'])     

        eviImgWet = img.expression(
            "float(2.4 * (b('nir_median_wet') - b('red_median_wet')) / (1 + b('nir_median_wet') + b('red_median_wet')))")\
                .rename(['evi_median_wet'])   

        eviImgDry = img.expression(
            "float(2.4 * (b('nir_median_dry') - b('red_median_dry')) / (1 + b('nir_median_dry') + b('red_median_dry')))")\
                .rename(['evi_median_dry'])   
        
        return img.addBands(eviImgY).addBands(eviImgWet).addBands(eviImgDry)

    def agregateBandsIndexGVMI(self, img):
        
        gvmiImgY = img.expression(
                        "float ((b('nir_median')  + 0.1) - (b('swir1_median') + 0.02)) / ((b('nir_median') + 0.1) + (b('swir1_median') + 0.02))" 
                    ).rename(['gvmi_median']).toFloat()   

        gvmiImgWet = img.expression(
                        "float ((b('nir_median_wet')  + 0.1) - (b('swir1_median_wet') + 0.02)) / ((b('nir_median_wet') + 0.1) + (b('swir1_median_wet') + 0.02))" 
                    ).rename(['gvmi_median_wet']).toFloat()

        gvmiImgDry = img.expression(
                        "float ((b('nir_median_dry')  + 0.1) - (b('swir1_median_dry') + 0.02)) / ((b('nir_median_dry') + 0.1) + (b('swir1_median_dry') + 0.02))" 
                    ).rename(['gvmi_median_dry']).toFloat()  
    
        return img.addBands(gvmiImgY).addBands(gvmiImgWet).addBands(gvmiImgDry)
    
    def agregateBandsIndexLAI(self, img):
        laiImgY = img.expression(
            "float(3.618 * (b('evi_median') - 0.118))")\
                .rename(['lai_median']).toFloat()
    
        return img.addBands(laiImgY)    

    def agregateBandsIndexGCVI(self, img):    
        gcviImgAY = img.expression(
            "float(b('nir_median')) / (b('green_median')) - 1")\
                .rename(['gcvi_median']).toFloat()   

        gcviImgAWet = img.expression(
            "float(b('nir_median_wet')) / (b('green_median_wet')) - 1")\
                .rename(['gcvi_median_wet']).toFloat() 
                
        gcviImgADry = img.expression(
            "float(b('nir_median_dry')) / (b('green_median_dry')) - 1")\
                .rename(['gcvi_median_dry']).toFloat()      
        
        return img.addBands(gcviImgAY).addBands(gcviImgAWet).addBands(gcviImgADry)

    # Global Environment Monitoring Index GEMI 
    def agregateBandsIndexGEMI(self, img):    
        # "( 2 * ( NIR ^2 - RED ^2) + 1.5 * NIR + 0.5 * RED ) / ( NIR + RED + 0.5 )"
        gemiImgAY = img.expression(
            "float((2 * (b('nir_median') * b('nir_median') - b('red_median') * b('red_median')) + 1.5 * b('nir_median')" +
            " + 0.5 * b('red_median')) / (b('nir_median') + b('green_median') + 0.5) )")\
                .rename(['gemi_median']).toFloat()    

        gemiImgAWet = img.expression(
            "float((2 * (b('nir_median_wet') * b('nir_median_wet') - b('red_median_wet') * b('red_median_wet')) + 1.5 * b('nir_median_wet')" +
            " + 0.5 * b('red_median_wet')) / (b('nir_median_wet') + b('green_median_wet') + 0.5) )")\
                .rename(['gemi_median_wet']).toFloat() 

        gemiImgADry = img.expression(
            "float((2 * (b('nir_median_dry') * b('nir_median_dry') - b('red_median_dry') * b('red_median_dry')) + 1.5 * b('nir_median_dry')" +
            " + 0.5 * b('red_median_dry')) / (b('nir_median_dry') + b('green_median_dry') + 0.5) )")\
                .rename(['gemi_median_dry']).toFloat()     
        
        return img.addBands(gemiImgAY).addBands(gemiImgAWet).addBands(gemiImgADry)

    # Chlorophyll vegetation index CVI
    def agregateBandsIndexCVI(self, img):    
        cviImgAY = img.expression(
            "float(b('nir_median') * (b('green_median') / (b('blue_median') * b('blue_median'))))")\
                .rename(['cvi_median']).toFloat()  

        cviImgAWet = img.expression(
            "float(b('nir_median_wet') * (b('green_median_wet') / (b('blue_median_wet') * b('blue_median_wet'))))")\
                .rename(['cvi_median_wet']).toFloat()

        cviImgADry = img.expression(
            "float(b('nir_median_dry') * (b('green_median_dry') / (b('blue_median_dry') * b('blue_median_dry'))))")\
                .rename(['cvi_median_dry']).toFloat()      
        
        return img.addBands(cviImgAY).addBands(cviImgAWet).addBands(cviImgADry)

    # Green leaf index  GLI
    def agregateBandsIndexGLI(self,img):    
        gliImgY = img.expression(
            "float((2 * b('green_median') - b('red_median') - b('blue_median')) / (2 * b('green_median') - b('red_median') - b('blue_median')))")\
                .rename(['gli_median']).toFloat()    

        gliImgWet = img.expression(
            "float((2 * b('green_median_wet') - b('red_median_wet') - b('blue_median_wet')) / (2 * b('green_median_wet') - b('red_median_wet') - b('blue_median_wet')))")\
                .rename(['gli_median_wet']).toFloat()   

        gliImgDry = img.expression(
            "float((2 * b('green_median_dry') - b('red_median_dry') - b('blue_median_dry')) / (2 * b('green_median_dry') - b('red_median_dry') - b('blue_median_dry')))")\
                .rename(['gli_median_dry']).toFloat()       
        
        return img.addBands(gliImgY).addBands(gliImgWet).addBands(gliImgDry)

    # Shape Index  IF 
    def agregateBandsIndexShapeI(self, img):    
        shapeImgAY = img.expression(
            "float((2 * b('red_median') - b('green_median') - b('blue_median')) / (b('green_median') - b('blue_median')))")\
                .rename(['shape_median']).toFloat()  

        shapeImgAWet = img.expression(
            "float((2 * b('red_median_wet') - b('green_median_wet') - b('blue_median_wet')) / (b('green_median_wet') - b('blue_median_wet')))")\
                .rename(['shape_median_wet']).toFloat() 

        shapeImgADry = img.expression(
            "float((2 * b('red_median_dry') - b('green_median_dry') - b('blue_median_dry')) / (b('green_median_dry') - b('blue_median_dry')))")\
                .rename(['shape_median_dry']).toFloat()      
        
        return img.addBands(shapeImgAY).addBands(shapeImgAWet).addBands(shapeImgADry)

    # Aerosol Free Vegetation Index (2100 nm) 
    def agregateBandsIndexAFVI(self, img):    
        afviImgAY = img.expression(
            "float((b('nir_median') - 0.5 * b('swir2_median')) / (b('nir_median') + 0.5 * b('swir2_median')))")\
                .rename(['afvi_median']).toFloat()  

        afviImgAWet = img.expression(
            "float((b('nir_median_wet') - 0.5 * b('swir2_median_wet')) / (b('nir_median_wet') + 0.5 * b('swir2_median_wet')))")\
                .rename(['afvi_median_wet']).toFloat()

        afviImgADry = img.expression(
            "float((b('nir_median_dry') - 0.5 * b('swir2_median_dry')) / (b('nir_median_dry') + 0.5 * b('swir2_median_dry')))")\
                .rename(['afvi_median_dry']).toFloat()      
        
        return img.addBands(afviImgAY).addBands(afviImgAWet).addBands(afviImgADry)

    # Advanced Vegetation Index 
    def agregateBandsIndexAVI(self, img):    
        aviImgAY = img.expression(
            "float((b('nir_median')* (1.0 - b('red_median')) * (b('nir_median') - b('red_median'))) ** 1/3)")\
                .rename(['avi_median']).toFloat()   

        aviImgAWet = img.expression(
            "float((b('nir_median_wet')* (1.0 - b('red_median_wet')) * (b('nir_median_wet') - b('red_median_wet'))) ** 1/3)")\
                .rename(['avi_median_wet']).toFloat()

        aviImgADry = img.expression(
            "float((b('nir_median_dry')* (1.0 - b('red_median_dry')) * (b('nir_median_dry') - b('red_median_dry'))) ** 1/3)")\
                .rename(['avi_median_dry']).toFloat()     
        
        return img.addBands(aviImgAY).addBands(aviImgAWet).addBands(aviImgADry)

    # Bare Soil Index 
    def agregateBandsIndexBSI(self,img):    
        bsiImgY = img.expression(
            "float(((b('swir1_median') - b('red_median')) - (b('nir_median') + b('blue_median'))) / " + 
                "((b('swir1_median') + b('red_median')) + (b('nir_median') + b('blue_median'))))")\
                .rename(['bsi_median']).toFloat()  

        bsiImgWet = img.expression(
            "float(((b('swir1_median') - b('red_median')) - (b('nir_median') + b('blue_median'))) / " + 
                "((b('swir1_median') + b('red_median')) + (b('nir_median') + b('blue_median'))))")\
                .rename(['bsi_median']).toFloat()

        bsiImgDry = img.expression(
            "float(((b('swir1_median') - b('red_median')) - (b('nir_median') + b('blue_median'))) / " + 
                "((b('swir1_median') + b('red_median')) + (b('nir_median') + b('blue_median'))))")\
                .rename(['bsi_median']).toFloat()      
        
        return img.addBands(bsiImgY).addBands(bsiImgWet).addBands(bsiImgDry)

    # BRBA	Band Ratio for Built-up Area  
    def agregateBandsIndexBRBA(self,img):    
        brbaImgY = img.expression(
            "float(b('red_median') / b('swir1_median'))")\
                .rename(['brba_median']).toFloat()   

        brbaImgWet = img.expression(
            "float(b('red_median_wet') / b('swir1_median_wet'))")\
                .rename(['brba_median_wet']).toFloat()

        brbaImgDry = img.expression(
            "float(b('red_median_dry') / b('swir1_median_dry'))")\
                .rename(['brba_median_dry']).toFloat()     
        
        return img.addBands(brbaImgY).addBands(brbaImgWet).addBands(brbaImgDry)

    # DSWI5	Disease-Water Stress Index 5
    def agregateBandsIndexDSWI5(self,img):    
        dswi5ImgY = img.expression(
            "float((b('nir_median') + b('green_median')) / (b('swir1_median') + b('red_median')))")\
                .rename(['dswi5_median']).toFloat() 

        dswi5ImgWet = img.expression(
            "float((b('nir_median_wet') + b('green_median_wet')) / (b('swir1_median_wet') + b('red_median_wet')))")\
                .rename(['dswi5_median_wet']).toFloat() 

        dswi5ImgDry = img.expression(
            "float((b('nir_median_dry') + b('green_median_dry')) / (b('swir1_median_dry') + b('red_median_dry')))")\
                .rename(['dswi5_median_dry']).toFloat() 

        return img.addBands(dswi5ImgY).addBands(dswi5ImgWet).addBands(dswi5ImgDry)

    # LSWI	Land Surface Water Index
    def agregateBandsIndexLSWI(self,img):    
        lswiImgY = img.expression(
            "float((b('nir_median') - b('swir1_median')) / (b('nir_median') + b('swir1_median')))")\
                .rename(['lswi_median']).toFloat()  

        lswiImgWet = img.expression(
            "float((b('nir_median_wet') - b('swir1_median_wet')) / (b('nir_median_wet') + b('swir1_median_wet')))")\
                .rename(['lswi_median_wet']).toFloat()

        lswiImgDry = img.expression(
            "float((b('nir_median_dry') - b('swir1_median_dry')) / (b('nir_median_dry') + b('swir1_median_dry')))")\
                .rename(['lswi_median_dry']).toFloat()      
        
        return img.addBands(lswiImgY).addBands(lswiImgWet).addBands(lswiImgDry)

    # MBI	Modified Bare Soil Index
    def agregateBandsIndexMBI(self,img):    
        mbiImgY = img.expression(
            "float(((b('swir1_median') - b('swir2_median') - b('nir_median')) /" + 
                " (b('swir1_median') + b('swir2_median') + b('nir_median'))) + 0.5)")\
                    .rename(['mbi_median']).toFloat() 

        mbiImgWet = img.expression(
            "float(((b('swir1_median_wet') - b('swir2_median_wet') - b('nir_median_wet')) /" + 
                " (b('swir1_median_wet') + b('swir2_median_wet') + b('nir_median_wet'))) + 0.5)")\
                    .rename(['mbi_median_wet']).toFloat() 

        mbiImgDry = img.expression(
            "float(((b('swir1_median_dry') - b('swir2_median_dry') - b('nir_median_dry')) /" + 
                " (b('swir1_median_dry') + b('swir2_median_dry') + b('nir_median_dry'))) + 0.5)")\
                    .rename(['mbi_median_dry']).toFloat()       
        
        return img.addBands(mbiImgY).addBands(mbiImgWet).addBands(mbiImgDry)

    # UI	Urban Index	urban
    def agregateBandsIndexUI(self,img):    
        uiImgY = img.expression(
            "float((b('swir2_median') - b('nir_median')) / (b('swir2_median') + b('nir_median')))")\
                .rename(['ui_median']).toFloat()  

        uiImgWet = img.expression(
            "float((b('swir2_median_wet') - b('nir_median_wet')) / (b('swir2_median_wet') + b('nir_median_wet')))")\
                .rename(['ui_median_wet']).toFloat() 

        uiImgDry = img.expression(
            "float((b('swir2_median_dry') - b('nir_median_dry')) / (b('swir2_median_dry') + b('nir_median_dry')))")\
                .rename(['ui_median_dry']).toFloat()       
        
        return img.addBands(uiImgY).addBands(uiImgWet).addBands(uiImgDry)

    # OSAVI	Optimized Soil-Adjusted Vegetation Index
    def agregateBandsIndexOSAVI(self,img):    
        osaviImgY = img.expression(
            "float(b('nir_median') - b('red_median')) / (0.16 + b('nir_median') + b('red_median'))")\
                .rename(['osavi_median']).toFloat() 

        osaviImgWet = img.expression(
            "float(b('nir_median_wet') - b('red_median_wet')) / (0.16 + b('nir_median_wet') + b('red_median_wet'))")\
                .rename(['osavi_median_wet']).toFloat() 

        osaviImgDry = img.expression(
            "float(b('nir_median_dry') - b('red_median_dry')) / (0.16 + b('nir_median_dry') + b('red_median_dry'))")\
                .rename(['osavi_median_dry']).toFloat()        
        
        return img.addBands(osaviImgY).addBands(osaviImgWet).addBands(osaviImgDry)

    # Normalized Difference Red/Green Redness Index  RI
    def agregateBandsIndexRI(self, img):        
        riImgY = img.expression(
            "float(b('nir_median') - b('green_median')) / (b('nir_median') + b('green_median'))")\
                .rename(['ri_median']).toFloat()   

        riImgWet = img.expression(
            "float(b('nir_median_wet') - b('green_median_wet')) / (b('nir_median_wet') + b('green_median_wet'))")\
                .rename(['ri_median_wet']).toFloat()

        riImgDry = img.expression(
            "float(b('nir_median_dry') - b('green_median_dry')) / (b('nir_median_dry') + b('green_median_dry'))")\
                .rename(['ri_median_dry']).toFloat()    
        
        return img.addBands(riImgY).addBands(riImgWet).addBands(riImgDry)    

    # Tasselled Cap - brightness 
    def agregateBandsIndexBrightness(self, img):    
        tasselledCapImgY = img.expression(
            "float(0.3037 * b('blue_median') + 0.2793 * b('green_median') + 0.4743 * b('red_median')  " + 
                "+ 0.5585 * b('nir_median') + 0.5082 * b('swir1_median') +  0.1863 * b('swir2_median'))")\
                    .rename(['brightness_median']).toFloat()

        tasselledCapImgWet = img.expression(
            "float(0.3037 * b('blue_median_wet') + 0.2793 * b('green_median_wet') + 0.4743 * b('red_median_wet')  " + 
                "+ 0.5585 * b('nir_median_wet') + 0.5082 * b('swir1_median_wet') +  0.1863 * b('swir2_median_wet'))")\
                    .rename(['brightness_median_wet']).toFloat()

        tasselledCapImgDry = img.expression(
            "float(0.3037 * b('blue_median_dry') + 0.2793 * b('green_median_dry') + 0.4743 * b('red_median_dry')  " + 
                "+ 0.5585 * b('nir_median_dry') + 0.5082 * b('swir1_median_dry') +  0.1863 * b('swir2_median_dry'))")\
                    .rename(['brightness_median_dry']).toFloat() 
        
        return img.addBands(tasselledCapImgY).addBands(tasselledCapImgWet).addBands(tasselledCapImgDry)
    
    # Tasselled Cap - wetness 
    def agregateBandsIndexwetness(self, img): 

        tasselledCapImgY = img.expression(
            "float(0.1509 * b('blue_median') + 0.1973 * b('green_median') + 0.3279 * b('red_median')  " + 
                "+ 0.3406 * b('nir_median') + 0.7112 * b('swir1_median') +  0.4572 * b('swir2_median'))")\
                    .rename(['wetness_median']).toFloat() 
        
        tasselledCapImgWet = img.expression(
            "float(0.1509 * b('blue_median_wet') + 0.1973 * b('green_median_wet') + 0.3279 * b('red_median_wet')  " + 
                "+ 0.3406 * b('nir_median_wet') + 0.7112 * b('swir1_median_wet') +  0.4572 * b('swir2_median_wet'))")\
                    .rename(['wetness_median_wet']).toFloat() 
        
        tasselledCapImgDry = img.expression(
            "float(0.1509 * b('blue_median_dry') + 0.1973 * b('green_median_dry') + 0.3279 * b('red_median_dry')  " + 
                "+ 0.3406 * b('nir_median_dry') + 0.7112 * b('swir1_median_dry') +  0.4572 * b('swir2_median_dry'))")\
                    .rename(['wetness_median_dry']).toFloat() 
        
        return img.addBands(tasselledCapImgY).addBands(tasselledCapImgWet).addBands(tasselledCapImgDry)
    
    # Moisture Stress Index (MSI)
    def agregateBandsIndexMSI(self, img):    
        msiImgY = img.expression(
            "float( b('nir_median') / b('swir1_median'))")\
                .rename(['msi_median']).toFloat() 
        
        msiImgWet = img.expression(
            "float( b('nir_median_wet') / b('swir1_median_wet'))")\
                .rename(['msi_median_wet']).toFloat() 

        msiImgDry = img.expression(
            "float( b('nir_median_dry') / b('swir1_median_dry'))")\
                .rename(['msi_median_dry']).toFloat() 
        
        return img.addBands(msiImgY).addBands(msiImgWet).addBands(msiImgDry)


    def agregateBandsIndexGVMI(self, img):        
        gvmiImgY = img.expression(
                        "float ((b('nir_median')  + 0.1) - (b('swir1_median') + 0.02)) " + 
                            "/ ((b('nir_median') + 0.1) + (b('swir1_median') + 0.02))" 
                        ).rename(['gvmi_median']).toFloat()  

        gvmiImgWet = img.expression(
                        "float ((b('nir_median_wet')  + 0.1) - (b('swir1_median_wet') + 0.02)) " + 
                            "/ ((b('nir_median_wet') + 0.1) + (b('swir1_median_wet') + 0.02))" 
                        ).rename(['gvmi_median_wet']).toFloat()

        gvmiImgDry = img.expression(
                        "float ((b('nir_median_dry')  + 0.1) - (b('swir1_median_dry') + 0.02)) " + 
                            "/ ((b('nir_median_dry') + 0.1) + (b('swir1_median_dry') + 0.02))" 
                        ).rename(['gvmi_median_dry']).toFloat()   
    
        return img.addBands(gvmiImgY).addBands(gvmiImgWet).addBands(gvmiImgDry) 
    
    def agregateBandsIndexsPRI(self, img):        
        priImgY = img.expression(
                                "float((b('green_median') - b('blue_median')) / (b('green_median') + b('blue_median')))"
                            ).rename(['pri_median'])   
        spriImgY =   priImgY.expression(
                                "float((b('pri_median') + 1) / 2)").rename(['spri_median']).toFloat()  

        priImgWet = img.expression(
                                "float((b('green_median_wet') - b('blue_median_wet')) / (b('green_median_wet') + b('blue_median_wet')))"
                            ).rename(['pri_median_wet'])   
        spriImgWet =   priImgWet.expression(
                                "float((b('pri_median_wet') + 1) / 2)").rename(['spri_median_wet']).toFloat()

        priImgDry = img.expression(
                                "float((b('green_median') - b('blue_median')) / (b('green_median') + b('blue_median')))"
                            ).rename(['pri_median'])   
        spriImgDry =   priImgDry.expression(
                                "float((b('pri_median') + 1) / 2)").rename(['spri_median']).toFloat()
    
        return img.addBands(spriImgY).addBands(spriImgWet).addBands(spriImgDry)
    

    def agregateBandsIndexCO2Flux(self, img):        
        ndviImg = img.expression("float(b('nir_median') - b('swir2_median')) / (b('nir_median') + b('swir2_median'))").rename(['ndvi']) 
        
        priImg = img.expression(
                                "float((b('green_median') - b('blue_median')) / (b('green_median') + b('blue_median')))"
                            ).rename(['pri_median'])   
        spriImg =   priImg.expression(
                                "float((b('pri_median') + 1) / 2)").rename(['spri_median'])

        co2FluxImg = ndviImg.multiply(spriImg).rename(['co2flux_median'])   
        
        return img.addBands(co2FluxImg)


    def agregateBandsTexturasGLCM(self, img):        
        img = img.toInt()                
        textura2 = img.select('nir_median').glcmTexture(3)  
        contrastnir = textura2.select('nir_median_contrast').toUint16()
        textura2Dry = img.select('nir_median_dry').glcmTexture(3)  
        contrastnirDry = textura2Dry.select('nir_median_dry_contrast').toUint16()
        #
        textura2R = img.select('red_median').glcmTexture(3)  
        contrastred = textura2R.select('red_median_contrast').toFloat()
        textura2RDry = img.select('red_median_dry').glcmTexture(3)  
        contrastredDry = textura2RDry.select('red_median_dry_contrast').toFloat()

        return  img.addBands(contrastnir).addBands(contrastred
                        ).addBands(contrastnirDry).addBands(contrastredDry)

    #endregion


    def get_class_maskFire(self, yyear):
        maskFireyyear = ee.Image(self.options['asset_fire']).select("burned_area_" + str(yyear)
                                    ).unmask(0).eq(0).rename('mask_fire')

        return maskFireyyear

    def CalculateIndice(self, imagem):

        band_feat = [
                "ratio","rvi","ndwi","awei","iia","evi",
                "gcvi","gemi","cvi","gli","shape","afvi",
                "avi","bsi","brba","dswi5","lswi","mbi","ui",
                "osavi","ri","brightness","wetness","gvmi",
                "nir_contrast","red_contrast"
            ]        

        imageW = self.agregateBandsIndexEVI(imagem)
        imageW = self.agregateBandsIndexRATIO(imageW)  #
        imageW = self.agregateBandsIndexRVI(imageW)    #    
        imageW = self.agregateBandsIndexWater(imageW)  #   
        imageW = self.agregateBandsIndexGVMI(imageW)
        imageW = self.AutomatedWaterExtractionIndex(imageW)  #      
        imageW = self.IndiceIndicadorAgua(imageW)    #      
        imageW = self.agregateBandsIndexGCVI(imageW)   #   
        imageW = self.agregateBandsIndexGEMI(imageW)
        imageW = self.agregateBandsIndexCVI(imageW) 
        imageW = self.agregateBandsIndexGLI(imageW) 
        imageW = self.agregateBandsIndexShapeI(imageW) 
        imageW = self.agregateBandsIndexAFVI(imageW) 
        imageW = self.agregateBandsIndexAVI(imageW) 
        imageW = self.agregateBandsIndexBSI(imageW) 
        imageW = self.agregateBandsIndexBRBA(imageW) 
        imageW = self.agregateBandsIndexDSWI5(imageW) 
        imageW = self.agregateBandsIndexLSWI(imageW) 
        imageW = self.agregateBandsIndexMBI(imageW) 
        imageW = self.agregateBandsIndexUI(imageW) 
        imageW = self.agregateBandsIndexRI(imageW) 
        imageW = self.agregateBandsIndexOSAVI(imageW)  #     
        imageW = self.agregateBandsIndexwetness(imageW)   #   
        imageW = self.agregateBandsIndexBrightness(imageW)  #       
        imageW = self.agregateBandsTexturasGLCM(imageW)     #

        return imageW#.select(band_feat)# .addBands(imageF)


    def calculate_indices_x_blocos(self, image):
        
        # band_year = [bnd + '_median' for bnd in self.option['bnd_L']]
        band_year = ['blue_median','green_median','red_median','nir_median','swir1_median','swir2_median']
        band_drys = [bnd + '_median_dry' for bnd in self.options['bnd_L']]    
        band_wets = [bnd + '_median_wet' for bnd in self.options['bnd_L']]
        band_std = [bnd + '_stdDev'for bnd in self.options['bnd_L']]
        band_features = [
                    "ratio","rvi","ndwi","awei","iia",
                    "gcvi","gemi","cvi","gli","shape","afvi",
                    "avi","bsi","brba","dswi5","lswi","mbi","ui",
                    "osavi","ri","brightness","wetness",
                    "nir_contrast","red_contrast"] # ,"ndfia"
        # band_features.extend(self.option['bnd_L'])        
        
        image_year = image.select(band_year)
        image_year = image_year.select(band_year, self.options['bnd_L'])
        # print("imagem bandas index ")    
        # print("  ", image_year.bandNames().getInfo())
        image_year = self.CalculateIndice(image_year)    
        # print("imagem bandas index ")    
        # print("  ", image_year.bandNames().getInfo())
        bnd_corregida = [bnd + '_median' for bnd in band_features]
        image_year = image_year.select(band_features, bnd_corregida)
        # print("imagem bandas final median \n ", image_year.bandNames().getInfo())

        image_drys = image.select(band_drys)
        image_drys = image_drys.select(band_drys, self.options['bnd_L'])
        image_drys = self.CalculateIndice(image_drys)
        bnd_corregida = [bnd + '_median_dry' for bnd in band_features]
        image_drys = image_drys.select(band_features, bnd_corregida)
        # print("imagem bandas final dry \n", image_drys.bandNames().getInfo())

        image_wets = image.select(band_wets)
        image_wets = image_wets.select(band_wets, self.options['bnd_L'])
        image_wets = self.CalculateIndice(image_wets)
        bnd_corregida = [bnd + '_median_wet' for bnd in band_features]
        image_wets = image_wets.select(band_features, bnd_corregida)
        # print("imagem bandas final wet \n ", image_wets.bandNames().getInfo())

        # image_std = image.select(band_std)
        # image_std = self.match_Images(image_std)
        # image_std = self.CalculateIndice(image_std)
        # bnd_corregida = ['stdDev_' + bnd for bnd in band_features]
        # image_std = image_std.select(band_features, bnd_corregida)        

        image_year =  image_year.addBands(image_drys).addBands(image_wets)#.addBands(image_std)
        return image_year

    def get_mask_Fire_estatics_pixels(self, yyear, exportFire):
        janela = 5        
        imgColFire = ee.ImageCollection( self.options['asset_fire']).filter(
                            ee.Filter.eq('biome', 'CAATINGA'))                            
        # print("image Fire imgColFire ", imgColFire.size().getInfo())
        intervalo_years = [kk for kk in self.lst_year if kk <= yyear and kk > yyear - janela]
        # print(intervalo_years)
        # sys.exit()
        imgTemp = imgColFire.filter(ee.Filter.inList('year', intervalo_years)
                                        ).sum().unmask(0).gt(0)
        # print("image Fire imgTemp ", imgTemp.size().getInfo())

        #@reducida: cria uma imagem que cada pixel diz quanto variou entre todas as bandas
        imgTemp = imgTemp.rename('fire_'+ str(yyear)).set('type', 'fire', 'year', yyear)

        name_exportimg = 'masks_fire_wind5_' + str(yyear)
        if exportFire:
            self.processoExportarImage(imgTemp,  name_exportimg, self.regionInterest.geometry(), 'fire')
        else:
            return imgTemp

    # https://code.earthengine.google.com/d5a965bbb6b572306fb81baff4bd401b
    def get_class_maskAlerts(self, yyear):
        #  get from ImageCollection 
        janela = 5
        intervalo_bnd_years = ['classification_' + str(kk) for kk in self.lst_year[1:] if kk <= yyear and kk > yyear - janela]
        maskAlertyyear = ee.Image(self.options['asset_alerts_Desf']).select(intervalo_bnd_years)\
                                    .divide(100).toUint16().eq(4).reduce(ee.Reducer.sum())
        return maskAlertyyear.eq(0).rename('mask_alerta')    
    
    def iterate_bacias(self, nomeBacia):
        
        for nDiv in [0, 1]:
            # loading geometry bacim
            nomeBaciaEx = nomeBacia + '_' + str(nDiv)

            # oneBacia = self.baciasN2.filter(ee.Filter.eq('nunivotto3', nomeBacia)).geometry()     
            oneBacia = ee.FeatureCollection(self.options['asset_cruzN245']).filter(
                                            ee.Filter.eq('wts_cd_pfa', nomeBaciaEx)).geometry()  

            for anoCount in self.lst_year:    

                print(" processing bacia_year => ",  " <> ", anoCount)             
                bandActiva = 'classification_' + str(anoCount)

                m_assetPixEst = self.options['asset_estaveis'] + '/masks_estatic_pixels_'+ str(anoCount)
                maksEstaveis = ee.Image(m_assetPixEst).rename('estatic')  
                 # 1 Concordante, 2 concordante recente, 3 discordante recente,
                # 4 discordante, 5 muito discordante
                if anoCount < 2022:
                    asset_PixCoinc = self.options['asset_Coincidencia'] + '/masks_pixels_incidentes_'+ str(anoCount)
                    imMasCoinc = ee.Image(asset_PixCoinc).rename('coincident') 
                # mask de fogo com os ultimos 5 anos de fogo mapeado 
                imMaskFire = self.get_mask_Fire_estatics_pixels(anoCount, False)
                imMaskFire = ee.Image(imMaskFire)

                if anoCount > 1985:
                    imMaksAlert = self.get_class_maskAlerts(anoCount)
                elif anoCount >= 2020:
                    imMaksAlert = self.AlertasSAD  
                else:
                    imMaksAlert = ee.Image.constant(1).rename('mask_alerta')   

                map_yearAct = self.imgMapbiomas.select(bandActiva).rename(['class'])
                areaColeta = maksEstaveis.multiply(imMaskFire).multiply(imMaksAlert) \
                                .multiply(imMasCoinc.lt(3))
                areaColeta = areaColeta.eq(1) # mask of the area for colects
                
                map_yearAct = map_yearAct.addBands(
                                        ee.Image.constant(int(anoCount)).rename('year')).addBands(
                                            imMasCoinc) 

                img_recMosaic = self.imgMosaic.filter(ee.Filter.eq('year', anoCount)
                                        ).filterBounds(oneBacia).median() 
                # print("size ", img_recMosaic.size().getInfo())  
                # print("metadato ", img_recMosaic.first().getInfo())

                # print("img_recMosaic   ", img_recMosaic.bandNames().getInfo())
                img_recMosaicnewB = self.CalculateIndice(img_recMosaic)
                # bndAdd = img_recMosaicnewB.bandNames().getInfo()
                
                # print(f"know bands names {len(bndAdd)}")
                # print("  ", bndAdd)

                img_recMosaic = img_recMosaic.addBands(ee.Image(img_recMosaicnewB)).addBands(map_yearAct)
                img_recMosaic = img_recMosaic.updateMask(areaColeta)
                # print("numero de ptos controle ", roisAct.size().getInfo())
                # opcoes para o sorteio estratificadoBuffBacia
                # sampleRegions()
                # sample(region, scale, projection, factor, numPixels, seed, dropNulls, tileScale, geometries)
                ptosTemp = img_recMosaic.sample(
                                    region=  oneBacia,                              
                                    scale= 30,   
                                    numPixels= 15000,
                                    dropNulls= True,
                                    # tileScale= 2,                             
                                    geometries= True
                                )
                # insere informacoes em cada ft

                # merge com colecoes anteriores
                # colecaoPontos = colecaoPontos.merge(ptosTemp)            
                # sys.exit()
                name_exp = str(nomeBaciaEx) + "_" + str(anoCount) + "_wl" 
                self.save_ROIs_toAsset(ee.FeatureCollection(ptosTemp), name_exp)        
            

    # salva ftcol para um assetindexIni
    # lstKeysFolder = ['cROIsN2manualNN', 'cROIsN2clusterNN'] 
    def save_ROIs_toAsset(self, collection, name):

        nfolder = "ROIsnotWithLabel"
        optExp = {
            'collection': collection,
            'description': name,
            'assetId': self.options['outAssetROIs'] + nfolder + "/" + name
        }

        task = ee.batch.Export.table.toAsset(**optExp)
        task.start()
        print("exportando ROIs da bacia $s ...!", name)


print("len arqParam ", len(arqParam.featuresreduce))

param = {
    'bioma': ["CAATINGA", 'CERRADO', 'MATAATLANTICA'],
    'asset_bacias': 'projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga',
    'asset_IBGE': 'users/SEEGMapBiomas/bioma_1milhao_uf2015_250mil_IBGE_geo_v4_revisao_pampa_lagoas',
    'outAssetROIs': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/',
    # 'outAsset': 'projects/mapbiomas-workspace/AMOSTRAS/col5/CAATINGA/PtosXBaciasBalanceados/',
    'asset_ROIs_manual': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/ROIs/coletaROIsv7N2manual'},
    'asset_ROIs_cluster': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/ROIs/coletaROIsv6N2cluster'},
    'asset_ROIs_automatic': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/ROIs/coletaROIsv1N245'},
    'showAssetFeat': True,
    'janela': 5,
    'escala': 30,
    'sampleSize': 0,
    'metodotortora': True,
    'tamROIsxClass': 4000,
    'minROIs': 1500,
    # "anoColeta": 2015,
    'anoInicial': 1985,
    'anoFinal': 2022,
    'sufix': "_1",
    'numeroTask': 6,
    'numeroLimit': 36,
    'conta': {
        '0': 'caatinga01',
        '6': 'caatinga02',
        '12': 'caatinga03',
        '18': 'caatinga04',
        '24': 'caatinga05',
        '30': 'solkan1201',
        # '24': 'diegoGmail',
        # '20': 'rodrigo'
    },
}
def gerenciador(cont, param):

    numberofChange = [kk for kk in param['conta'].keys()]

    if str(cont) in numberofChange:

        gee.switch_user(param['conta'][str(cont)])
        gee.init()
        gee.tasks(n=param['numeroTask'], return_list=True)

    elif cont > param['numeroLimit']:
        cont = 0

    cont += 1
    return cont

def GetPolygonsfromFolder(dictAsset):    
    getlistPtos = ee.data.getList(dictAsset)
    ColectionPtos = []
    # print("bacias vizinhas ", nBacias)

    for idAsset in tqdm(getlistPtos):         
        path_ = idAsset.get('id')        
        ColectionPtos.append(path_) 
        name = path_.split("/")[-1]
        if param['showAssetFeat']:
            print("Reading ", name)
        
    return ColectionPtos

def compare_nameFilefromAssets(assetsgeeSource, assetsgeeTarge):

    listTarge = []
    lstOut = []
    pathroot = None
    print("reading all list ...")
    for idAsset in tqdm(assetsgeeTarge):  
        name = idAsset.split("/")[-1] 
        name = name.replace("_0", "").replace("_1", "")
        listTarge.append(name)
    print("list ROIs bacin did\n =>", listTarge)
    for idAsset in tqdm(assetsgeeSource):  
        name = idAsset.split("/")[-1]        
        if name not in listTarge: 
            print("    >> ", name)
            lstOut.append(idAsset)    
    
    return lstOut 

def getListBaciasSaved (nList):
    lstB = []
    dictBacin = {}
    for namef in nList:
        nameB = namef.split("/")[-1].split("_")[0]
        if nameB not in lstB:
            lstB.append(nameB)
            dictBacin[nameB] = 1
        else:
            dictBacin[nameB] += 1
    for cc, nameB in enumerate(lstB):
        print("# ", cc, "  ", nameB, "  ", dictBacin[nameB])
        if dictBacin[nameB] < 37:
            lstB.remove(nameB)
    return lstB

listaNameBacias = [
    '741','7421','7422','744','745','746','7492','751','752','753',
    '754','755','756','757','758','759','7621','7622','763','764',
    '765','766','767','771','772','773', '7741','7742','775','776',
    '777','778','76111','76116','7612','7614','7615','7616','7617',
    '7618','7619', '7613'
]
# listaNameBacias = ['765','766','759','7619','7422']
cont = gerenciador(0, param)
# revisao da coleção 8 
# https://code.earthengine.google.com/5e8af5ef94684a5769e853ad675fc368

lstKeysFolder = ['cROIsN245red_allBND']  # , , 'asset_ROIs_manual', 'asset_ROIs_cluster'
dictKeysF = {
    'asset_ROIs_manual': "coletaROIsNormN2manual",
    'asset_ROIs_cluster': "coletaROIsNormN2cluster",
    'asset_ROIs_automatic': "cROIsN245red_allBND"
}

    
objetoMosaic_exportROI = ClassMosaic_indexs_Spectral()
for cc, item_bacia in enumerate(listaNameBacias[:]):
    print(f"# {cc + 1} loading geometry bacia {item_bacia}")     
    # geobacia, colAnos, nomeBacia, dict_nameBN4
    objetoMosaic_exportROI.iterate_bacias(item_bacia)
    # sys.exit()
    cont = gerenciador(cont, param)

# sys.exit()

