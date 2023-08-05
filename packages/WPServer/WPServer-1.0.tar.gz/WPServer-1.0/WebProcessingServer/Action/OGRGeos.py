from WebProcessingServer.Action import Action, Feature 

import_failed = None

try:
    from ogrhelpers import *
    try:
        import osgeo.ogr as ogr
    except ImportError:
        import ogr
except ImportError, E:
    import_failed = E

class OGRGeos(Action):
    def action(self, request):
        if import_failed:
            raise Exception("The OGR library is required for the dissolve service. (%s)" % import_failed)

class StandaloneGeosAction(OGRGeos):
    def action(self, request):
        OGRGeos.action(self, request)
        for feature in request.features:
            geom = feature['geometry']
            ogrgeom = CreateGeometryFromJson(geom)
            newgeom = getattr(ogrgeom, self.action_name)()
            feature['properties']['created_by'] = self.action_name
            feature['geometry'] = ExportToJson(newgeom)
        return request 

class CollectedGeosAction(OGRGeos):
    def action(self, request):
        OGRGeos.action(self, request)
        if len(request.features) == 0:
            return request
        ogrgeom = CreateGeometryFromJson(request.features[0]['geometry'])
        for feature in request.features[1:]:
            diffgeom = CreateGeometryFromJson(feature['geometry'])
            ogrgeom = getattr(ogrgeom, self.action_name)(diffgeom)
        
        request.features = [
            Feature(0, 
                ExportToJson(ogrgeom), 
                {'created_by':self.action_name}
            )
        ]    
        return request    

class ConvexHull(StandaloneGeosAction):
    action_name = "ConvexHull"

class Centroid(StandaloneGeosAction):
    action_name = "Centroid"


class SymmetricDifference(CollectedGeosAction):
    action_name = "SymmetricDifference"

class Difference(CollectedGeosAction):
    action_name = "Difference"
    
class Intersection(CollectedGeosAction):
    action_name = "Intersection"

class Union(CollectedGeosAction):
    action_name = "Union"

class Dissolve(OGRGeos):
    def action(self, request, key=None):
        OGRGeos.action(self, request)
        
        geomcol = ogr.Geometry(type=ogr.wkbGeometryCollection)
        
        for feature in request.features:
            if feature['geometry']['type'] != "Polygon":
                raise Exception("You can only dissolve Polygons. (%s)" % feature['geometry'])
            geom = CreateGeometryFromJson(feature['geometry'])
            geomcol.AddGeometry(geom)
        gb = geomcol.Buffer(0)
        features = []
        if gb.GetGeometryType() == ogr.wkbGeometryCollection or \
           gb.GetGeometryType() == ogr.wkbMultiPolygon:
            for i in range(gb.GetGeometryCount()):
                features.append(
                    Feature(0, ExportToJson(gb.GetGeometryRef(i)),
                        {'created_by':'dissolve'})
            )
        else:
           features.append(
                Feature(0, 
                    ExportToJson(gb), 
                    {'created_by':'dissolve'}
                )
           )
        
        request.features = features
        return request 
                
class Buffer(OGRGeos):
    def action(self, request, buffer=2):
        OGRGeos.action(self, request)
        for feature in request.features:
            geom = feature['geometry']
            ogrgeom = CreateGeometryFromJson(geom)
            newgeom = ogrgeom.Buffer(float(buffer))
            feature['properties']['created_by'] = "Buffer (%s)" % buffer
            feature['geometry'] = ExportToJson(newgeom)
        return request 
        
