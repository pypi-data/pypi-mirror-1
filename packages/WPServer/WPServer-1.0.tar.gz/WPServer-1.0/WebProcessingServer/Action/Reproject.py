import_failed = False
try:
    from ogrhelpers import *
    try:
        import osgeo.osr as osr
    except:
        import osr
except ImportError, E:
    import_failed = E

from WebProcessingServer.Action import Action

class Reproject(Action):
    def action(self, request, input="EPSG:4326", output="EPSG:4326"):
        if import_failed:
            raise Exception("The OGR and OSR libraries are required for the reprojection service. (%s)" % import_failed)
        inref = osr.SpatialReference()
        inref.SetFromUserInput(input)
        outref = osr.SpatialReference()
        outref.SetFromUserInput(output)
        transform = osr.CoordinateTransformation(inref, outref)
        for feature in request.features:
            geom = feature['geometry']
            ogrgeom = CreateGeometryFromJson(geom)
            ogrgeom.AssignSpatialReference(inref)
            ogrgeom.Transform(transform)
            feature['geometry'] = ExportToJson(ogrgeom)
        return request 
