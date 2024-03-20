
var functionExports = function(cc_image, nameEXp, geomSHP, nassetId){
    var pmtExpo = {
        image: cc_image,
        description: nameEXp,
        scale: 30, // Escolha a escala de acordo com sua necessidade
        region: geomSHP.geometry(),
        assetId: nassetId + nameEXp, // Substitua pelo nome da sua pasta no Google Drive
        maxPixels: 1e13 // Escolha o valor adequado para o número máximo de pixels permitidos
    };
    Export.image.toAsset(pmtExpo);

    print("maps salvo " + nameEXp + " ...");
};
var vis = {
    'alerta': {
        min: 0, max: 1,
        palette: '#a52a2a'
    }, 
    'fire' :{
        min: 0, max: 1,
        palette: '#c71585'
    } 
}

var parameters = {
    "asset_alerta": 'users/data_sets_solkan/Alertas/dashboard_alerts-shapefile_2024_02',
    "asset_fogo": 'projects/ee-geomapeamentoipam/assets/MAPBIOMAS_FOGO/COLECAO_2/Colecao2_fogo_mask_v1',
    'limit_caat': 'users/CartasSol/shapes/nCaatingaBff3000',
    'asset_img': 'users/data_sets_solkan/Alertas/',
    "consulta": true
};
var alertas = ee.FeatureCollection(parameters.asset_alerta);
var shp_limit = ee.FeatureCollection(parameters.limit_caat);
alertas = alertas.filterBounds(shp_limit.geometry());

if (parameters.consulta){
    var year = 2022;
    var imgFire = ee.ImageCollection(parameters.asset_fogo)
                        .filter(ee.Filter.eq('biome', 'CAATINGA'))
                        .filter(ee.Filter.eq('year', 2022))
                        
    print("show data img fire ", imgFire);
    imgFire = imgFire.mosaic().clip(shp_limit.geometry().bounds());
    var imgALerts = ee.Image(parameters.asset_img + 'layersImgClassTP_2024_02');
    
    Map.addLayer(imgFire.gt(0), vis.fire, "fire year " + year.toString());
    Map.addLayer(imgALerts, vis.alerta, "Alerta All years");
}else{
    alertas = alertas.map(function(feat){return feat.set('class', 1)});
    var pmtred = {
        properties: ['class'], 
        reducer: ee.Reducer.first()
    };
    var imgExp = alertas.reduceToImage(pmtred);
    var name_toExport = 'layersImgClassTP_2024_02';
    functionExports(imgExp, name_toExport, shp_limit,parameters.asset_img);
}