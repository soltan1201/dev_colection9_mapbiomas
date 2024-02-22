
var param = {
    'asset_ROIs_manual': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/ROIs/coletaROIsv7N2manual'},
    'asset_ROIs_cluster': {"id" : 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/ROIs/coletaROIsv6N2cluster'}
}
var showAssetall = false;
var showpropAll = true;

var getROIsFeatures = function(dictAsset){
    var getlistPtos = ee.data.getList(dictAsset);
    var featGeralPoints = ee.FeatureCollection([]);
    getlistPtos.forEach(function(assetFeat){
        if (showAssetall === true){
            print(" loading  ", assetFeat);
        }
        var tmpFeat = ee.FeatureCollection(assetFeat.id);
        featGeralPoints = featGeralPoints.merge(tmpFeat);
    })
    
    return featGeralPoints;
}

var featPointsCC = getROIsFeatures(param['asset_ROIs_cluster']);
print("show the first features permanentes", featPointsCC.limit(4));
var lstProp = featPointsCC.first().propertyNames() 
print('size features ', featPointsCC.size());
print("size list properties ", ee.List(lstProp).size());
if (showpropAll){
    print(" show all properties  ", lstProp);
}

var featPointsM = getROIsFeatures(param['asset_ROIs_manual']);
print("show the first features Manuais", featPointsM.limit(4));
print('size features ', featPointsM.size());