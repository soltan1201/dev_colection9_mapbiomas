

var Palettes = require('users/mapbiomas/modules:Palettes.js');
var palette = Palettes.get('classification8');
var vis = {
    cobertura : {
        'min': 0,
        'max': 62,
        'palette': palette,
        'format': 'png'
    },
    diferencia: {
        'min': 1,
        'max': 2,
        'palette': 'd52a14,a2d514',
        'format': 'png'
    }
};
var param = {
    'assetMapbiomas60': 'projects/mapbiomas-workspace/public/collection6/mapbiomas_collection60_integration_v1',
    'assetMapbiomas71': 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1',
    'assetMapbiomas80': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    'assetMapbiomas90': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVX', 
    "classifier": "RF", // "GTB"
    "version": 5,
    "showLegend": true
}

Map.addLayer(ee.Image.constant(1), {min: 0, max: 1}, 'base');
var asset_ImBiomas = 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019-raster';
var limitBioma = ee.Image(asset_ImBiomas).eq(5).selfMask();
Map.addLayer(limitBioma, {}, 'Bioma Raster', false)

// Define a list of years to export
var years = [
    '1985', '1986', '1987', '1988', '1989', 
    // '1990', '1991', '1992', '1993', '1994', 
    // '1995', '1996', '1997', '1998', '1999', 
    // '2000', '2001', '2002', '2003', '2004', 
    // '2005', '2006', '2007', '2008', '2009', 
    // '2010', '2011', '2012', '2013', '2014', 
    // '2015', '2016', '2017', '2018', '2019', 
    // '2020', '2021', '2022'
];

//var years = [2021]
var igual_Class71_90GTB = null;    
var maskChangeCC71_90GTB = null; 
var igual_Class71_90RF = null;    
var maskChangeCC71_90RF = null; 
var igual_Class80_90GTB = null;     
var maskChangeCC80_90GTB = null; 
var igual_Class80_90RF = null;     
var maskChangeCC80_90RF = null; 

var class_in =  [3,4,5,6,49,11,12,13,32,29,50,15,19,39,20,40,62,41,36,46,47,48,9,21,22,23,24,30,25,33,31]
var class_out = [3,4,3,6,3,11,12,12,12,29,12,21,21,21,21,21,21,21,21,21,21,21,21,21,25,25,25,25,25,33,33]

years.forEach(function(year) {  
    var band_activa = 'classification_' + year;
    // 7.1 - Classificação Integração 
    var mapsCol71 = ee.Image(param.assetMapbiomas71)
                                    .mask(limitBioma).select(band_activa)
                                    .remap(class_in, class_out)//.rename('class')
    
    // 8.0 - Classificação Integração 
    var mapsCol80 = ee.Image(param.assetMapbiomas80)
                        .mask(limitBioma).select(band_activa)
                        .remap(class_in, class_out)//.rename('class')
    
    // 9.0 - Classificação Integração 
    var mapsCol90GTB = ee.ImageCollection(param.assetMapbiomas90)
                            .filter(ee.Filter.eq('version', param.version))
                            .filter(ee.Filter.eq("classifier", "GTB")).min()
                            .mask(limitBioma).select(band_activa)
                            .remap(class_in, class_out)//.rename('class')

    var mapsCol90RF = ee.ImageCollection(param.assetMapbiomas90)
                            .filter(ee.Filter.eq('version', param.version))
                            .filter(ee.Filter.eq("classifier", "RF")).min()
                            .mask(limitBioma).select(band_activa)
                            .remap(class_in, class_out)//.rename('class')                        
    
    igual_Class71_90GTB = mapsCol71.eq(mapsCol90GTB).remap([1],[2]);    
    maskChangeCC71_90GTB = limitBioma.blend(igual_Class71_90GTB);
    igual_Class71_90RF = mapsCol71.eq(mapsCol90RF).remap([1],[2]);    
    maskChangeCC71_90RF = limitBioma.blend(igual_Class71_90RF);
    igual_Class80_90GTB = mapsCol80.eq(mapsCol90GTB).remap([1],[2]);    
    maskChangeCC80_90GTB = limitBioma.blend(igual_Class80_90GTB);
    igual_Class80_90RF = mapsCol80.eq(mapsCol90RF).remap([1],[2]);    
    maskChangeCC80_90RF = limitBioma.blend(igual_Class80_90RF);
    
    Map.addLayer(mapsCol71, vis.cobertura, 'Col 7.1 '+ year, false);
    Map.addLayer(mapsCol80, vis.cobertura, 'Col 8.0 '+ year, false);
    Map.addLayer(mapsCol90GTB, vis.cobertura, 'C9 GTB v5 '+ year, false);
    Map.addLayer(mapsCol90RF, vis.cobertura, 'C9 RF v5 '+ year, false);
    Map.addLayer(maskChangeCC71_90GTB, vis.diferencia, 'maskChGTBcc71_90_'+ year, false);
    Map.addLayer(maskChangeCC71_90RF, vis.diferencia, 'maskChRFcc71_90_'+ year, false);
    Map.addLayer(maskChangeCC80_90GTB, vis.diferencia, 'maskChGTBcc80_90_'+ year, false);
    Map.addLayer(maskChangeCC80_90RF, vis.diferencia, 'maskChRFcc80_90_'+ year, false);

    // if (year === '1985'){
    //     class_mask_final = mask_final.rename('mask_' + year) 
    // }else{
    //     class_mask_final = class_mask_final.addBands(mask_final.rename('mask_' + year)); 
    // }
  
})

if (param.showLegend){
    var legend = ui.Panel({style: {position: 'bottom-center', padding: '8px 15px'}}); 

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
    value: 'Pixels change',
    style: {fontWeight: 'bold',
        fontSize: '16px',
        margin: '0px 0 4px 0px'}});

    legend.add(title);
    legend.add(makeRow('#d52a14','1 - Pixels com Mudanças'));
    legend.add(makeRow('#a2d514','2 - Pixels Estaveis'));
    Map.add(legend);

}