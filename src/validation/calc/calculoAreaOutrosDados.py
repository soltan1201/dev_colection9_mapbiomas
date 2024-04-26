#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#  SCRIPT DE CALCULO DE AREA POR AREAS PRIORITARIAS DA CAATINGA
#  Produzido por Geodatin - Dados e Geoinformacao
#  DISTRIBUIDO COM GPLv2

#   Relação de camadas para destaques:
#   limite bioma Caatinga 
#   Novo limite do semiarido 2024
#   Camadas Raster:
#       Fogo
#       Agua
#       Alertas
#       Vegetação secundaria 

'''


import ee 
import sys
import arqParametros as arqParamet
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
    'asset_Cover_Col8': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',  
    'asset_transicao': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_transitions_v1',
    'asset_annual_water': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_water_collection2_annual_water_coverage_v1',
    'asset_desf_vegsec': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_deforestation_secondary_vegetation_v2',
    'asset_irrigate_agro': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_irrigated_agriculture_v1',
    "asset_semiarido2024": 'projects/mapbiomas-workspace/AUXILIAR/SemiArido_2024',
    "asset_biomas_250" : "projects/earthengine-legacy/assets/users/solkancengine17/shps_public/Im_bioma_250",
    'asset_fire_annual': 'projects/mapbiomas-workspace/FOGO_COL2/SUBPRODUTOS/mapbiomas-fire-collection2-annual-burned-v2',
    'asset_fire_acumulado': 'projects/mapbiomas-workspace/FOGO_COL2/SUBPRODUTOS/mapbiomas-fire-collection2-fire-frequency-coverage-v2',
    'scale': 30,
    'driverFolder': 'AREA-EXP-SEMIARIDO-24',
}

lst_nameAsset = [    
    # 'asset_annual_water',
    # 'asset_desf_vegsec',
    'asset_irrigate_agro',
    # 'asset_fire_annual',
    # 'asset_fire_acumulado'
]

##############################################
###     Helper function
###    @param item 
##############################################
def convert2featCollection (item):
    item = ee.Dictionary(item)
    feature = ee.Feature(ee.Geometry.Point([0, 0])).set(
        'classe', item.get('classe'),"area", item.get('sum'))
        
    return feature

#########################################################################
####     Calculate area crossing a cover map (deforestation, mapbiomas)
####     and a region map (states, biomes, municipalites)
####      @param image 
####      @param geometry
#########################################################################
# https://code.earthengine.google.com/5a7c4eaa2e44f77e79f286e030e94695
def calculateArea (image, pixelArea, geometry):

    pixelArea = pixelArea.addBands(image.rename('classe')).clip(geometry)#.addBands(
                                # ee.Image.constant(yyear).rename('year'))
    reducer = ee.Reducer.sum().group(1, 'classe')
    optRed = {
        'reducer': reducer,
        'geometry': geometry,
        'scale': param['scale'],
        'bestEffort': True, 
        'maxPixels': 1e13
    }    
    areas = pixelArea.reduceRegion(**optRed)

    areas = ee.List(areas.get('groups')).map(lambda item: convert2featCollection(item))
    areas = ee.FeatureCollection(areas)    
    return areas

# pixelArea, imgMapa, bioma250mil
# pixelArea, imgWater, limitGeometria, pref_bnd, nomegeometria, byYears, nameCSV
def iterandoXanoImCruda(imgAreaRef, mapaDelimitado, limite, preficoBnd, nameregion, porAno, nameExport):
    
    imgAreaRef = imgAreaRef.clip(limite)
    areaGeral = ee.FeatureCollection([])      
    print("Loadding image Cobertura Coleção 8 " )
    imgMapp = ee.Image(mapaDelimitado).clip(limite)  
    # print("---- SHOW ALL BANDS FROM MAPBIOKMAS MAPS -------\n ", imgMapp.bandNames().getInfo())

    for year in range(1985, 2023):          
        bandAct = preficoBnd + str(year)
        print(f" ========  🫵 processing year {year} for mapbiomas map ===== {bandAct}")
        newimgMap = imgMapp.select(bandAct)
        areaTemp = calculateArea (newimgMap, imgAreaRef, limite)        
        areaTemp = areaTemp.map( lambda feat: feat.set(
                                            'year', year, 
                                            'camada', preficoBnd[:-2],
                                            'region', nameregion                                               
                                        ))
        if porAno:
            nameCSV = nameExport + "_" + str(year)
            processoExportar(areaTemp, nameCSV)        
        
        if "_desf_veg_"  in nameExport and year > 1985:
            areaGeral = areaGeral.merge(areaTemp)      
       
    nExport = True
    if porAno:
        nExport = False     
    
    return areaGeral, nExport


# pixelArea, imgWater, limitGeometria, pref_bnd, nomegeometria, byYears, nameCSV
def anoImCruda(imgAreaRef, mapaDelimitado, limite, preficoBnd, nameregion, nameExport):
    
    imgAreaRef = imgAreaRef.clip(limite)
    areaGeral = ee.FeatureCollection([])      
    print("Loadding image Cobertura Coleção 8 " )
    imgMapp = ee.Image(mapaDelimitado).clip(limite)
    imgMapp = imgMapp.select("fire_frequency_1986_2022")  
    # print("---- SHOW ALL BANDS FROM MAPBIOKMAS MAPS -------\n ", imgMapp.bandNames().getInfo())

    areaTemp = calculateArea (imgMapp, imgAreaRef, limite)        
    areaTemp = areaTemp.map( lambda feat: feat.set(
                                        'year', '1986_2022', 
                                        'camada', preficoBnd[:-2],
                                        'region', nameregion                                               
                                    ))

    nameCSV = "stat_" + nameExport
    processoExportar(areaTemp, nameCSV)       



#exporta a imagem classificada para o asset
def processoExportar(areaFeat, nameT):      
    optExp = {
          'collection': areaFeat, 
          'description': nameT, 
          'folder': param["driverFolder"]        
        }    
    task = ee.batch.Export.table.toDrive(**optExp)
    task.start() 
    print("salvando ... " + nameT + "..!") 

pixelArea = ee.Image.pixelArea().divide(10000)
select_Caatinga = False
sobreNomeGeom = "_Semiarido"
nomegeometria = 'semiarido'
CD_Bioma = None
if select_Caatinga:
    limitGeometria = ee.FeatureCollection(param["asset_biomas_250"])
    if CD_Bioma == None:
        sobreNomeGeom = '_Brasil'
    else:
        print('         limite caatinga carregado ')
        limitGeometria = limitGeometria.filter(ee.Filter.eq("CD_Bioma", str(CD_Bioma)))
        sobreNomeGeom = dict_CD_Bioma[str(CD_Bioma)]
else:
    limitGeometria = ee.FeatureCollection(param["asset_semiarido2024"])

print("=============== limite a Macro Selecionado ========== ", limitGeometria.size().getInfo())

limitGeometria = limitGeometria.geometry()
imgWater = ee.Image(param["asset_annual_water"]).clip(limitGeometria)
mapsdesfVegSec = ee.Image(param["asset_desf_vegsec"]).clip(limitGeometria)
mapsIrrigate = ee.Image(param["asset_irrigate_agro"]).clip(limitGeometria)
mapsFire = ee.Image(param["asset_fire_annual"]).clip(limitGeometria)
mapsFireAcc = ee.Image(param["asset_fire_acumulado"]).clip(limitGeometria)

exportar = False
byYears = True
# iterandoXanoImCruda(imgAreaRef, mapaDelimitado, limite, preficoBnd, nameregion):
for assetName in lst_nameAsset:
    if assetName == 'asset_annual_water':
        print("---- PROCESSING MAPS WATER ---------------")
        pref_bnd = "annual_water_coverage_"  
        nameCSV = "area_class_water" + sobreNomeGeom      
        csv_table, exportar = iterandoXanoImCruda(pixelArea, imgWater, limitGeometria, pref_bnd, nomegeometria, byYears, nameCSV)        

    elif assetName == 'asset_desf_vegsec':
        print("---- PROCESSING MAPS VEGETAÇÃO SECUNDARIA  ---------------")
        pref_bnd = "classification_"
        nameCSV = "area_class_desf_veg_secundaria" + sobreNomeGeom
        csv_table, exportar = iterandoXanoImCruda(pixelArea, mapsdesfVegSec, limitGeometria, pref_bnd, nomegeometria, byYears, nameCSV)

    elif assetName == 'asset_irrigate_agro':
        print("---- PROCESSING MAPS AREAS IRRIGADAS ---------------")
        pref_bnd = "irrigated_agriculture_"
        nameCSV = "area_class_irrigated_" + sobreNomeGeom
        csv_table, exportar = iterandoXanoImCruda(pixelArea, mapsIrrigate, limitGeometria, pref_bnd, nomegeometria, byYears, nameCSV)

    elif assetName == 'asset_fire_annual':
        print("---- PROCESSING MAPS AREAS QUEIMADAS ---------------")
        pref_bnd = "burned_area_"
        nameCSV = "area_class_queimadas" + sobreNomeGeom
        csv_table, exportar = iterandoXanoImCruda(pixelArea, mapsFire, limitGeometria, pref_bnd, nomegeometria, byYears, nameCSV)

    elif assetName == 'asset_fire_acumulado':
        print("---- PROCESSING MAPS AREAS QUEIMADAS ---------------")
        pref_bnd = "burned_area_acc"
        nameCSV = "area_class_queimadas_accumalada" + sobreNomeGeom
        anoImCruda(pixelArea, mapsFireAcc, limitGeometria, pref_bnd, nomegeometria, nameCSV)

    if exportar:
        processoExportar(csv_table, nameCSV)