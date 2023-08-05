import_failed = False
try:
    from shapely import geometry 
except ImportError, E:
    import_failed = E


from WebProcessingServer.Action import Action

class Buffer(Action):
    def action(self, request, buffer = 2):
        if import_failed:
            raise Exception("Unabled to run shapely operations without shapely module (%s)" % import_failed)  
        for feature in request.features:
            shape = geometry.asShape(feature['geometry'])
            shape = shape.buffer(buffer)
            feature['geometry'] = shape.__geo_interface__
        return request    
