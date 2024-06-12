
var nameBacias = [
    '741', '7421','7422','744','745','746','751','752','7492',
    '753', '754','755','756','757','759','7621','7622','763', '758',
    '764','765','766','771','772', '7741','7742','775', '773',
    '776','76111','76116','7612','7613','7614','7615','777',
    '778','7616','7617','7618', '7619', '767', '758', '773'
] 
var newListBasin = [
    "7754","7691","7581","7625","7584","751","7614","752","7616",
    "745","7424","773","7612","7613","7618","7561","755","7617","7564",
    "761111","761112","7741","7422","76116","7761","7671","7615","7411",
    "7764","757","771","7712","766","7746","753","764","7541","7721","772",
    "7619","7443","765","7544","7438","763","7591","7592","7622","746"

]
var lstBasinLitoral = ["7581","773","761112","757","771","772","7591"];
function processoExportarSHP(ROIsFeat, nameB){
    var idAssetExp = "projects/mapbiomas-arida/ALERTAS/auxiliar/" + nameB
    var optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'assetId': idAssetExp        
        };
    Export.table.toAsset(optExp);
    print("salvando ... " + nameB + "..!")  ;  
}

var asset_bacias = "projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga";
var asset_bacias2 = "users/mapbiomascaatinga04/bacias_final_caatingaa";
var bacias = ee.FeatureCollection(asset_bacias);
var bacias2 = ee.FeatureCollection(asset_bacias2);
print(bacias2);
var lstIdBasin = bacias.reduceColumns(ee.Reducer.toList(), ['nunivotto3']).get('list').getInfo();
var exportBuffer = false;
var getIdBasinbef = true;
var getVizinhas = false;
print("know id basin Caatinga ", lstIdBasin);

var lstIdBasin = bacias2.reduceColumns(ee.Reducer.toList(), ['nunivotto4']).get('list');
print("lista de nunivotto4 ", lstIdBasin);

var lstBasinMA = bacias2.filterBounds(geometry).reduceColumns(ee.Reducer.toList(), ['nunivotto4']).get('list');
print("lista de nunivotto4 litoral ", lstBasinMA);

var dictBasin = {
    "7754" : "775",
    "7581" : "758",
    "7625" : "7621",
    "7584" : "758",
    "751" : "751",
    "7614" : "7614",
    "752" : "752",
    "7616" : "7616",
    "745" : "745",
    "7424" : "7421",
    "773" : "773",
    "7612" : "7612",
    "7613" : "7613",
    "7618" : "7618",
    "7561" : "756",
    "755" : "755",
    "7617" : "7617",
    "7564" : "756",
    "761111" : "76111",
    "761112" : "76111",
    "7741" : "7741",
    "7422" : "7422",
    "76116" : "76116",
    "7761" : "776",
    "7671" : "767",
    "7615" : "7615",
    "7411" : "741",
    "7764" : "776",
    "757" : "757",
    "771" : "771",
    "7712" : "771",
    "766" : "766",
    "7746" : "7741",
    "753" : "753",
    "764" : "764",
    "7541" : "754",
    "7721" : "772",
    "772" : "772",
    "7619" : "7619",
    "7443" : "744",
    "765" : "765",
    "7544" : "754",
    "7438" : "744",
    "763" : "763",
    "7591" : "759",
    "7592" : "759",
    "7622" : "7622",
    "746" : "746",
    "7691" : "766"
} 
var lst6 = ["761111","761112"]
var lst4 = ["7754","7581","7691","7584",]
 var baciasId ;

if (getIdBasinbef){
    var allbasinReg = bacias2.map(function(feat){
                            var featBef = bacias.filterBounds(feat.geometry().centroid())
                            var idBasin = ee.Algorithms.If(
                                                    ee.String(feat.get('nunivotto4')).equals('7691'),
                                                    '767',
                                                    featBef.get('nunivotto3')
                                                );
                            return feat.set('nunivotto3', idBasin);
                        });

    print("know how featureCollection are ", allbasinReg);
    print("ver filter ", allbasinReg.filter(ee.Filter.eq('nunivotto3', '767')))
    allbasinReg = ee.FeatureCollection(allbasinReg);
    processoExportarSHP(allbasinReg, 'bacias_hidrografica_caatinga49div');
}
if (getVizinhas){
    var assetBasin49 = 'projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga49div';
    var basin49 = ee.FeatureCollection(assetBasin49);
    newListBasin.forEach(function(name){
        print("bacias ", name)
        var bacia_a = basin49.filter(ee.Filter.eq('nunivotto4', name));
        var bacias_viz = basin49.filterBounds(bacia_a)
        var lstIdBasin = bacias_viz.reduceColumns(ee.Reducer.toList(), ['nunivotto4']).get('list')
        print("dict basin vizinhas ", lstIdBasin);
    
    });
}
if (exportBuffer){
    var assetBasin49 = 'projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga49div';
    var basin49 = ee.FeatureCollection(assetBasin49);
    var basin49Buffer = basin49.map(function(feat){
                            return feat.buffer(5000)
                        })
    print('conferir buffer ', basin49Buffer );
  //buffer5k
    Map.addLayer(basin49Buffer, {}, 'bacias Buffer');
    processoExportarSHP(basin49Buffer, 'bacias_hidrografica_caatinga49divbuffer5k');
}else{
    var assetBasin49 = 'projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga49div';
    var basin49 = ee.FeatureCollection(assetBasin49);
    print(basin49.size());
    var lstIdBasin = basin49.reduceColumns(ee.Reducer.toList(2), ['nunivotto4','nunivotto3']).get('list')
    print("metadata par properties basin ", lstIdBasin);
}


Map.addLayer(bacias , {color: 'green'}, 'bacias');
Map.addLayer(bacias2 , {color: 'yellow'}, 'baciasv2');
Map.addLayer(bacias2.filter(ee.Filter.eq('nunivotto4', '7754')),{}, 'bcias')



