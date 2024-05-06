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
    assetMapC7: 'projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_integration_v1',
    assetMapC8: 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    asset_MapC9X : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVX',
    asset_MapC9P : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVP',
    // assetclass : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/class_filtered_Fq',
    asset_Gapfill : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Gap-fill',   
    asset_Spatial : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Spatial', 
    asset_mixed: 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/toExport',
    asset_baciasN1raster: 'projects/mapbiomas-workspace/AUXILIAR/bacias-nivel-1-raster',
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
    classMapB: [3, 4, 5, 9,12,13,15,18,19,20,21,22,23,24,25,26,29,30,31,32,33,36,39,40,41,46,47,48,49,50,62],
    classNew:  [3, 4, 3, 3,12,12,15,18,18,18,21,22,22,22,22,33,29,22,33,12,33,18,18,18,18,18,18,18, 3,12,18],

}
var selBacia = 'all';
var yearcourrent = 2020;
var version = 5;
var assetCol9 = param.asset_MapC9X;
if (version > 5){
    assetCol9 = param.asset_MapC9P;
}
var banda_activa = 'classification_' + String(yearcourrent)
var FeatColbacia = ee.FeatureCollection(param.assetBacia);

var baciaRaster = ee.Image(param.asset_baciasN1raster);
var maskBacia = baciaRaster.eq(104).add(baciaRaster.eq(103))
                          .add(baciaRaster.eq(106)).add(baciaRaster.eq(107));

var imgMapCol71= ee.Image(param.assetMapC7).updateMask(maskBacia.gt(0))
                        .select(banda_activa);
var imgMapCol8= ee.Image(param.assetMapC8).updateMask(maskBacia.gt(0))
                        .select(banda_activa);

var imgMapCol9GTB =  ee.ImageCollection(assetCol9)
                            .filter(ee.Filter.eq('version', version))
                            .filter(ee.Filter.eq("classifier", "GTB"))
                            .select(banda_activa);
print("  imgMapCol9GTB", imgMapCol9GTB);
var imgMapCol9GF = ee.ImageCollection(param.asset_Gapfill)
                        .filter(ee.Filter.eq('version', version))
                        .select(banda_activa);

var imgMapCol9SP = ee.ImageCollection(param.asset_Spatial)
                        .filter(ee.Filter.eq('version', version))
                        .select(banda_activa);
var imgMapmixed = ee.ImageCollection(param.asset_mixed)
                        .filter(ee.Filter.eq('version', version))
                        .map(function(img){
                            return ee.Image.cat(img).toByte();
                        })
                        .select(banda_activa);                        

var Mosaicos = ee.ImageCollection(param.assetIm).filter(
                        ee.Filter.eq('biome', 'CAATINGA')).select(param.bandas);

// ========================================================================= //
// set as 'all' to show all map or set the basin from pamareter dictionary
// ========================================================================= //
var imgMapCol9GTBjoin = null;
var imgMapCol9SPjoin = null;
var imgMapCol9GFjoin = null;
var imgMapmixedJoin = null;
if (selBacia === 'all'){
    imgMapCol9GTBjoin = imgMapCol9GTB.min();
    imgMapCol9SPjoin = imgMapCol9SP.min();
    imgMapCol9GFjoin = imgMapCol9GF.min();
    imgMapmixedJoin = imgMapmixed.min();
}else{
    FeatColbacia = FeatColbacia.filter(ee.Filter.eq('nunivotto3', selBacia));   
    imgMapCol9GTBjoin = imgMapCol9GTB.filter(ee.Filter.eq("id_bacia", selBacia)); 
    imgMapCol9SPjoin = imgMapCol9SP.filter(ee.Filter.eq("id_bacia", selBacia)); 
    imgMapCol9GFjoin = imgMapCol9GF.filter(ee.Filter.eq("id_bacia", selBacia)); 
    imgMapmixedJoin = imgMapmixed.filter(ee.Filter.eq("id_bacia", selBacia));
    Mosaicos = Mosaicos.filterBounds(FeatColbacia);
}

print(" 📍 imagem no Asset Geral Mapbiomas Col 7.1  ‼️", imgMapCol71);
print(" 📍 imagem no Asset Geral Mapbiomas Col 8.0  ‼️", imgMapCol8);
print(" 📍 imagem no Asset Geral X Bacias col 9 GTB", imgMapCol9GTB);
print(" 📍 imagem no Asset Geral X Bacias pos-Class col 9 Gap Fill", imgMapCol9GFjoin);
print(" 📍 imagem no Asset Geral X Bacias pos-Class col 9 Spatial", imgMapCol9SPjoin);
print(" 📍 imagem no Asset Geral X Bacias pos-Class col 9 Mixed", imgMapmixedJoin);

var mosaic_year = Mosaicos.filter(ee.Filter.eq('year', yearcourrent)).median();                     
Map.addLayer(FeatColbacia, {color: 'green'}, 'bacia');
Map.addLayer(mosaic_year, visualizar.visMosaic,'Mosaic Col8');

// var imgMapCol71temp = imgMapCol71.select(banda_activa).remap(param.classMapB, param.classNew);
// var imgMapCol8temp = imgMapCol8.select(banda_activa).remap(param.classMapB, param.classNew);

Map.addLayer(imgMapCol9SPjoin,  visualizar.visclassCC, 'Class Spatial', false);
Map.addLayer(imgMapCol9GFjoin,  visualizar.visclassCC, 'Class Gap-fill', false);
Map.addLayer(imgMapCol9GTBjoin,  visualizar.visclassCC, 'Class GTB ' + String(version), false);
Map.addLayer(imgMapmixedJoin,  visualizar.visclassCC, 'Class Mixed', false);
Map.addLayer(imgMapCol71, visualizar.visclassCC,'Col71_' + String(yearcourrent), false);
Map.addLayer(imgMapCol8,  visualizar.visclassCC, 'Col8_'+ String(yearcourrent), false);






