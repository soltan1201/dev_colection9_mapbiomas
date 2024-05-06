


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


param = {
    'inputAssetpolg': {'id':'users/CartasSol/coleta/polygonsCorr'},
    'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrograficaCaatbuffer5k',
    'assetMap': 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1',
    'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/Spatial/',
    'input_solo': 'users/diegocosta/doctorate/Bare_Soils_Caatinga',
    'outputAsset': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/merge/',
    'asset_florestErrNe' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/shpExtras/shpExtraspoligons_rev_sombrasrelNer',
    'asset_florestErrRa' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/shpExtras/shpExtraspoligons_rev_sombrasrelRaf',
    'asset_afloramentoPol' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/shpExtras/shpExtraspoligons_rev_afloramento',
    'asset_restingaNeri' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/shpExtras/poligons_region_restingaNeri',
    'asset_restingaRafa' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/shpExtras/poligons_region_restingaRafa',
    'correct_past_to_Grass' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/shpExtras/geom_correct21_12_7612_7613_76116',
    'asset_mask_aflora':'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/AFLORAMENTO/label_mask_afloramento',
    'year_first': 1985,
    'year_end': 2022,
}


mask_afloramento = ee.Image(param['asset_mask_aflora']).selfMask()
polg_sombra = ee.FeatureCollection(param['asset_florestErrNe']).merge(
                        ee.FeatureCollection(param['asset_florestErrRa'])).geometry()
nameBacias = [
    '741','7421','7422','744','745','746','7492','751','752','753',
    '754','755','756','757','758','759','7621','7622','763','764',
    '765','766','767','771','772','773', '7741','7742','775','776',
    '777','778','76111','76116','7612','7614','7615','7616','7617',
    '7618','7619', '7613'
]


# lista de bacia con afloramento
#  ['741', '7421', '7422', '744', '745', '746', '7492', '754', '755', '756', '758', 
# '759', '7621', '763', '764', '765', '766', '767', '771', '772', '773', '7741', 
# '7742', '776', '777', '778', '76111', '7614', '7615', '7616', '7617', '7618', 
# '7619', '7613']

# lista de bacia con sombra relevo
#  ['741', '7421', '7422', '744', '745', '746', '7492', '751', '752', 
# '753', '754', '756', '7621', '763', '765', '771', '772', '773', 
# '7741', '7742', '776', '7612', '7615', '7619', '7613']
lstAflora = []
lstSombra = []
geoBacias = ee.FeatureCollection(param['asset_bacias_buffer'])
for nbacia in nameBacias:
    # print("loading ", nbacia)
    limBacia = geoBacias.filter(ee.Filter.eq('nunivotto3', nbacia)).geometry()
    pmtroRed = {
                'reducer': ee.Reducer.count(), 
                'geometry': limBacia, 
                'scale': 30, 
                'bestEffort': True, 
                'maxPixels': 1e13, 
                'tileScale': 4
            }
    redImg = mask_afloramento.select('constant').reduceRegion(**pmtroRed)
    dictInfo = redImg.getInfo()['constant']
    print("loading ", nbacia, " com pixeis afloramento = ", dictInfo)
    if dictInfo > 0:
        lstAflora.append(nbacia)

    polGInte = limBacia.intersection(polg_sombra)
    area = polGInte.area(0.01).getInfo()

    if area > 0:
        lstSombra.append(nbacia)


print("lista de bacia con afloramento \n", lstAflora)
print("   ")

print("lista de bacia con sombra relevo \n", lstSombra)



