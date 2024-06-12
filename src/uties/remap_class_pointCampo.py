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

def processoExportar(ROIsFeat, nameT, porAsset):  

    if porAsset:
        optExp = {
          'collection': ROIsFeat, 
          'description': nameT, 
          'assetId':"projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/" + nameT          
        }
        task = ee.batch.Export.table.toAsset(**optExp)
        task.start() 
        print("salvando ... " + nameT + "..!")
    else:
        optExp = {
            'collection': ROIsFeat, 
            'description': nameT, 
            'folder':"ptosAccCol9corr",
            # 'priority': 1000          
            }
        task = ee.batch.Export.table.toDrive(**optExp)
        task.start() 
        print("salvando ... " + nameT + "..!")

def set_class_level1(feat):
    dict_pointsL3 = ee.Dictionary({
            'afloramentos': 29,
            'agricultura': 21,
            'agua': 33,
            'aquicultura': 33,
            'campo': 12,
            'carnaúbas': 21,
            'desmatamento': 22 ,
            'exotica': 21,
            'floresta': 3,
            'mineração': 22,
            'mosaico de uso': 21,
            'pastagem': 21,
            'regeneração savana': 4,
            'savana': 4,
            'solo exposto': 22,
            'urbano': 22,
            'áreas não vegetadas': 22
    })

    dict_pointsL1 = ee.Dictionary({
            'afloramentos': 2,
            'agricultura': 3,
            'agua': 5,
            'aquicultura': 5,
            'campo': 2,
            'carnaúbas': 3,
            'desmatamento': 4 ,
            'exotica': 3,
            'floresta': 1,
            'mineração': 4,
            'mosaico de uso': 3,
            'pastagem': 3,
            'regeneração savana': 1,
            'savana': 1,
            'solo exposto': 4,
            'urbano': 4,
            'áreas não vegetadas': 4
    })
    return feat.set(
            'level_1', dict_pointsL1.get(feat.get('classe')),
            'level_3', dict_pointsL3.get(feat.get('classe')),
        )

classMapB = [ 0, 3, 4, 5, 6, 9,11,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62]
classNew =  [27, 3, 4, 3, 3, 3,12,12,12,21,21,21,21,21,22,22,22,22,33,29,22,33,12,33,21,33,33,21,21,21,21,21,21,21,21,21,21, 4,12,21]
asset_points = 'users/nerivaldogeo/pontos_campo_caatinga'
pointsCampo = ee.FeatureCollection(asset_points).map(lambda feat : set_class_level1(feat))

print(" ", pointsCampo.first().getInfo())
namePoint = 'pontos_campo_caatinga_03_2024'
processoExportar(pointsCampo, namePoint, True)