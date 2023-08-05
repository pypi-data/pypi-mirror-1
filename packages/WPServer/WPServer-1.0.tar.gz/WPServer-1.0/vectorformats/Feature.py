class Feature (object):
    def __init__ (self, id = None, geometry = None, props = None):
        self.id         = id
        self.geometry   = geometry or {}
        self.properties = props or {}
        self.bbox       = None

    def __getitem__(self, key):
        if key == "geometry":
            return self.geometry
        elif key == "properties":
            return self.properties
        elif key == "id":
            return self.id
        raise KeyError(key)    
    
    def __setitem__(self, key, value):
        if key == "geometry":
            self.geometry = value
        elif key == "properties":
            self.properties = value
        elif key == "id":
            self.id = value
        else:
            raise KeyError(key)
        return     
    
    def get_bbox (self):
        minx = miny = 2**31
        maxx = maxy = -2**31
        try:
            
            coords = self.geometry["coordinates"]
            
            if self.geometry["type"] == "Point":
                minx = coord[0]
                maxx = coord[0]
                miny = coord[1]
                maxy = coord[1]
            
            elif self.geometry["type"] == "LineString":
                for coord in coords:
                    if coord[0] < minx: minx = coord[0]
                    if coord[0] > maxx: maxx = coord[0]
                    if coord[1] < miny: miny = coord[1]
                    if coord[1] > maxy: maxy = coord[1]
            
            elif self.geometry["type"] == "Polygon":
                for ring in coords:
                    for coord in ring:
                        if coord[0] < minx: minx = coord[0]
                        if coord[0] > maxx: maxx = coord[0]
                        if coord[1] < miny: miny = coord[1]
                        if coord[1] > maxy: maxy = coord[1]
            
            return (minx, miny, maxx, maxy)
        
        except:
            raise Exception("Unable to determine bounding box for feature with geometry %s" % self.geometry)

    def to_dict (self):
        return {"id": self.id,
                "geometry": self.geometry,
                "properties": self.properties}
