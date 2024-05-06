
#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
'''

import ee 
import gee
import sys
import copy
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
    'assetSolo': 'projects/nexgenmap/MapBiomas2/LANDSAT/DEGRADACAO/LAYER_SOILV4', 
    'assetBacia': "projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga",    
    'assetbaciasJoined': 'projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatingaUnion',
    'asset_output': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/layerSoilbyBasin',
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


def processing_soil_layer(idBasin, lstBands):
    geomBacia = ee.FeatureCollection(param['asset_bacias_buffer']).filter(
                        ee.Filter.eq('nunivotto3', idBasin)).geometry()
    bandaAntiga = None
    imgColSolo = ee.ImageCollection(param['assetSolo'])
    imgOutput = ee.Image().byte()
    for yyear in range(param['first_year'], param['last_year'] + 1):
        bandAct = 'classification_' + str(yyear)
        if yyear < 2023:
            colSoilYY = imgColSolo.filter(ee.Filter.eq('year', yyear))\
                                    .filterBounds(geomBacia)
            numberImg = colSoilYY.size().getInfo()
            print("número de imagens ", numberImg)
            if numberImg > 1:
                colSoilYY = colSoilYY.map(lambda img: img.select([0], ['class']).gt(0.6).selfMask())
                imgSoilYY = ee.Image.cat(colSoilYY.max())
        try:
            imgOutput = imgOutput.addBands(imgSoilYY.rename(bandAct))
            if bandaAntiga:
                imgOutput = imgOutput.addBands(imgSoilYY.rename(bandaAntiga))
        except:
            bandaAntiga = copy.deepcopy(bandAct)


    imgOutput = imgOutput.select(lstBands)
    imgOutput = imgOutput.set(
                            'version',  4, 
                            'biome', 'CAATINGA',
                            'layer', 'soil',
                            'collection', '9.0',
                            'id_bacia', idBasin,
                            'sensor', 'Landsat',
                            'system:footprint' , geomBacia
                        )
    name_toexport= 'layer_soil_' + str(idBasin) + 'v4'
    # print("imageOutput ", imgOutput.bandNames().getInfo())
    processoExportar(imgOutput, name_toexport, geomBacia)                            


#exporta a imagem classificada para o asset
def processoExportar(mapaRF,  nomeDesc, geom_bacia):
    
    idasset =  param['asset_output'] + nomeDesc
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

        
listaNameBacias = [
    # '741','7421','7422','744','745','746','7492','751','752',
    # '753', '755','758', '759', ojo
    '7621','7622','764','765',
    '766','767','771','772','7741','7742','773','775','776',
    '777','778','76111','76116','7612','7614','7615','7616',
    '7617','7618','7619', '7613',
    '754','756','757','763'
]

listaBandas = [ 'classification_' + str(yyear) for yyear in range(param['first_year'], param['last_year'] + 1)]
cont = 0
for cc, idbacia in enumerate(listaNameBacias[:]):   
    print(f"----- {cc} PROCESSING BACIA {idbacia} -------")
    cont = gerenciador(cont)
    processing_soil_layer(idbacia, listaBandas)