//https://code.earthengine.google.com/a439f870a02b371daf094c5b6cf6de34
//https://code.earthengine.google.com/c6be8cee51ed15cb9cd80c031f8f2729
var palettes = require('users/mapbiomas/modules:Palettes.js');
var text = require('users/gena/packages:text')

var visualizar = {
    visclassCC: {
            "min": 0, 
            "max": 45,
            "palette":  palettes.get('classification5'),
            "format": "png"
    },
    visMosaic: {
        min: 0,
        max: 2000,
        bands: ['red_median', 'green_median', 'blue_median']
    },
    props: {  
        textColor: 'ff0000', 
        outlineColor: 'ffffff', 
        outlineWidth: 1.5, 
        outlineOpacity: 0.2
    }
} 


var param = { 
    assetMap: 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1',
    asset_filted : {
        'gapfill':'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/Gap-fill',
        'spatial':'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/Spatial',
        'V5':'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/CLASS/ClassCol8V5',
        'V6':'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/CLASS/ClassCol8V6',
        'V7':'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/CLASS/ClassCol8V8',
        'V9':'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/CLASS/ClassCol8V9',
    },
    // assetclass : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/class_filtered_Fq',
    // assetclass : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/class_filtered_GF',    
    assetIm: 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',    
    assetBacia: "projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga",    
    anos: ['1985','1986','1987','1988','1989','1990','1991','1992','1993','1994',
           '1995','1996','1997','1998','1999','2000','2001','2002','2003','2004',
           '2005','2006','2007','2008','2009','2010','2011','2012','2013','2014',
           '2015','2016','2017','2018','2019','2020','2021','2022'],
    bandas: ['red_median', 'green_median', 'blue_median'],
    
    listaNameBacias: [
        '741','7421','7422','744','745','746','7492','751','752',
        '753', '754','755','756','757','758','759','7621','7622','763',
        '764','765','766','767','771','772','773', '7741','7742','775',
        '776','777','778','76111','76116','7612','7613','7614','7615',
        '7616','7617','7618','7619'
    ],
    classMapB: [3, 4, 5, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,62],
    classNew:  [3, 4, 3, 3,12,12,21,21,21,21,21,22,22,22,22,33,29,22,33,12,33, 21,33,33,21,21,21,21,21,21,21,21,21,21, 4,12,21]
};
var selBacia = '7742';
var yearcourrent = 2016;
var banda_activa = 'classification_' + String(yearcourrent);
var FeatColbacia = ee.FeatureCollection(param.assetBacia);
var imgMapCol71= ee.Image(param.assetMap)//.clip(FeatColbacia.geometry());
var imgMapCol8gapfillV2 =  ee.ImageCollection(param.asset_filted.gapfill)
                                    .filter(ee.Filter.eq('version', '2'))
                                    .filter(ee.Filter.eq('id_bacia', selBacia)).first();
imgMapCol8gapfillV2 = imgMapCol8gapfillV2.select(banda_activa)//.remap(param.classMapB, param.classNew);


var imgMapCol8gapfillV3 =  ee.ImageCollection(param.asset_filted.gapfill)
                                    .filter(ee.Filter.eq('version', '3'))
                                    .filter(ee.Filter.eq('id_bacia', selBacia)).first();
print('imgMapCol8gapfillV3 = ', imgMapCol8gapfillV3);
imgMapCol8gapfillV3 = imgMapCol8gapfillV3.select(banda_activa)//.remap(param.classMapB, param.classNew);

var imgMapCol8SpaV2 =  ee.ImageCollection(param.asset_filted.spatial)
                                    .filter(ee.Filter.eq('version', '2'))
                                    .filter(ee.Filter.eq('id_bacia', selBacia)).first();
imgMapCol8SpaV2 = imgMapCol8SpaV2.select(banda_activa).remap(param.classMapB, param.classNew);

var imgMapCol8SpaV3 =  ee.ImageCollection(param.asset_filted.spatial)
                                    .filter(ee.Filter.eq('version', '3'))
                                    .filter(ee.Filter.eq('id_bacia', selBacia)).first();
imgMapCol8SpaV3 = imgMapCol8SpaV3.select(banda_activa)//.remap(param.classMapB, param.classNew);


print("imagem no Asset Geral Mapbiomas Col 7.1", imgMapCol71);
// print("imagem no Asset Geral X Bacias col 8", imgMapCol8V6);

var Mosaicos = ee.ImageCollection(param.assetIm).filter(
                        ee.Filter.eq('biome', 'CAATINGA')).select(param.bandas);
                        
var mosaic_year = Mosaicos.filter(ee.Filter.eq('year', yearcourrent)).median();                     
Map.addLayer(FeatColbacia, {color: 'green'}, 'bacia', false);
Map.addLayer(mosaic_year, visualizar.visMosaic,'Mosaic Col8', false);

var imgMapCol71temp = imgMapCol71.select(banda_activa)//.remap(param.classMapB, param.classNew);
Map.addLayer(imgMapCol71temp, visualizar.visclassCC, 'Col71_' + String(yearcourrent), false);
Map.addLayer(imgMapCol8gapfillV2.selfMask(),  visualizar.visclassCC, 'Col8_GapfillV2', false);
Map.addLayer(imgMapCol8gapfillV3.selfMask(),  visualizar.visclassCC, 'Col8_GapfillV3', false);
Map.addLayer(imgMapCol8SpaV2.selfMask(),  visualizar.visclassCC, 'Col8_Spacial V2<-5', true);
Map.addLayer(imgMapCol8SpaV3.selfMask(),  visualizar.visclassCC, 'Col8_Spacial V3<-10', false);


var save_ROIs_toAsset = function(collection, name){
    var outAssetpolg = 'users/CartasSol/coleta/polygonsCorr/'
    var optExp = {
        'collection': collection,
        'description': name,
        'assetId': outAssetpolg + name
    };

    Export.table.toAsset(optExp);
    print("exportando ROIs da bacia $s ...!", name)
};


// var de_22_para_21  = ee.Feature(trocar_area_nao_vegetada_para_21, 
//                                     {'idBacia': '753', 'de': 22, 
//                                     'fCol': 'c8', 'para': 21, 'eCol': 'c8'});

// var de_22_para_29  = ee.Feature(trocar_area_nao_vegetada_para_Afloramento, 
//                                     {'idBacia': '753','de': 22, 
//                                     'fCol': 'c8', 'para': 29, 'eCol': 'c8'});    
// var de_3_para_4 = ee.Feature(trocar_floresta, 
//                                 {'idBacia': '753','de': 3, 
//                                 'fCol': 'c8', 'para': 4, 'eCol': 'c71'});
// var de_33_para_4 = ee.Feature(trocar_agua_savana, 
//                                     {'idBacia': '776','de': 33, 
//                                     'fCol': 'c8', 'para': 4, 'eCol': 'c8'});
// var de_33_para_21 = ee.Feature(trocar_agua_21, 
//                                         {'idBacia': '776','de': 33, 
//                                         'fCol': 'c8', 'para': 21, 'eCol': 'c8'});
// var de_12_para_29 = ee.Feature(trocar_campo_afloramento, 
//                                             {'idBacia': '7616','de': 12, 
//                                             'fCol': 'c8', 'para': 29, 'eCol': 'c8'});
// var de_33_para_21 = ee.Feature(trocar_agua_21, 
//                                                 {'idBacia': '7616','de': 33, 
//                                                 'fCol': 'c8', 'para': 21, 'eCol': 'c8'});
// var de_22_para_21 = ee.Feature(trocar_solo_21, 
//                                         {'idBacia': '7421','de': 29, 
//                                         'fCol': 'c8', 'para': 21, 'eCol': 'c8'});   // 7421, 754
// var de_22_para_21 = ee.Feature(trocar_area_nao_vegetada_para_21, 
//                                         {'idBacia': '755','de': 22, 
//                                         'fCol': 'c8', 'para': 21, 'eCol': 'c8'});  // 754, 755
// var de_3_para_21 = ee.Feature(trocar_area_nao_vegetada_para_21, 
//                                         {'idBacia': '754','de': 3, 
//                                         'fCol': 'c8', 'para': 21, 'eCol': 'c8'});

// var de_12_para_21 = ee.Feature(trocar_campo_21, 
//                                             {'idBacia': '777','de': 12, 
//                                             'fCol': 'c8', 'para': 21, 'eCol': 'c8'});  

// var de_22_para_21 = ee.Feature(trocar_area_nao_vegetada_para_21, 
//                                             {'idBacia': '755','de': 22, 
//                                             'fCol': 'c8', 'para': 21, 'eCol': 'c8'});
// var de_33_para_33 = ee.Feature(trocar_agua_Agua, 
//                                             {'idBacia': '778','de': 33, 
//                                             'fCol': 'c8', 'para': 33, 'eCol': 'c71'});

// trocar_21_campo
// var de_21_para_12 = ee.Feature(trocar_21_campo, 
//                                             {'idBacia': '7618','de': 21, 
//                                             'fCol': 'c8', 'para': 12, 'eCol': 'c8'});
var de_22_para_12 = ee.Feature(trocar_solo_campo, 
                                            {'idBacia': '756','de': 22, 
                                            'fCol': 'c8', 'para': 12, 'eCol': 'c8'});
var de_22_para_21 = ee.Feature(trocar_solo_para_21, 
                                            {'idBacia': '756','de': 22, 
                                            'fCol': 'c8', 'para': 21, 'eCol': 'c8'});


//[de_22_para_21,de_22_para_29,de_3_para_4,de_33_para_4, de_33_para_21,de_12_para_29, 
// de_33_para_21, de_29_para_21, de_22_para_21, de_12_para_21]
var featCorrection = ee.FeatureCollection([de_22_para_12, de_22_para_21]);
var nomeExp = "nbacia_" + selBacia + "_" + yearcourrent;
save_ROIs_toAsset(featCorrection, nomeExp);
