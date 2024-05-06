var building = false;
var asset_buffer = 'users/CartasSol/shapes/caatinga_buffer5km';
var asset_IBGE= 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019';
var caatOrg = ee.FeatureCollection(asset_IBGE).filter(ee.Filter.eq('CD_Bioma', 2));
print("caatinga biome ", caatOrg);
if (building){
    var featCaat = ee.Feature(caatOrg.geometry().buffer(5000), 
                            {'buffer_km': 5, 'CD_Bioma': 2, 'biome': 'Caatinga'});
    var newFeatCaat = ee.FeatureCollection([featCaat]);
    
    Export.table.toAsset({
      collection: newFeatCaat, 
      description: 'caatinga_buffer5km', 
      assetId: asset_buffer, 
      maxVertices: 1e12
    });
}else{
    var newFeatCaat = ee.FeatureCollection(asset_buffer);
}

Map.addLayer(caatOrg, {color: 'green'}, 'Caatinga limit');
Map.addLayer(newFeatCaat, {color: 'yellow'}, 'Caatinga Buffer');