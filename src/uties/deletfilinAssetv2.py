import ee
import sys
import collections
collections.Callable = collections.abc.Callable
try:
    ee.Initialize()
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Gap-fill'
asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/SpatialV3'
# asset = "projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Classifier/ClassVP"
# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/FrequencyV2' #/filterFQnu_BACIA_776_V15
# asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/TemporalV3'
lsBacias = [
    # '741','7421','7422','744','745','746','7492','751','752','753',
    # '754','755','756','757','758','759','7621','7622', '763','764',
    # '765','766', '767','771','772','773', '7741','7742','775','776',
    # '777','778','76111','76116', '7614','7616','7618','7619','7613','7612',
    # '7422','744','7492','751','752','757','7622','763',
    # '765','766','767','772','773','7741','7742','776',
    # '778','7612','7613','7615','7617'
]



imgCol = ee.ImageCollection(asset).filter(
                ee.Filter.eq('version', 18)).filter(
                    ee.Filter.eq('filter', 'spatial_use'))#.filter(
                    # ee.Filter.inList('id_bacia', lsBacias))
lst_id = imgCol.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list').getInfo()

for cc, idss in enumerate(lst_id):    
    # id_bacia = idss.split("_")[2]
    path_ = str(asset + '/' + idss)    
    print ("... eliminando ❌ ... item 📍{} : {}  ▶️ ".format(cc, idss))
    
    try:
        # ee.data.deleteAsset(path_)
        print(path_)
    except:
        print(" NAO EXISTE!")
