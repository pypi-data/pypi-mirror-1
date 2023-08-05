from vectorformats.Feature import Feature
from vectorformats.Formats.Format import Format

import re

class WKT(Format):
    wkt_linestring_match = re.compile(r'\(([^()]+)\)')

    def from_wkt (self, geom):
        coords = []
        for line in self.wkt_linestring_match.findall(geom):
            ring = []
            for pair in line.split(","):
                ring.append(map(float, pair.split(" ")))
            coords.append(ring)
        if geom.startswith("POINT"):
            geomtype = "Point"
            coords = coords[0][0]
        elif geom.startswith("LINESTRING"):
            geomtype = "LineString"
            coords = coords[0]
        elif geom.startswith("POLYGON"):
            geomtype = "Polygon"
        else:
            geomtype = geom[:geom.index["("]]
            raise Error("Unsupported geometry type %s" % geomtype)
        return {"type": geomtype, "coordinates": coords}
        
    
    def decode(self, data):    
        features = [
           Feature(1, self.from_wkt(data))
        ]
        
        return features    
