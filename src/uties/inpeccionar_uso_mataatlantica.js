
//https://code.earthengine.google.com/a439f870a02b371daf094c5b6cf6de34
//https://code.earthengine.google.com/c6be8cee51ed15cb9cd80c031f8f2729
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
} 

var param = { 
    assetMap: 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    asset_filted : 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/TemporalV3/',
    assetclass : 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/misto',       
    assetIm: 'projects/nexgenmap/MapBiomas2/LANDSAT/BRAZIL/mosaics-2',    
    asset_bioma_raster : 'projects/mapbiomas-workspace/AUXILIAR/biomas-raster-41',
    asset_uso_mata_atlantica: 'projects/ee-mapbiomascaatinga04/assets/bacias_mata_caatinga',
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
var lst_bacias_uso_MA = ['757', '758', '759', '76111', '76116', '771', '772', '773'];
var selBacia = '745';
var yearcourrent = 1985;
var banda_activa = 'classification_' + String(yearcourrent);
var FeatColbacia = ee.FeatureCollection(param.assetBacia)
                        .filter(ee.Filter.inList('nunivotto3', lst_bacias_uso_MA)).geometry();
var biomaRaster = ee.Image(param.asset_bioma_raster).eq(5);
biomaRaster = biomaRaster.add(ee.Image(param.asset_bioma_raster).eq(2));

var imgMapCol80= ee.Image(param.assetMap).mask(biomaRaster);
var regionsMA_Caat = ee.FeatureCollection(param.asset_uso_mata_atlantica).geometry()
var imgMapCol9Mix =  ee.ImageCollection(param.asset_filted)
                            .filter(ee.Filter.eq('version', 22))
                            .filter(ee.Filter.eq('janela', 5))
                            .filter(ee.Filter.inList('id_bacia', lst_bacias_uso_MA))
                            .min();


print("imagem no Asset Geral Mapbiomas Col 8", imgMapCol80);
// print("imagem no Asset Geral X Bacias col 8", imgMapCol8V6);

var bufferBacia = FeatColbacia.filter(ee.Filter.eq('nunivotto3', selBacia)).geometry()
var polRecort = regionsMA_Caat
print("ver properties ", polRecort)
var changePixel = function(imgClass_temp){
    var lstBandNames = ee.List([])
    var imgClassFinal = ee.Image().toByte();

    print("properties ", dictProp);
    polRecort = polRecort.geometry()
    var classDe = dictProp['de']
    
    var areaToChange = ee.Feature(FeatColbacia.difference(polRecort), {'value': 1})
    var areaFixa = ee.Feature(polRecort, {'value': 0})
    var areaTo_mask = ee.FeatureCollection([areaFixa, areaToChange])
    var img_mask_err = areaTo_mask.reduceToImage(['value'], ee.Reducer.first())
    
    param.anos.forEach(function(yyear) {
        print("###### change pixels from " + classDe.toString() + " TO " + classPara.toString() + " in year " + yyear)
        var bandaAct = 'classification_' + yyear 
        lstBandNames = lstBandNames.add(bandaAct)
        var imgClasBand = imgClass_temp.select(bandaAct)
        layerYY21 = imgMapCol80.select(bandaAct).eq(15) // get class pastagem
        layerYY21 = layerYY21.and(img_mask_err)

        imgClasBand = imgClasBand.where(layerYY21.eq(1), layerYY21.multiply(21))

        imgClassFinal = imgClassFinal.addBands(imgClasBand.rename(bandaAct))
    })
   
    Map.addLayer(img_mask_err, {min: 0, max: 1}, 'dif')
    return imgClassFinal.select(lstBandNames)
    
}



var imgMista = changePixel(imgMapCol9Mix)
var imgMapmisto = imgMista.select(banda_activa)


var Mosaicos = ee.ImageCollection(param.assetIm).filter(
                        ee.Filter.eq('biome', 'CAATINGA')).select(param.bandas);
                        
var mosaic_year = Mosaicos.filter(ee.Filter.eq('year', yearcourrent)).median();                     
Map.addLayer(FeatColbacia, {color: 'green'}, 'bacia', false);
Map.addLayer(mosaic_year, visualizar.visMosaic,'Mosaic Col8', false);

var imgMapCol8temp = imgMapCol80.select(banda_activa).remap(param.classMapB, param.classNew);

Map.addLayer(imgMapCol8temp,  visualizar.visclassCC, 'Col8 '  + String(yearcourrent), false);
Map.addLayer(imgMapCol9Mix.select(banda_activa),  visualizar.visclassCC, 'Col9_ClassV22');
Map.addLayer(imgMapmisto,  visualizar.visclassCC, 'ClassMisto');
