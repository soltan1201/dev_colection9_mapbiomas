/// exporta a o vetor de pontos para o asset
function processoExportarSHP(ROIsFeat, nameB, asset_path){
    
    var optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'assetId': asset_path + nameB          
        };
    Export.table.toAsset(optExp);
    print("salvando ... " + nameB + "..!")  ;  
}

var asset_divN245 = 'projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_hidrografica_caatinga_BdivN245';
var asset_divN5 = 'projects/mapbiomas-arida/ALERTAS/auxiliar/bacias_nivel_5_clipReg_Caat';
var asset_output = 'projects/mapbiomas-arida/ALERTAS/auxiliar/';
var divN245 = ee.FeatureCollection(asset_divN245);
var divN5 = ee.FeatureCollection(asset_divN5);

print("divide a Nivel 245 ", divN245.limit(5));
print("divide a Nivel 5", divN5.limit(5));
print("Quantidade de featueres ", divN5.size());

var newdivN5 = divN5.map(
            function(feat){
                var centroif = feat.centroid(0.01).geometry();
                var featN245 = divN245.filterBounds(centroif).first();
                        
                return feat.copyProperties(featN245, ["nunivotto3","wts_cd_pfa"])        
          });
          
print("new properties of div N5 ", newdivN5.first());
var nameExp = 'bacias_nivel_5_prop24_clipReg_Caat';
processoExportarSHP(newdivN5, nameExp, asset_output);

Map.addLayer(divN245, {color: 'green'}, 'divN245');
Map.addLayer(divN5, {color: 'yellow'}, 'divN5');