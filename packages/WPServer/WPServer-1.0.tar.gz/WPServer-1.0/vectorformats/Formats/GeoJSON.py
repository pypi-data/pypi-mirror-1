from vectorformats.Feature import Feature
from vectorformats.Formats.Format import Format

ops = {}

try:
    import cjson as json_module
    ops['encode'] = 'encode'    
    ops['decode'] = 'decode'    
except:
    try:
        import simplejson as json_module
        ops['encode'] = 'dumps'    
        ops['decode'] = 'loads'    
    except Exception, E:
        raise Exception("simplejson is required for using the GeoJSON service. (Import failed: %s)" % E)

class GeoJSON(Format):
    def createFeature(self, feature_dict, id = None):
        feature = Feature(id)
        if feature_dict.has_key('geometry'):
            feature.geometry = feature_dict['geometry']
        if feature_dict.has_key('properties'):
            feature.properties = feature_dict['properties']
        return feature 
        
    
    def encode(self, features):
        results = []
        result_data = None
        for feature in features:
            data = self.encode_feature(feature)
            for key,value in data['properties'].items():
                if value and isinstance(value, str): 
                    data['properties'][key] = unicode(value,"utf-8")
            results.append(data)
        
        result_data = {
                       'type':'FeatureCollection',
                       'features': results,
                       'crs':
                        {
                            'type':'none',
                            'properties':
                                {
                                    'info':'No CRS information has been provided with this data.'
                                } 
                        } 
                      }
        
        result = getattr(json_module,ops['encode'])(result_data) 
        return result
    
    def encode_feature(self, feature):
        return {'type':"Feature", 
            "id": feature.id, 
            "geometry": feature.geometry, 
            "properties": feature.properties}

    def decode(self, data):    
        feature_data = getattr(json_module,ops['decode'])(data)
        if feature_data.has_key("features"):
            feature_data = feature_data['features']
        elif feature_data.has_key("members"):
            feature_data = feature_data['members']
        elif feature_data.has_key("type") and feature_data['type'] in ['Point', 'LineString', 'Polygon', 'MultiPolygon', 'MultiPoint', 'MultiLineString']:
            feature_data = [{'geometry':feature_data}] 
        else:
            feature_data = [feature_data]
        
        features = []
        for feature in feature_data:
            features.append(self.createFeature(feature))
        
        return features    
