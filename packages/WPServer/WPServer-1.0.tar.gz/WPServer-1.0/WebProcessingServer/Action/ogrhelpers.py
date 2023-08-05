try:
    import osgeo.ogr as ogr
except ImportError:
    import ogr

try:
    ogr.UseExceptions()
except AttributeError:
    pass

# From hobu's OGR stuff.
def CreateGeometryFromJson(input):
    try:
        input['type']
    except TypeError:
        try:
            import simplejson
        except ImportError:
            raise ImportError, "You must have 'simplejson' installed to be able to use this functionality"
        input = simplejson.loads(input)

    types = { 'Point': ogr.wkbPoint,
              'LineString': ogr.wkbLineString,
              'Polygon': ogr.wkbPolygon,
              'MultiPoint': ogr.wkbMultiPoint,
              'MultiLineString': ogr.wkbMultiLineString,
              'MultiPolygon': ogr.wkbMultiPolygon,
              'GeometryCollection': ogr.wkbGeometryCollection
    }
   
    type = input['type']
    gtype = types[type]

    geometry = ogr.Geometry(type=gtype)
    coordinates = input['coordinates']
   
    if type == 'Point':
        geometry.AddPoint_2D(coordinates[0], coordinates[1])
    
    elif type == 'MultiPoint':
        for point in coordinates:
            gring = ogr.Geometry(type=ogr.wkbPoint)
            gring.AddPoint_2D(point[0], point[1])
            geometry.AddGeometry(gring)
   
    elif type == 'LineString':
        for coordinate in coordinates:
            geometry.AddPoint_2D(coordinate[0], coordinate[1])
    
    elif type == 'MultiLineString':
        for ring in coordinates:
            gring = ogr.Geometry(type=ogr.wkbLineString)
            for coordinate in ring:
                gring.AddPoint_2D(coordinate[0], coordinate[1])
            geometry.AddGeometry(gring)

    
    elif type == 'Polygon':
        for ring in coordinates:
            gring = ogr.Geometry(type=ogr.wkbLinearRing)
            for coordinate in ring:
                gring.AddPoint_2D(coordinate[0], coordinate[1])
            geometry.AddGeometry(gring)
    
    elif type == 'MultiPolygon':
        for poly in coordinates:
            gpoly = ogr.Geometry(type=ogr.wkbPolygon)
            for ring in poly:
                gring = ogr.Geometry(type=ogr.wkbLinearRing)
                for coordinate in ring:
                    gring.AddPoint_2D(coordinate[0], coordinate[1])
                gpoly.AddGeometry(gring)
            geometry.AddGeometry(gpoly)
    
    return geometry

def ExportToJson(geometry):
    def get_coordinates(geometry):
        gtype = geometry.GetGeometryType()
        geom_count = geometry.GetGeometryCount()
        coordinates = []

        if gtype == ogr.wkbPoint: 
            return [geometry.GetX(0), geometry.GetY(0)]
        
        if gtype == ogr.wkbPoint25D:
            return [geometry.GetX(0), geometry.GetY(0), geometry.GetZ(0)]
            
        if gtype == ogr.wkbMultiPoint or gtype == ogr.wkbMultiPoint25D:
            geom_count = geometry.GetGeometryCount()
            for g in range(geom_count):
                geom = geometry.GetGeometryRef(g)
                coordinates.append(get_coordinates(geom))
            return coordinates

        if gtype == ogr.wkbLineString or gtype == ogr.wkbLineString25D:
            points = []
            point_count = geometry.GetPointCount()
            for i in range(point_count):
                points.append([geometry.GetX(i), geometry.GetY(i)])
            return points

        if gtype == ogr.wkbMultiLineString or gtype == ogr.wkbMultiLineString25D:
            coordinates = []
            geom_count = geometry.GetGeometryCount()
            for g in range(geom_count):
                geom = geometry.GetGeometryRef(g)        
                coordinates.append(get_coordinates(geom))
            return coordinates

        if gtype == ogr.wkbPolygon or gtype == ogr.wkbPolygon25D:
            coordinates = []
            geom_count = geometry.GetGeometryCount()
            for g in range(geom_count):
                geom = geometry.GetGeometryRef(g)
                coordinates.append(get_coordinates(geom))
            return coordinates

        if gtype == ogr.wkbMultiPolygon or gtype == ogr.wkbMultiPolygon25D:

            coordinates = []
            geom_count = geometry.GetGeometryCount()
            for g in range(geom_count):
                geom = geometry.GetGeometryRef(g)
                coordinates.append(get_coordinates(geom))
            return coordinates
            
    types = { ogr.wkbPoint:'Point',
              ogr.wkbLineString: 'LineString',
              ogr.wkbPolygon: 'Polygon',
              ogr.wkbMultiPoint: 'MultiPoint',
              ogr.wkbMultiLineString: 'MultiLineString',
              ogr.wkbMultiPolygon: 'MultiPolygon',
              ogr.wkbGeometryCollection: 'GeometryCollection',
              ogr.wkbPoint25D: "Point",  
              ogr.wkbLineString25D: "LineString",  
              ogr.wkbPolygon25D: "Polygon",  
              ogr.wkbMultiPoint25D: "MultiPoint",  
              ogr.wkbMultiLineString25D: "MultiLineString",  
              ogr.wkbMultiPolygon25D: "MultiPolygon"  
    }

    if geometry.GetGeometryType() == ogr.wkbGeometryCollection or \
       geometry.GetGeometryType() == ogr.wkbGeometryCollection25D:
        geometries = []    
        geom_count = geometry.GetGeometryCount()
        for g in range(geom_count):
            geom = geometry.GetGeometryRef(g)
            geometries.append(ExportToJson(geom))
        output = {'type': types[geometry.GetGeometryType()],
                  'geometries': geometries}
    else:
        output = {'type': types[geometry.GetGeometryType()],
                  'coordinates': get_coordinates(geometry)}
    return output
