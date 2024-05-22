

var asset_MapC9X = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVX';
var asset_ptosDifLapigvsCol8 = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/occTab_acc_Dif_Caat_mapbiomas_80_integration_v1';
var assetBacia = "projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga";
var assetSamples = 'users/vieiramesquita/MAPBIOMAS/mapbiomas_100k_all_points_w_edge_and_edited_v7';
var assetBiomas =  'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil';
var limitCaatinga = ee.FeatureCollection(assetBiomas).filter(ee.Filter.eq('Bioma', 'Caatinga')).geometry();
// print(limitCaatinga)
var pontosLapig = ee.FeatureCollection(assetSamples).filterBounds(limitCaatinga);
print("Pontos Lapig ", pontosLapig.size());

var anos = [
    '1985','1986','1987','1988','1989','1990','1991','1992','1993','1994',
    '1995','1996','1997','1998','1999','2000','2001','2002','2003','2004',
    '2005','2006','2007','2008','2009','2010','2011','2012','2013','2014',
    '2015','2016','2017','2018','2019','2020','2021','2022'
];
var lsAllprop = [];
anos.forEach(function(yyear){
    lsAllprop.push("CLASS_" + yyear);
})
print("show all bands properties from shp pontos Lapig ", lsAllprop);
var selBacia = '741';
var yearcourrent = 2020;
var banda_activa = 'classification_' + String(yearcourrent);

var FeatColbacia = ee.FeatureCollection(assetBacia).filter(ee.Filter.eq('nunivotto3', selBacia)).geometry();
var ptosRefLapig = ee.FeatureCollection(asset_ptosDifLapigvsCol8).filterBounds(FeatColbacia);
print("número de pontos na bacia 741 ", ptosRefLapig.size());
print(ptosRefLapig);
var imgMapCol9GTB =  ee.ImageCollection(asset_MapC9X)
                            .filter(ee.Filter.eq('version', 5))
                            .filter(ee.Filter.eq("classifier", "GTB"))
                            .filter(ee.Filter.eq("id_bacia", selBacia))
                            .first();
                            // .select(banda_activa);

print("show image map loaded ", imgMapCol9GTB);
var  pointAccTemp = ee.Image(imgMapCol9GTB).unmask(0).sampleRegions({
        collection: ptosRefLapig, 
        properties:  lsAllprop,  
        scale: 30, 
        geometries: true
});

print("Pontos coletados ", pointAccTemp.size());
print(pointAccTemp)


print("ultimos pontos do lapig ", pontosLapig.filterBounds(FeatColbacia));