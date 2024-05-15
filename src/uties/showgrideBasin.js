/**
 * Calculates the valid area of each feature in the input feature collection with respect to the given limit.
 * @param {ee.FeatureCollection} shpLimit - The feature collection representing the limit for calculating valid areas.
 * @param {ee.FeatureCollection} shpGr - The input feature collection for which valid areas need to be calculated.
 * @return {ee.FeatureCollection} The feature collection with an added property 'area_ba' representing the valid area of each feature.
 */
function setAreavalida (shpLimit, shpGr){
    var shpGrades = shpGr.map(function(feat){
        var areaInt = ee.Number(feat.intersection(shpLimit).area());
        return feat.set('area_ba', areaInt);
    })
    return ee.FeatureCollection(shpGrades);
}

function getAreavalida (shpLimit, shpGr){
    var shpGrades = shpGr.map(function(feat){
        var areaInt = ee.Number(feat.geometry().intersection(shpLimit).area());
        return feat.set('area_ba', areaInt);
    })
    return ee.FeatureCollection(shpGrades);
}
/**
 * Export the given feature collection to an asset.
 * @param {ee.FeatureCollection} ROIsFeat - The feature collection to be exported.
 * @param {string} nameB - The description or name of the asset to be exported.
 * @param {string} asset_path - The path of the asset where the feature collection will be exported.
 */
function processoExportarSHP(ROIsFeat, nameB, asset_path){    
    var optExp = {
            'collection': ROIsFeat, 
            'description': nameB, 
            'assetId': asset_path + nameB          
        };
    Export.table.toAsset(optExp);
    print("salvando ... " + nameB + "..!")  ;  
}

var param = {
    'asset_shpGrade': 'projects/mapbiomas-arida/ALERTAS/auxiliar/basegrade30KMCaatinga',
    'asset_output': 'projects/mapbiomas-arida/ALERTAS/auxiliar/',
    'asset_bacias': 'projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga',
    'asset_bacias_limit': 'users/CartasSol/shapes/bacias_limit',
    'asset_shpGradeupdate': 'projects/mapbiomas-arida/ALERTAS/auxiliar/basegrade30KMCaatingaArea',
    'asset_Coincidencia': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/masks/maks_coinciden',
    'asset_estaveis': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/masks/maks_estaveis',
    'asset_fire_mask': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/masks/maks_fire_w5',
    'assetMapbiomas80': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    'exportSHP': false
}
var yearcourrent = 2020;
var shpGrade = ee.FeatureCollection(param.asset_shpGrade);
var shpBacias = ee.FeatureCollection(param.asset_bacias);
var shpBaLimit = ee.FeatureCollection(param.asset_bacias_limit).geometry();

print("showing metadata of shpGrade ", shpGrade.limit(10));
print("showing metadata of shpBaLimit ", shpBaLimit);
print("showing metadata of shpBacias ", shpBacias.limit(1));

if (param.exportSHP){
    shpGrade = setAreavalida(shpBaLimit, shpGrade);
    var nameExpGr = 'basegrade30KMCaatingaArea';
    processoExportarSHP(shpGrade, nameExpGr, param.asset_output);
}

Map.addLayer(shpBaLimit, {color: 'green'}, 'bacias limit');
Map.addLayer(shpBacias, {color: 'blue'}, 'bacias');
Map.addLayer(shpGrade, {color: 'red'}, 'grade');



var mapCol8 = ee.Image(param.assetMapbiomas80);

var m_assetPixEst = param.asset_estaveis + '/masks_estatic_pixels_' + String(yearcourrent);
var maksEstaveis = ee.Image(m_assetPixEst).rename('estatic'); 

var asset_PixCoinc = param.asset_Coincidencia + '/masks_pixels_incidentes_'+ String(yearcourrent);
var imMasCoinc = ee.Image(asset_PixCoinc).rename('coincident');