// https://code.earthengine.google.com/c41a6f946d734cee1c8dc313171c55b9
// https://code.earthengine.google.com/37b91ad3a9d2c1844956be614c80139e?noload=1
function processoExportarSHP(ROIsFeat, nameB, asset_path){
    
    var optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'assetId': asset_path + nameB          
        };
    Export.table.toAsset(optExp);
    print("salvando ... " + nameB + "..!")  ;  
}

function processoExportarSHPDr(ROIsFeat, nameB){
    
    var optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'folder': 'areaFlorest'          
        };
    Export.table.toDrive(optExp);
    print("salvando ... " + nameB + "..!")  ;  
}
function processoExportar(mapaRF,  nomeDesc, geomRegion){
    var idasset =  param.output_asset + nomeDesc
    var optExp = {
        'image': mapaRF, 
        'description': nomeDesc, 
        'assetId':idasset, 
        'region': geomRegion,
        'scale': 30, 
        'maxPixels': 1e13,
        "pyramidingPolicy":{".default": "mode"}
    }
    Export.image.toAsset(optExp);
    print("salvando ... " + nomeDesc + "..!")
}
/**
 * Convert a complex ob to feature collection
 * @param obj 
 */
var convert2table = function (obj) {

    obj = ee.Dictionary(obj);

    var territory = obj.get('territory');

    var classesAndAreas = ee.List(obj.get('groups'));

    var tableRows = classesAndAreas.map(
        function (classAndArea) {
            classAndArea = ee.Dictionary(classAndArea);

            var classId = classAndArea.get('class');
            var area = classAndArea.get('sum');

            var tableColumns = ee.Feature(null)
                .set('territory', territory)
                .set('class', classId)
                .set('area', area);

            return tableColumns;
        }
    );

    return ee.FeatureCollection(ee.List(tableRows));
};
var pixelArea = ee.Image.pixelArea().divide(1000000);
/**
 * Calculate area crossing a cover map (deforestation, mapbiomas)
 * and a region map (states, biomes, municipalites)
 * @param image 
 * @param territory 
 * @param geometry
 */
var calculateArea = function (image, geometry, nyear) {

    var reducer = ee.Reducer.sum().group(1, 'class')

    var territotiesData = pixelArea.addBands(image)
        .reduceRegion({
            reducer: reducer,
            geometry: geometry,
            scale: 30,
            maxPixels: 1e12
        });

    territotiesData = ee.List(territotiesData.get('groups'));
    print(territotiesData)
    // var areas = territotiesData.map(convert2table);

    return ee.Feature(ee.Geometry.Point([0,0]),  ee.Dictionary(territotiesData.get(0)).set('year', nyear));

};

var Palettes = require('users/mapbiomas/modules:Palettes.js');
var palette = Palettes.get('classification8');
var vis = {
        classCC: {'min': 0,'max': 62,'palette': palette,'format': 'png'},
        concordenate: {min:1, max:3, palette: ['gray', 'blue', 'red']}
    }

var param = {
    'asset_col60': 'projects/mapbiomas-workspace/public/collection6/mapbiomas_collection60_integration_v1',
    'asset_col71': 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1',
    'asset_col80': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    'asset_col90': 'projects/mapbiomas-workspace/COLECAO9/integracao',
    'asset_serra_confusoes': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/masks/floresta_regions_Serra_confusoesAmp',
    'asset_chapada_araripe': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/masks/floresta_regions_chapada_Araripe',
    'asset_caat_buffer': 'users/CartasSol/shapes/caatinga_buffer5km',
    'asset_Output_shp': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/masks/',
    'output_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/toExportYY/',
    'asset_layer_florest': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/toExportYY',
    'years': [
        '1985','1986','1987','1988','1989','1990','1991','1992','1993','1994',
        '1995','1996','1997','1998','1999','2000','2001','2002','2003','2004',
        '2005','2006','2007','2008','2009','2010','2011','2012','2013','2014',
        '2015','2016','2017','2018','2019','2020','2021','2022','2023'
    ],
    exportGeom: false, 
    processLayerFlorest: false,
    applyFrequency: false,
    corregirUltimoAno: false
     
}

var bioma = "CAATINGA"// 'PAMPA' // 'CERRADO' //'PANTANAL'// "MATA ATLÂNTICA";



var bioma5kbuf = ee.FeatureCollection(param.asset_caat_buffer).geometry();
var limitSerraConf = ee.FeatureCollection(param.asset_serra_confusoes).geometry();
var limitChapadaAr = ee.FeatureCollection(param.asset_chapada_araripe).geometry();
var regionsFlorest = limitSerraConf.union(limitChapadaAr);
var dif = bioma5kbuf.difference(regionsFlorest);
var areaFixa = ee.Feature(dif, {'value': 0});
var areaToChange = ee.Feature(regionsFlorest, {'value': 1});
var areaTo_mask = ee.FeatureCollection([areaFixa, areaToChange]);
var img_mask_err = areaTo_mask.reduceToImage(['value'], ee.Reducer.first());
var maskCaat = img_mask_err.gte(0);

var class_col60 = ee.Image(param.asset_col60).updateMask(maskCaat);
var class_col71 = ee.Image(param.asset_col71).updateMask(maskCaat);
var class_col80 = ee.Image(param.asset_col80).updateMask(maskCaat);
var class_col90a = ee.ImageCollection(param.asset_col90)
                        .filter(ee.Filter.eq('version','0-5'))
                        .mosaic().updateMask(maskCaat);               
var class_col90b =  ee.ImageCollection(param.asset_col90)
                            .filter(ee.Filter.eq('version','0-14'))
                            .mosaic().updateMask(maskCaat);

var ccCol8 = class_col80.select('classification_2022');
var ccCol9 = class_col90a.select('classification_2022');
var ccCol9b = class_col90b.select('classification_2022');

var conc = ee.Image(0).where(ccCol8.eq(3).and(ccCol9.eq(3)), 1)   // [1]: Concordância
                          .where(ccCol8.neq(3).and(ccCol9.eq(3)), 2)  // [3]: Apenas Landsat
                          .where(ccCol8.eq(3).and(ccCol9.neq(3)), 3)  // [2]: Apenas Sentinel
conc = conc.updateMask(conc.neq(0)).rename('coincidentes');

var concB = ee.Image(0).where(ccCol8.eq(3).and(ccCol9b.eq(3)), 1)   // [1]: Concordância
                          .where(ccCol8.neq(3).and(ccCol9b.eq(3)), 2)  // [3]: Apenas Landsat
                          .where(ccCol8.eq(3).and(ccCol9b.neq(3)), 3);  // [2]: Apenas Sentinel
concB = concB.updateMask(concB.neq(0)).rename('coincidentes');
    
Map.addLayer(ccCol8, vis.classCC, 'class8 ', false);
Map.addLayer(ccCol9, vis.classCC, 'class9 ver 10', false);
Map.addLayer(ccCol9b, vis.classCC, 'class9 ver ultima 22', false );
Map.addLayer(class_col90b.select('classification_2023'), vis.classCC, 'class9 ver ultima 23', false);
Map.addLayer(conc, vis.concordenate, 'Agr cc 4 2022 v10', false);
Map.addLayer(concB, vis.concordenate, 'Agr cc 4 2022 v14', false);

var lstBands = [];
param.years.forEach(function(yyear){
    var banda_activa = 'classification_' + yyear;
    lstBands.push(banda_activa);
});

if (param.exportGeom){
    var nameExp = 'floresta_regions_serra_confusoes';  // floresta_regions_chapada_Araripe
    var featCexp = ee.FeatureCollection([ee.Feature(geometry, {'mask': 1,'regions': nameExp})]);
    processoExportarSHP(featCexp, nameExp, param.asset_Output_shp);
}
var imgLayerFF = ee.Image().byte();
if (param.processLayerFlorest){

    Map.addLayer(img_mask_err, {min:0, max: 1}, 'img_erro', false);
    var recover, nameExport, bandAdd;
    var col8tmp, col9tmp, col9afttmp;
    var layerFlorest = null;
    param.years.forEach(function(yyear){
        var banda_activa = 'classification_' + yyear;
        print("processing ", banda_activa);
        col8tmp = class_col80.select(banda_activa).eq(3);
        col9tmp = class_col90a.select(banda_activa).eq(3);
        col9afttmp = class_col90b.select(banda_activa).eq(3);        
        
        if (yyear !== '2023'){      
            layerFlorest  = col8tmp.or(col9tmp).or(col9afttmp).gt(0);
            print(layerFlorest);
            bandAdd = layerFlorest.updateMask(img_mask_err).selfMask().rename(banda_activa);        
        }else{
            layerFlorest  = class_col80.select('classification_2022').eq(3).or(col9tmp).or(col9afttmp);
            recover = class_col90b.select('classification_2022').eq(3).or(col9afttmp.eq(3));  // diferença entre o 22 e 23
            bandAdd = layerFlorest.updateMask(img_mask_err).unmask(0).or(recover)
                                  .selfMask().rename(banda_activa);
                    
        }
        imgLayerFF = imgLayerFF.addBands(bandAdd);
        if ((yyear === '2022') || (yyear === '2023')){
            Map.addLayer(bandAdd, vis.classCC, 'Florest  ' + yyear, true);
        }
        lstBands.push(banda_activa);

    });
    imgLayerFF = imgLayerFF.select(lstBands);
    imgLayerFF = imgLayerFF.set(
        'version',  2, 
        'biome', 'CAATINGA',
        'type_filter', 'ocorrencia',
        'layer', 'florest',
        'collection', '9.0',
        'sensor', 'Landsat',
        'system:footprint' , bioma5kbuf
    )
    nameExport = 'layer_florest_regions_esp';
    processoExportar(imgLayerFF,  nameExport, bioma5kbuf);
    
}else{

    imgLayerFF = ee.ImageCollection(param.asset_layer_florest).filter(ee.Filter.eq('version', 2)).first();
    Map.addLayer(imgLayerFF.select('classification_1992'), vis.classCC, 'Florest  2022', false);
    Map.addLayer(imgLayerFF.select('classification_2002'), vis.classCC, 'Florest  2023', false);
    Map.addLayer(imgLayerFF.select('classification_2022'), vis.classCC, 'Florest  2022', false);
    Map.addLayer(imgLayerFF.select('classification_2023'), vis.classCC, 'Florest  2023', false);

    if (param.applyFrequency){
        var exp = '100*((b(0) + b(1) + b(2) + b(3) + b(4) + b(5) + b(6) + b(7) + b(8) + b(9) + b(10) + b(11) + b(12)'
        exp += '+ b(13) + b(14) + b(15) + b(16) + b(17) + b(18) + b(19) + b(20) + b(21) + b(22) + b(23) + b(24)'
        exp += '+ b(25) + b(26) + b(27) + b(28) + b(29) + b(30) + b(31) + b(32) + b(33) + b(34) + b(35) + b(36)'
        exp += '+ b(37)+ b(38))/39)'
        
        var florest_frequence = imgLayerFF.eq(3).expression(exp)
        var vegetationMask = ee.Image(0).where(florest_frequence.gt(60), 3)
        var layerFlorestcorreg = imgLayerFF.where(vegetationMask.gt(0), vegetationMask);
        print("know layer florest corregido ", layerFlorestcorreg);
        Map.addLayer(img_mask_err, {min:0, max: 1}, 'img_erro', false);
        Map.addLayer(layerFlorestcorreg.select('classification_2022'), vis.classCC, 'Florest corr 2022', true);
        Map.addLayer(layerFlorestcorreg.select('classification_2023'), vis.classCC, 'Florest corr  2023', true);
        var areaImage = calculateArea (layerFlorestcorreg.select('classification_2022'), bioma5kbuf);
        
        layerFlorestcorreg  = layerFlorestcorreg.set(
            'version',  2, 
            'biome', 'CAATINGA',
            'type_filter', 'frequence',
            'collection', '9.0',
            'sensor', 'Landsat',
            'system:footprint' , bioma5kbuf
        )
        nameExport = 'layer_florest_correcao_freq';
        processoExportar(layerFlorestcorreg,  nameExport, bioma5kbuf);    
    }else{
        
        var featAreas = ee.FeatureCollection([]);
        imgLayerFF = ee.ImageCollection(param.asset_layer_florest)
                                .filter(ee.Filter.eq('type_filter', 'temporal'))
                                .filter(ee.Filter.eq('janela', 5)).first();
        print("know metadata from imgLayerFF ", imgLayerFF);

        if (param.corregirUltimoAno){
            print(' menos ultima banda ', lstBands.slice(0, lstBands.length - 1));
            var imgCorre = ee.Image().byte();
             
            var difAr = bioma5kbuf.difference(limitChapadaAr);
            areaFixa = ee.Feature(difAr, {'value': 0});
            areaToChange = ee.Feature(regionsFlorest, {'value': 1});
            areaTo_mask = ee.FeatureCollection([areaFixa, areaToChange]);
            var img_mask_errArra = areaTo_mask.reduceToImage(['value'], ee.Reducer.first());
            maskCaat = img_mask_err.gte(0);
            Map.addLayer(img_mask_errArra, {min:0, max: 1}, 'img_erro', false);

            var difSerr = bioma5kbuf.difference(limitSerraConf);
            areaFixa = ee.Feature(difSerr, {'value': 0});
            areaToChange = ee.Feature(regionsFlorest, {'value': 1});
            areaTo_mask = ee.FeatureCollection([areaFixa, areaToChange]);
            var img_mask_errSerr = areaTo_mask.reduceToImage(['value'], ee.Reducer.first());            
            param.years.forEach(function(yyear){
                var banda_activa = 'classification_' + yyear;
                print("processing ", banda_activa);
                if (yyear !== '2023'){
                    var layerFFAr = imgLayerFF.select(banda_activa).gt(0);
                    var bandV10 = class_col90a.select(banda_activa).eq(3).updateMask(img_mask_errArra)
                    layerFFAr = layerFFAr.updateMask(bandV10).unmask(0);
                    var layerFFSerr = imgLayerFF.select(banda_activa).updateMask(img_mask_errSerr).unmask(0);
                    layerFFSerr = layerFFSerr.add(layerFFAr.multiply(3)).rename(banda_activa);
                    imgCorre = imgCorre.addBands(layerFFSerr.selfMask());
                    if ((yyear === '2021') || (yyear === '2022')){
                        Map.addLayer(layerFFSerr.selfMask(), vis.classCC, 'Florest  ' + yyear, true);
                    }
                }else{
                    var layer22 = class_col90b.select('classification_2022').eq(3).add(
                        imgCorre.select('classification_2022').eq(3).unmask(0));
                    var layer23 = imgLayerFF.select('classification_2023').unmask(0).gt(0);
                    layer23 = layer23.and(layer22);
                    imgCorre = imgCorre.addBands(layer23.multiply(3).unmask(0).selfMask().rename('classification_2023'))
                    Map.addLayer(layer23.multiply(3).unmask(0).selfMask(), vis.classCC, 'Florest  ' + yyear, true);
                }

            })             
            
            imgCorre  = imgCorre.set(
                                        'version',  3, 
                                        'biome', 'CAATINGA',
                                        'type_filter', 'cor2023',
                                        'collection', '9.0',
                                        'sensor', 'Landsat',
                                        'system:footprint' , bioma5kbuf
                                    )
            nameExport = 'layer_florest_correcao_2023';
            processoExportar(imgCorre,  nameExport, bioma5kbuf);  

        }else{
            
            imgLayerFF = ee.ImageCollection(param.asset_layer_florest)
                                .filter(ee.Filter.eq('type_filter', 'cor2023')).first();
            
            param.years.forEach(function(yyear){
                var banda_activa = 'classification_' + yyear;
                if ((yyear === '2021') || (yyear === '2022') || (yyear === '2023')){
                    Map.addLayer(imgLayerFF.select(banda_activa).selfMask(), vis.classCC, 'Florest  ' + yyear, true);
                }

            })



            param.years.forEach(function(yyear){
                var banda_activa = 'classification_' + yyear;
                print("processing ", banda_activa);
                var imgtmp = imgLayerFF.select(banda_activa)
                var areaImage = calculateArea (imgtmp.selfMask(), bioma5kbuf, yyear);
                featAreas = featAreas.merge(ee.FeatureCollection([areaImage]));
                if ((yyear === '2022') || (yyear === '2023')){
                    Map.addLayer(imgtmp.selfMask(), vis.classCC, 'Florest J5 ' + yyear, true);
                }
            })                
            processoExportarSHPDr(areaImage, "areas_florestas");
        }
    }
}