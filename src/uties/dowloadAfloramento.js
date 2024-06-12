
//https://code.earthengine.google.com/b2a926c5ecb0a208498dd6072705ccae
var asset_afloramento = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/layer_afloramento_cluster';
var imgAfloramento = ee.Image(asset_afloramento);

Map.addLayer(imgAfloramento.selfMask(), {min: 0, max: 1, palette: 'red'}, 'afloramento');
// Exportamos al drive
Export.image.toDrive({
    image: imgAfloramento,
    description: 'layer_afloramento_cluster',
    folder: 'raster_Aflor',
    crs: 'EPSG:4326',
    region: imgAfloramento.geometry(),
    fileFormat: 'GeoTIFF',
    scale: 30,
    maxPixels: 1e13,
    formatOptions: {
      cloudOptimized: true
    }
});
