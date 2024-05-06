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
sys.setrecursionlimit(1000000000)

# table registros 
# https://docs.google.com/spreadsheets/d/11L_wTnkmjW9nRK7UgP6q6fkBOk8dElEyeQ3gnnJ2vUg/edit#gid=1999040808

param = {
    'inputAssetpolg': {'id':'users/CartasSol/coleta/polygonsCorr'},
    'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrograficaCaatbuffer5k',
    'assetMap': 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1',
    'input_assetV10': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/Temporal/',
    'input_assetV5': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/CLASS/ClassCol8V5/',
    'input_solo': 'users/diegocosta/doctorate/Bare_Soils_Caatinga',
    'outputAsset': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/misto/',
    'year_first': 1985,
    'year_end': 2022,
    'classMapB': [3, 4, 5, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62],
    'classNew':  [3, 4, 3, 3,12,12,21,21,21,21,21,22,22,22,22,33,29,22,33,12,33, 21,33,33,21,21,21,21,21,21,21,21,21,21, 4,12,21]
}
nameBacias = [
    '741','7421','7422','744','745','746','7492','751','752','753',
    '754','755','756','757','758','759','7621','7622','763','764',
    '765','766','767','771','772','773', '7741','7742','775','776',
    '777','778','76111','76116','7612','7614','7615','7616','7617',
    '7618','7619', '7613'
]

dict_Bacia_version = {
    '741': 'V5',
    '7421': 'V5',
    '7422': 'V5',
    '744': 'V5',
    '745': 'V5',
    '746': 'V5',
    '7492': 'V10',
    '751': 'V10',
    '752': 'V10',
    '753': 'V5',
    '754': 'V5',
    '755': 'V5',
    '756': 'V10',
    '757': 'V10',
    '758': 'V5',
    '759': 'V5',
    '7621': 'V5',
    '7622': 'V5',
    '763': 'V5',
    '764': 'V5',    
    '765': 'V10',
    '766': 'V5',
    '767': 'V5',
    '771': 'V5',
    '772': 'V5',
    '773': 'V5',
    '7741': 'V5',
    '7742': 'V5',
    '775': 'V5',
    '776': 'V5',
    '777': 'V5',
    '778': 'V5',
    '76111': 'V5',
    '76116': 'V5',
    '7612': 'V10',
    '7614': 'V10',
    '7615': 'V10',
    '7616': 'V10',
    '7617': 'V5',
    '7618': 'V10',
    '7619': 'V5',
    '7613': 'V5'
}
dict_version ={
    'V5': 'V1',
    'V10': 'V1' 
}
dict_class = {
    '3':  'Forest Formation',
    '4':  'Savanna Formation',
    '12': 'Grassland',
    '21': 'Mosaic of Uses',
    '22': 'Non vegetated area',
    '29': 'Rocky Outcrop',
    '33': 'Water',
    '50': 'restinga',
    '49': 'restinga',
    '48': 'Lavouras Perenes',
    '9' : 'Forest Plantation'
}
lst_Bacia_aflo = [
    '741','7421','7422','744','745','746','7492',
    '754','755','756','758','759','7621','763',
    '764','765','766','767','771','772','773','7741',
    '7742','776','777','778','76111','7614','7615',
    '7616','7617','7618','7619','7613'
]
lst_bacias_restinga = ["757","755","754","753"]
lst_bacias_relebo = [
    '741', '7421', '7422', '744', '745', '746', '7492', '751', '752', 
    '753', '754', '756', '7621', '763', '765', '771', '772', '773', 
    '7741', '7742', '776', '7612', '7615', '7619', '7613'
]

def GetPolygonsfromFolder():

    getlistPtos = ee.data.getList(param['inputAssetpolg'])    
    dict_pol = {}
    # 'idBacia': ,'de': 'c8','fCol': ,'para': ,'eCol': 'c8' or 'c71
    for idAsset in getlistPtos:   
        print(" ", idAsset.get('id'))
        if '_v2' in idAsset.get('id'):      
            path_ = idAsset.get('id')
            lsFile =  path_.split("/")
            name = lsFile[-1]
            nameBacia = name.split('_')[1]
            dict_pol[nameBacia] = path_

    return  dict_pol

def corregir_pixels_inPol_inColecao(imgClass_temp, bufferBacia, polRecort, dictProp, nameBac):
    print("properties ", dictProp)
    
    lstBandNames = ['classification_' + str(yy) for yy in range(param['year_first'], param['year_end'] + 1)]
    imgClassFinal = ee.Image().toByte();
    areaFixa = ee.Feature(bufferBacia.difference(polRecort), {'value': 1})
    areaToChange = ee.Feature(polRecort, {'value': 0})
    areaTo_mask = ee.FeatureCollection([areaFixa, areaToChange])
    img_mask_err = areaTo_mask.reduceToImage(['value'], ee.Reducer.first())

    if dictProp['para'] == 1:
        dictProp['para'] = 21
    classDe = dict_class[str(dictProp['de'])]
    classPara = dict_class[str(dictProp['para'])]
    for yyear in range(param['year_first'], param['year_end'] + 1):
        
        print(f"###### change pixels from {classDe} TO {classPara} in year [{yyear}] ########")
        bandaAct = 'classification_' + str(yyear) 
        
        imgClasBand = ee.Image(imgClass_temp.select(bandaAct)).remap(
                        param['classMapB'], param['classNew']);
        # https://code.earthengine.google.com/b5d40873094cb56a881c3df3e5e2ea16          
        
        maskToChange = img_mask_err.eq(0) 
        mapRecCorregir = imgClasBand.updateMask(maskToChange).unmask(0)
        
        # {'de': 3, 'eCol': 'c8', 'fCol': 'c8', 'idBacia': '757', 'para': 21}
        # image binaria com a classe a change
        mapaBinarioDe = mapRecCorregir.eq(dictProp['de']) 
        imgClasBand = imgClasBand.where(mapaBinarioDe.eq(1), mapaBinarioDe.multiply(dictProp['para']))
        
        bandaAct = 'classification_' + str(yyear)
        imgClassFinal = imgClassFinal.addBands(imgClasBand.rename(bandaAct))

    imgClassFinal = imgClassFinal.select(lstBandNames)
    imgClassFinal = imgClassFinal.set(
                        'version', 5, 'biome', 'CAATINGA',
                        'collection', '8.0', 'id_bacia', nameBac,
                        'sensor', 'Landsat', 'source','geodatin',
                        'system:footprint', imgClass_temp.get('system:footprint')
                    )
    
    return imgClassFinal

def corregir_pixels_inPol_BetwenColecao(imgClass_temp, bufferBacia, polRecort, dictProp, nameBac):

    mapColBefore = ee.Image(param['assetMap'])
    # nlstBandNames = ['classification_' + str(yy) + '_O' for yy in range(param['year_first'], param['year_end'] + 1)]    
    lstBandNames = ['classification_' + str(yy) for yy in range(param['year_first'], param['year_end'] + 1)]
    # imgClass_temp = imgClass_temp.rename(nlstBandNames)
    imgClassFinal = ee.Image().toByte();

    classDe = dict_class[str(dictProp['de'])]
    classPara = dict_class[str(dictProp['para'])]

    areaFixa = ee.Feature(bufferBacia.difference(polRecort), {'value': 1})
    areaToChange = ee.Feature(polRecort, {'value': 0})
    areaTo_mask = ee.FeatureCollection([areaFixa, areaToChange])
    img_mask_err = areaTo_mask.reduceToImage(['value'], ee.Reducer.first())
    maskToChange = img_mask_err.eq(0) 
    

    for yyear in range(param['year_first'], param['year_end'] + 1):
        
        print(f"###### change pixels from {classDe} Col 7 TO {classPara} col8 in year [{yyear}] ########")        
        bandaAct = 'classification_' + str(yyear)
        if yyear == 2022:
            imClassRef = mapColBefore.select('classification_2021')
        else:
            imClassRef = mapColBefore.select(bandaAct)
        imgClasBand = ee.Image(imgClass_temp.select(bandaAct)).remap(
                                                param['classMapB'], param['classNew'])
        mapRecCorregir = imClassRef.updateMask(maskToChange).unmask(0)
        
        # {'de': 3, 'eCol': 'c8', 'fCol': 'c8', 'idBacia': '757', 'para': 21}
        mapaBinarioDe = mapRecCorregir.eq(dictProp['de'])
        imgClasBand = imgClasBand.where(mapaBinarioDe.eq(1), imClassRef)

        imgClassFinal = imgClassFinal.addBands(imgClasBand.rename(bandaAct))

    # print("todas as bandas ", imgClassFinal.bandNames().getInfo())

    imgClassFinal = imgClassFinal.select(lstBandNames)
    imgClassFinal = imgClassFinal.set(
                        'version', 5, 'biome', 'CAATINGA',
                        'collection', '8.0', 'id_bacia', nameBac,
                        'sensor', 'Landsat', 'source','geodatin',
                        'system:footprint', imgClass_temp.get('system:footprint')
                    )
    return imgClassFinal

def corregir_pixels_BetwenColecao(imgClass_temp, bufferBacia, CC, nameBac):
    print("change classe Campo ")
    mapColBefore = ee.Image(param['assetMap'])
   
    lstBandNames = ['classification_' + str(yy) for yy in range(param['year_first'], param['year_end'] + 1)]
    imgClassFinal = ee.Image().toByte();
    
    for yyear in range(param['year_first'], param['year_end'] + 1):
        
        print(f"###### change pixels from Col 7 TO col8 in year [{yyear}] ########")
        bandaAct = 'classification_' + str(yyear)
        if yyear == 2022:
            imClassRef = mapColBefore.select('classification_2021')
        else:
            imClassRef = mapColBefore.select(bandaAct)

        imClassRef = imClassRef.remap(param['classMapB'], param['classNew'])
        imgClasBand = ee.Image(imgClass_temp.select(bandaAct)).remap(
                            param['classMapB'], param['classNew'])

        # {'de': 3, 'eCol': 'c8', 'fCol': 'c8', 'idBacia': '757', 'para': 21}
        mapaBinarioDe = imClassRef.eq(CC)
        imgClasBand = imgClasBand.where(mapaBinarioDe.eq(1), imClassRef)
        
        bandaAct = 'classification_' + str(yyear)
        imgClassFinal = imgClassFinal.addBands(imgClasBand.rename(bandaAct))

    imgClassFinal = imgClassFinal.select(lstBandNames)
    imgClassFinal = imgClassFinal.set(
                        'version', 5, 'biome', 'CAATINGA',
                        'collection', '8.0', 'id_bacia', nameBac,
                        'sensor', 'Landsat', 'source','geodatin',
                        'system:footprint', imgClass_temp.get('system:footprint')
                    )
    return imgClassFinal


def corregir_pixels_Aflora(imgClass_temp, bufferBacia, maskAflo,nameBac):
    rec_maskAflo = maskAflo.clip(bufferBacia)

    lstBandNames = ['classification_' + str(yy) for yy in range(param['year_first'], param['year_end'] + 1)]
    imgClassFinal = ee.Image().toByte();

    for yyear in range(param['year_first'], param['year_end'] + 1):
        print("###### change pixels Afloramento in year [{}] ########".format(yyear))
        bandaAct = 'classification_' + str(yyear)
        imgClasBand = ee.Image(imgClass_temp.select(bandaAct)).remap(
                            param['classMapB'], param['classNew'])

        imgClasBand = imgClasBand.where(rec_maskAflo.eq(1), rec_maskAflo.multiply(29))
        bandaAct = 'classification_' + str(yyear)
        imgClassFinal = imgClassFinal.addBands(imgClasBand.rename(bandaAct))

    imgClassFinal = imgClassFinal.select(lstBandNames)
    imgClassFinal = imgClassFinal.set(
                        'version', 5, 'biome', 'CAATINGA',
                        'collection', '8.0', 'id_bacia', nameBac,
                        'sensor', 'Landsat', 'source','geodatin',
                        'system:footprint', imgClass_temp.get('system:footprint')
                    )
    return imgClassFinal

def corregir_pixels_inPol_Restinga(imgClass_temp, bufferBacia, polRestinga,nameBac):
    polRestinga = ee.Geometry(polRestinga)
    lstBandNames = ['classification_' + str(yy) for yy in range(param['year_first'], param['year_end'] + 1)]
    imgClassFinal = ee.Image().toByte();

    # https://code.earthengine.google.com/9d2e4142f4f249c9bc116c1790d15bfb          
    areaFixa = ee.Feature(bufferBacia.difference(polRestinga), {'value': 1})
    areaToChange = ee.Feature(polRestinga, {'value': 0})
    areaTo_mask = ee.FeatureCollection([areaFixa, areaToChange])
    img_mask_err = areaTo_mask.reduceToImage(['value'], ee.Reducer.first())
    maskToChange = img_mask_err.eq(0) 

    for yyear in range(param['year_first'], param['year_end'] + 1):
        print("###### change pixels Restinga in year [{}] ########".format(yyear))
        bandaAct = 'classification_' + str(yyear)
        imgClasBand = ee.Image(imgClass_temp.select(bandaAct)).remap(
                            param['classMapB'], param['classNew'])
        
        mapRecCorregir = imgClasBand.updateMask(maskToChange).unmask(0)
        
        # {'de': 3, 'eCol': 'c8', 'fCol': 'c8', 'idBacia': '757', 'para': 21}
        # image binaria com a classe a change
        mapaBinarioDe12 = mapRecCorregir.eq(12) 
        mapaBinarioDe3 = mapRecCorregir.eq(3)
        mapaBinarioDe49 = mapRecCorregir.eq(49)
        mapaBinarioDe = mapaBinarioDe3.add(mapaBinarioDe12).add(mapaBinarioDe49).gt(0)
        imgClasBand = imgClasBand.where(mapaBinarioDe.eq(1), mapaBinarioDe.multiply(50))
        
        bandaAct = 'classification_' + str(yyear)
        imgClassFinal = imgClassFinal.addBands(imgClasBand.rename(bandaAct))

    imgClassFinal = imgClassFinal.select(lstBandNames)
    imgClassFinal = imgClassFinal.set(
                        'version', 5, 'biome', 'CAATINGA',
                        'collection', '8.0', 'id_bacia', nameBac,
                        'sensor', 'Landsat', 'source','geodatin',
                        'system:footprint', imgClass_temp.get('system:footprint')
                    )
    return imgClassFinal

def corregir_pixels_inPol_Relevo(imgClass_temp, bufferBacia, polRelevo,nameBac):

    lstBandNames = ['classification_' + str(yy) for yy in range(param['year_first'], param['year_end'] + 1)]
    imgClassFinal = ee.Image().toByte();    
    
    # https://code.earthengine.google.com/b5d40873094cb56a881c3df3e5e2ea16       
    areaFixa = ee.Feature(bufferBacia.difference(polRelevo), {'value': 1})
    areaToChange = ee.Feature(polRelevo, {'value': 0})
    areaTo_mask = ee.FeatureCollection([areaFixa, areaToChange])
    img_mask_err = areaTo_mask.reduceToImage(['value'], ee.Reducer.first())

    maskToChange = img_mask_err.eq(0) 

    for yyear in range(param['year_first'], param['year_end'] + 1):
        print("###### change pixels with Relevo in year [{}] ########".format(yyear))
        bandaAct = 'classification_' + str(yyear)
        imgClasBand = ee.Image(imgClass_temp.select(bandaAct)).remap(
                            param['classMapB'], param['classNew'])       
        
        mapRecCorregir = imgClasBand.updateMask(maskToChange).unmask(0)
        
        # {'de': 3, 'eCol': 'c8', 'fCol': 'c8', 'idBacia': '757', 'para': 21}
        # image binaria com a classe a change
        mapaBinarioDe3 = mapRecCorregir.eq(3) 
        mapaBinarioDe33 = mapRecCorregir.eq(33)
        mapaBinarioDe = mapaBinarioDe3.add(mapaBinarioDe33).gt(0)
        imgClasBand = imgClasBand.where(mapaBinarioDe.eq(1), mapaBinarioDe.multiply(4))
        
        bandaAct = 'classification_' + str(yyear)
        imgClassFinal = imgClassFinal.addBands(imgClasBand.rename(bandaAct))

    imgClassFinal = imgClassFinal.select(lstBandNames)
    imgClassFinal = imgClassFinal.set(
                        'version', 5, 'biome', 'CAATINGA',
                        'collection', '8.0', 'id_bacia', nameBac,
                        'sensor', 'Landsat', 'source','geodatin',
                        'system:footprint', imgClass_temp.get('system:footprint')
                    )
    return imgClassFinal


#exporta a imagem classificada para o asset
def processoExportar(mapaRF,  nomeDesc, geom_bacia):
    
    idasset =  param['outputAsset'] + nomeDesc
    optExp = {
        'image': mapaRF, 
        'description': nomeDesc, 
        'assetId': idasset, 
        'region': ee.Geometry(geom_bacia), #  .getInfo()['coordinates']
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

## ============================================================##
## ==================LOADING ALL DATASETS =====================##
## ============================================================##

dict_bacias_asset = GetPolygonsfromFolder()
lst_keyBacias = [kk for kk in dict_bacias_asset.keys()]
print('liat de bacias ', lst_keyBacias)
# polg_sombra = ee.FeatureCollection(param['asset_florestErrNe']).merge(
#                         ee.FeatureCollection(param['asset_florestErrRa'])).geometry()
# polg_restinga = ee.FeatureCollection(param['asset_restingaNeri']).merge(
#                         ee.FeatureCollection(param['asset_restingaRafa'])).geometry()
# mask_afloramento = ee.Image(param['asset_mask_aflora'])


geoBacias = ee.FeatureCollection(param['asset_bacias_buffer'])
nameBacias = ['7616','7618','7741','7742'] # ,'746','778''76116'
# list_corr = ['76116','7612','7613', '7614', '752','753','746', '7422', '754','756','757']
list_corr = []
for nameBa in  nameBacias[:]:
    print("  dict_Bacia_version[nameBa] ", dict_Bacia_version[nameBa])
    
    # name_imgClass = 'filter_BACIA_' + nameBa + "_" + dict_version[dict_Bacia_version[nameBa]]  
    if  dict_Bacia_version[nameBa] == 'V5':
        print('entrou ')
        name_imgClass = 'BACIA_' + nameBa + "_GTB_col8" 
        imgClass = ee.Image(param['input_assetV5'] + name_imgClass)        
        
    else:
        # name_imgClass = 'BACIA_' + nameBa + "_RF_col8" 
        # imgClass = ee.Image(param['input_assetV10'] + name_imgClass)  
        print("rodando a V10")
        name_imgClass = 'filterTP_BACIA_' + nameBa + "_V7"
        imgClass = ee.Image(param['input_assetV10'] + name_imgClass)
    # sys.exit()
    print("Bacia ", nameBa, " => numero de bandas ", len(imgClass.bandNames().getInfo()))
    limBacia = geoBacias.filter(ee.Filter.eq('nunivotto3', nameBa)).geometry()
    # print(lst_keyBacias)
    print("entrar no loop ", nameBa in lst_keyBacias)
    
    if nameBa in lst_keyBacias : # and nameBa not in list_corr
        print("Bacia IS ")
        # try: 
        feat_pog = ee.FeatureCollection(dict_bacias_asset[nameBa])           
        size_pol = feat_pog.size().getInfo()
        print("      size ", size_pol)
        
        if size_pol == 1:
            dictPropert = feat_pog.first().getInfo()['properties']
            print("polygon = ", dictPropert)
            
            imgBaClass = corregir_pixels_inPol_inColecao(imgClass, limBacia, feat_pog.first().geometry(), dictPropert, nameBa)
            
        # except:
        #     print("   ENTRPU AQUI A TROCAR O CAMPO ")
        #     imgBaClass = corregir_pixels_BetwenColecao(imgClass, limBacia, 12)
    
    



    # if nameBa in lst_bacias_relebo:
    #     imgBaClass = corregir_pixels_inPol_Relevo(imgBaClass, limBacia, polg_sombra)

    name_imgClass = 'BACIA_corr_mista_' + nameBa + "_V3"
    processoExportar(imgBaClass.clip(limBacia),  name_imgClass, limBacia)