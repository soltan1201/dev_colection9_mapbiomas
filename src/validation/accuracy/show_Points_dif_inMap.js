/*
# SCRIPT DE COMPARAÇÃO DOS PONTOS DE ACCURACIA CONTRA A COLEÇÃO 7.1 E 8.0
# Produzido por Geodatin - Dados e Geoinformacao
# DISTRIBUIDO COM GPLv2
*/

var palettes = require('users/mapbiomas/modules:Palettes.js');
var text = require('users/gena/packages:text')

var visualizar = {
    visclassCC: {
            "min": 0, 
            "max": 62,
            "palette":  palettes.get('classification8'),
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
} ;

/**
 * Export the feature collection to a shapefile in Google Earth Engine asset.
 * @param {ee.FeatureCollection} ROIsFeat - The feature collection to be exported.
 * @param {string} nameB - The description or name of the exported shapefile.
 * @param {string} asset_path - The path to the Google Earth Engine asset where the shapefile will be stored.
 */
function processoExportarSHP(ROIsFeat, nameB, asset_path){    
    var optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'assetId': asset_path + "/" + nameB          
        };
    Export.table.toAsset(optExp);
    print("salvando ... " + nameB + "..!")  ;  
}
/**
 * This function compares the classification of a given year with the reference classification 
 * for each point in the feature collection. It adds a new property to each feature indicating 
 * whether the classification is different from the reference classification.
 * 
 * @param {Array<string>} lstYear - An array of years to compare the classification.
 * @param {ee.FeatureCollection} featCol - The feature collection containing the points.
 * @param {number} sizeYY - The number of years to compare.
 * @returns {ee.FeatureCollection} - The feature collection with added properties indicating 
 *                                  the difference in classification for each year.
 */
function compare_class_change(lstYear, featCol, sizeYY){
    featCol = ee.FeatureCollection(featCol).map(
        function(feat){
            lstYear.slice(0, sizeYY).forEach(function(yyear){
                var propRef = 'CLASS_' + yyear;
                var propClass = 'classification_' + yyear;
                var dif = ee.Algorithms.IsEqual(ee.Number(feat.get(propRef)).subtract(ee.Number(feat.get(propClass))).neq(0), 1);
                // values with 1 in dif means that the class is different, the other value is the same class
                feat = feat.set('diference' + yyear, dif);
            });
            
            return feat;
    });

    return ee.FeatureCollection(featCol);
}


var param = {
    // pontos de accuracias comparados contra as outras coleções 
    'asset_pointsLapigvsCol7': 'users/mapbiomascaatinga04/occTab_corr_Caatinga_mapbiomas_collection71_integration_v1',
    'asset_pointsLapigvsCol8': 'users/mapbiomascaatinga04/occTab_corr_Caatinga_mapbiomas_collection80_integration_v1',
    'asset_pointsLapigvsCol8dif': 'users/mapbiomascaatinga04/occTab_Acc_Caatinga_mapbiomas_collection80_dif',
    'asset_Map_col7': 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1',
    'asset_Map_col8' : "projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1",
    'asset_output': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier',
    'asset_ptosDifLapigvsCol7': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/occTab_acc_Dif_Caat_mapbiomas_71_integration_v1',
    'asset_ptosDifLapigvsCol8': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/occTab_acc_Dif_Caat_mapbiomas_80_integration_v1',
    'asset_caat_buffer': 'users/CartasSol/shapes/caatinga_buffer5km',
    'assetIm': 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',
    'bandas': ['red_median', 'green_median', 'blue_median'],
    'anos': [
        '1985','1986','1987','1988','1989','1990','1991','1992','1993','1994',
        '1995','1996','1997','1998','1999','2000','2001','2002','2003','2004',
        '2005','2006','2007','2008','2009','2010','2011','2012','2013','2014',
        '2015','2016','2017','2018','2019','2020','2021','2022'
    ],
};
var exportShps = true;
var yearcourrent = 2020;
var banda_activa = 'classification_' + String(yearcourrent);
var limitCaat = ee.FeatureCollection(param.asset_caat_buffer).geometry();
var imgMapCol71= ee.Image(param.asset_Map_col7).clip(limitCaat).select(banda_activa);
var imgMapCol8= ee.Image(param.asset_Map_col8).clip(limitCaat).select(banda_activa);
print("raster maps coleção 7.1 ", imgMapCol71);
print("raster maps coleção 8.0 ", imgMapCol8);
var pointRefCol71 = ee.FeatureCollection(param.asset_pointsLapigvsCol7);
var pointRefCol80 = ee.FeatureCollection(param.asset_pointsLapigvsCol8);

print(ee.String(" we loading ").cat(pointRefCol71.size()).cat(" points of reference in Col7.1"));
print("show the 10 first ", pointRefCol71.limit(10));
print(ee.String(" we loading ").cat(pointRefCol80.size()).cat(" points of reference in Col8.0"));
print("show the 10 first ", pointRefCol80.limit(10));

var poitsRefCol71comp = null;
var pointRefCol80comp = null;
if (exportShps){
    poitsRefCol71comp = compare_class_change(param.anos, pointRefCol71, 37);
    print("show the 5 first comparations col71", poitsRefCol71comp.limit(5));
    pointRefCol80comp = compare_class_change(param.anos, pointRefCol80, 38);
    print("show the 5 first comparations col80", pointRefCol80comp.limit(5));
}
var Mosaicos = ee.ImageCollection(param.assetIm).filter(
                        ee.Filter.eq('biome', 'CAATINGA')).select(param.bandas);
var mosaic_year = Mosaicos.filter(ee.Filter.eq('year', yearcourrent)).median();  

Map.addLayer(mosaic_year, visualizar.visMosaic,'Mosaic Col8');
Map.addLayer(imgMapCol71, visualizar.visclassCC,'Col71_' + String(yearcourrent), false);
Map.addLayer(imgMapCol8,  visualizar.visclassCC, 'Col8_'+ String(yearcourrent), false);
var limitCaatinga = ee.Image().byte().paint(limitCaat, 1, 1);
limitCaatinga = limitCaatinga.visualize({palette: '000000', 'opacity': 0.7});
Map.addLayer(limitCaatinga, {}, "Caatinga buffer 5KM");


if (exportShps){
    var nameFeatRefDif = 'occTab_acc_Dif_Caat_mapbiomas_71_integration_v1';
    processoExportarSHP(poitsRefCol71comp, nameFeatRefDif, param.asset_output);
    nameFeatRefDif = 'occTab_acc_Dif_Caat_mapbiomas_80_integration_v1';
    processoExportarSHP(pointRefCol80comp, nameFeatRefDif, param.asset_output);

}else{
    poitsRefCol71comp = ee.FeatureCollection(param.asset_ptosDifLapigvsCol7);
    pointRefCol80comp = ee.FeatureCollection(param.asset_ptosDifLapigvsCol8);
    var poitsRefCol71compY = null;
    if(yearcourrent < 2022){
        poitsRefCol71compY = poitsRefCol71comp.filter(ee.Filter.eq('diference' + String(yearcourrent), true));
        print(" size points filtered Col7.1", poitsRefCol71compY.size());
    }else{
        print("We don´t have points of references in this year, sorry !");
    }
    
    var pointRefCol80compY = pointRefCol80comp.filter(ee.Filter.eq('diference' + String(yearcourrent), true));
    print(" size points filtered Col8.0", pointRefCol80compY.size());
    Map.addLayer(poitsRefCol71compY, {color: 'red'}, 'diferences C71 ' + String(yearcourrent), false);
    Map.addLayer(pointRefCol80compY, {}, 'diferences C80 ' + String(yearcourrent));
}




