

//var imageVisParam = {"opacity":1,"bands":["classes"],"min":1,"palette":["cecece","dae792","ff9a7c","ef00ff","ff3131"]};
var palettes = require('users/mapbiomas/modules:Palettes.js');
var legend = ui.Panel({style: {position: 'bottom-left', padding: '8px 15px'}});
var vis = {
    classeCruzado : {
        "opacity":1,
        "bands":["classes"],
        "min":1,
        "max": 5,
        "palette":["faf3dd","c8d5b9","f19c79","fec601","013a63"]
    },
    visIncidente: {
        max: 8,
        min: 0,
        palette: [
            '#C8C8C8','#FED266','#FBA713','#cb701b','#cb701b','#a95512',
            '#a95512','#662000','#662000','#cb181d'
        ]
    },
    visState : {
        max: 5,
        min: 1,
        palette: ['#C8C8C8','#AE78B2','#772D8F','#4C226A','#22053A']
    },
    colecao: { 
        'min': 0, 
        'max': 62,  
        'palette': palettes.get('classification8')
    }
};
var anos = [
    '1985', '1986', '1987', '1988', '1989', 
    // '1990', '1991', '1992', '1993', '1994', 
    // '1995', '1996', '1997', '1998', '1999', 
    // '2000', '2001', '2002', '2003', '2004', 
    // '2005', '2006', '2007', '2008', '2009', 
    // '2010', '2011', '2012', '2013', '2014', 
    // '2015', '2016', '2017', '2018', '2019', 
    // '2020', '2021', '2022'
];
Map.addLayer(ee.Image.constant(1), {min: 0, max: 1}, 'base', false);

//var biomes = ee.Image('projects/mapbiomas-workspace/AUXILIAR/biomas-raster-41')
//var pampa = biomes.mask(biomes.eq(6))
var params = {
    asset_Col6 : 'projects/mapbiomas-workspace/public/collection6/mapbiomas_collection60_integration_v1',
    asset_Col7 : 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1',
    asset_Col8 : 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    asset_Col9 : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVX',
    asset_biomas: 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019-raster',
    asset_sphBiomas: "projects/mapbiomas-workspace/AUXILIAR/biomas-2019",
    assetOutput: 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/estabilidade_colecoes',
    lstClassMB:  [3, 4, 5,49, 9, 11, 12, 13, 29, 50, 15, 21, 23, 24, 25, 30, 31, 33, 39, 20, 40, 62, 41, 36, 46, 47, 48],
    lstClassRC:  [3, 4, 3, 3,22, 12, 12, 12, 12, 12, 21, 21, 22, 22, 22, 30, 33, 33, 21, 21, 21, 21, 21, 21, 21, 21, 21],
    version: 5,
    showLegend: false,
    showMaps: false
}
var bioma =  'Caatinga'; // "Amazônia", "Caatinga", "Cerrado", "Mata Atlântica", "Pampa", "Pantanal".
// Asset of regions for which you want to calculate statistics
var assetTerritories = "projects/mapbiomas-workspace/AUXILIAR/ESTATISTICAS/COLECAO8/VERSAO-1/state-raster";
var outGTB = null;
var outRF = null;
//var dirCol7 = 'projects/mapbiomas-workspace/COLECAO7/integracao';
//var inputVersion = '0-29';

// --- --- --- Caaatinga --------------------------
var limitBioma = ee.FeatureCollection(params.asset_sphBiomas)
                    .filter(ee.Filter.eq("Bioma", bioma));

var biomas = ee.Image(params.asset_biomas).eq(5).selfMask(); 

var mapsCol71 = ee.Image(params.asset_Col7).updateMask(biomas);
var mapsCol80 = ee.Image(params.asset_Col8).updateMask(biomas);//.filterMetadata('version','equals','0-29').mosaic()

// 9.0 - Classificação Integração 
var mapsCol90GTB = ee.ImageCollection(params.asset_Col9)
                            .filter(ee.Filter.eq('version', params.version))
                            .filter(ee.Filter.eq("classifier", "GTB")).min()
                            .updateMask(biomas)//.select(band_activa)
                            //.remap(class_in, class_out)//.rename('class')

var mapsCol90RF = ee.ImageCollection(params.asset_Col9)
                            .filter(ee.Filter.eq('version', params.version))
                            .filter(ee.Filter.eq("classifier", "RF")).min()
                            .updateMask(biomas)//.select(band_activa)
                            //.remap(class_in, class_out)//.rename('class')    
//Map.addLayer(col7,{},'col7')

print("Coleção publicada 7.1 ", mapsCol71);
print("Coleção publicada 8.0 ", mapsCol80);
print("Coleção em desenvolvimento 9.0 versão 5 classifier GTB ", mapsCol90GTB);
print("Coleção em desenvolvimento 9.0 versão 5 classifier RF ", mapsCol90RF);

//exporta a imagem classificada para o asset
var processoExportarSHPDrive = function (shpTable, nameTable){
    print("saving " + nameTable);
    var optExp = {
            collection: shpTable,
            description: nameTable,
            folder: 'AREA-EXPORT',
            fileNamePrefix: nameTable,
            fileFormat: 'CSV'
      };
    Export.table.toDrive(optExp)
    print("salvando ... " + nameTable + "..!");
};


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

/**
 * Calculate area crossing a cover map (deforestation, mapbiomas)
 * and a region map (states, biomes, municipalites)
 * @param image 
 * @param territory 
 * @param geometry
 */
var calculateArea = function (image, territory, geometry) {

    var reducer = ee.Reducer.sum().group(1, 'class').group(1, 'territory');

    var territotiesData = pixelArea.addBands(territory).addBands(image)
        .reduceRegion({
            reducer: reducer,
            geometry: geometry,
            scale: scale,
            maxPixels: 1e13
        });

    territotiesData = ee.List(territotiesData.get('groups'));

    var areas = territotiesData.map(convert2table);

    areas = ee.FeatureCollection(areas).flatten();

    return areas;
};

    
// anos = [2019]
anos.forEach(function(ano){   
    var img71 = mapsCol71.select('classification_' + ano )
                    .remap(params.lstClassMB, params.lstClassRC)
                    .rename('c71_class_' + ano);   
    var img8 = mapsCol80.select('classification_' + ano )
                    .remap(params.lstClassMB, params.lstClassRC)
                    .rename('c8_class_' + ano);
    var img9GTB = mapsCol90GTB.select('classification_' + ano )
                        .remap(params.lstClassMB, params.lstClassRC);
    var img9RF = mapsCol90GTB.select('classification_' + ano )
                        .remap(params.lstClassMB, params.lstClassRC)
    var imgClassGTB = img71.addBands(img8).addBands(img9GTB);
    var imgClassRF = img71.addBands(img8).addBands(img9RF);

    var incidentesGTB = imgClassGTB.reduce(ee.Reducer.countRuns()).subtract(1).rename('incidentes');
    var incidentesRF = imgClassRF.reduce(ee.Reducer.countRuns()).subtract(1).rename('incidentes');
    var statesGTB = imgClassGTB.reduce(ee.Reducer.countDistinctNonNull()).rename('states');
    var statesRF = imgClassRF.reduce(ee.Reducer.countDistinctNonNull()).rename('states');
    
    
    
    var modaGTB = imgClassGTB.reduce(ee.Reducer.mode());
    var modaRF = incidentesRF.reduce(ee.Reducer.mode());
    ///logica de definição de classes está embasada no fato de termos 3 coleções de entrada
    //para analisar mais coleções a logica precisa ser reestruturada
    var clas1_GTB = incidentesGTB.eq(0).selfMask();
    var clas2_GTB = incidentesGTB.eq(1).and(imgClassGTB.select(2).subtract(modaGTB).eq(0)).selfMask();
    var clas3_GTB = incidentesGTB.eq(1).and(imgClassGTB.select(0).subtract(modaGTB).eq(0)).selfMask();
    var clas4_GTB = incidentesGTB.eq(2).and(statesGTB.eq(2)).selfMask();
    var clas5_GTB = incidentesGTB.eq(2).and(statesGTB.eq(3)).selfMask();

    var clas1_RF = incidentesRF.eq(0).selfMask();
    var clas2_RF = incidentesRF.eq(1).and(imgClassRF.select(2).subtract(modaRF).eq(0)).selfMask();
    var clas3_RF = incidentesRF.eq(1).and(imgClassRF.select(0).subtract(modaRF).eq(0)).selfMask();
    var clas4_RF = incidentesRF.eq(2).and(statesRF.eq(2)).selfMask();
    var clas5_RF = incidentesRF.eq(2).and(statesRF.eq(3)).selfMask();
    
    outGTB = clas1_GTB.blend(clas2_GTB.multiply(2))
                   .blend(clas3_GTB.multiply(3))
                   .blend(clas4_GTB.multiply(4))
                   .blend(clas5_GTB.multiply(5))
                   .rename('classes');

    outRF = clas1_RF.blend(clas2_RF.multiply(2))
                   .blend(clas3_RF.multiply(3))
                   .blend(clas4_RF.multiply(4))
                   .blend(clas5_RF.multiply(5))
                   .rename('classes');
    
    if (ano === anos[4]){
        print("ver image metadados imgClass GTB", imgClassGTB);
        print("ver image metadados imgClass RF", imgClassRF);
        params.showMaps = true;
    }
    // Map.addLayer(incidentes, vis.visIncidente, 'incidentes_' + ano, false);
    // Map.addLayer(states, vis.visState, 'states_' + ano, false);
    Map.addLayer(img71, vis.colecao, 'col 7.1_' + ano, false);
    Map.addLayer(img8, vis.colecao, 'col 8.0_' + ano, false);
    Map.addLayer(img9GTB, vis.colecao, 'col devGTB 9.0_' + ano, false);
    Map.addLayer(img9RF, vis.colecao, 'col devRF 9.0_' + ano, false);
    Map.addLayer(outGTB, vis.classeCruzado, 'coincidencia_GTB_' + ano, params.showMaps);
    Map.addLayer(outRF, vis.classeCruzado, 'coincidencia_RF_' + ano, params.showMaps);   

});


// Paint all the polygon edges with the same number and width, display.
var outline = ee.Image().byte().paint({
  featureCollection: limitBioma,
  color: 1,
  width: 1.5
});
Map.addLayer(outline, {palette: 'FF0000'}, 'LimiteCaatinga');

var makeRow = function(color, name) {
  var colorBox = ui.Label({
    style: {color: '#ffffff',
      backgroundColor: color,
      padding: '10px',
      margin: '0 0 4px 0',
    }
  });
  var description = ui.Label({
    value: name,
    style: {
      margin: '0px 0 4px 6px',
    }
  }); 
  return ui.Panel({
    widgets: [colorBox, description],
    layout: ui.Panel.Layout.Flow('horizontal')}
)};

var title = ui.Label({
  value: 'Coincidencias das classes',
  style: {
        fontWeight: 'bold',
        fontSize: '16px',
        margin: '0px 0 4px 0px'
    }
});

legend.add(title);
legend.add(makeRow('#faf3dd','Classe 1'));
legend.add(makeRow('#c8d5b9','Classe 2'));
legend.add(makeRow('#f19c79','Classe 3'));
legend.add(makeRow('#fec601','Classe 4'));
legend.add(makeRow('#013a63','Classe 5'));
Map.add(legend);


if (params.showLegend){

    /**
     * @description
     *    calculate area
     * @author
     *    João Siqueira
     */

    // Change the scale if you need.
    var scale = 30;

    /**
     * Territory image
     */
    var territory = ee.Image(assetTerritories);

    // LULC mapbiomas image
    var mapbiomas = ee.Image(out).selfMask();

    // Image area in km2
    var pixelArea = ee.Image.pixelArea().divide(1000000);

    // Geometry to export
    var geometry = mapbiomas.geometry();

    var years = [2022];
    var areas = years.map(
        function (year) {
            var image = mapbiomas.select('classes');
            var areas = calculateArea(image, territory, geometry);
            // set additional properties
            areas = areas.map(
                function (feature) {
                    return feature.set('year', year);
                }
            );
            return areas;
        }
    );
    areas = ee.FeatureCollection(areas).flatten();
    processoExportarSHPDrive(areas,  'areas-filtro-UF');
}