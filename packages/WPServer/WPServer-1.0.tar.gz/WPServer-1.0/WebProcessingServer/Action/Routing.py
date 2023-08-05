import re
import_failed = False
try:
    import psycopg2
except ImportError, E:
    try:
        import psycopg as psycopg2
    except ImportError, E2:    
        import_failed = (E, E2)
   
from WebProcessingServer.Action import Action, Feature

# This class is essentially a port of the PHP code made available by Orkney
# as part of the pgRouting + OpenLayers workshop.
class PGRouting(Action):
    def action(self, request, method="SPD"): 
        if import_failed:
            raise Exception("Couldn't load neccesary postgres module. (%s)" % E)
        edges = []
        if len(request.features) < 2:
            raise Exception("Routing requires at least two points.") 
        for point in request.features:
            geom = point['geometry']
            if geom['type'] != "Point":
                raise Exception("Point to Point routing only.")
            edge = self.find_nearest_edge(
                geom['coordinates'][0], 
                geom['coordinates'][1])
            if edge:
                edges.append(edge)
            else:
                raise Exception("Couldn't find an edge close to %s." % point)
        
        sql = """SELECT AsText(GeometryN(rt.the_geom,1)) AS wkt, 
                     length(rt.the_geom) AS length, %s.gid 
                  FROM %s, 
                      (SELECT gid, the_geom 
                          FROM dijkstra_sp_delta(
                              '%s',
                              %s,
                              %s,
                              3000)
                       ) as rt 
                  WHERE %s.gid=rt.gid""" % (self.table, self.table, 
                                            self.table, edges[0]['source'], edges[1]['target'],
                                            self.table)
        con = psycopg2.connect(self.dsn)
        cur = con.cursor()
        cur.execute(sql)
        features = cur.fetchall()
        con.close()
        return_features = []
        length = 0
        for feature in features:
            length += feature[1]
            return_features.append(Feature(feature[2],self.from_wkt(feature[0]),{'length': length}))
        
        request.features = return_features
        return request        
    
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
            coords = coords[0]
        elif geom.startswith("LINESTRING"):
            geomtype = "LineString"
            coords = coords[0]
        elif geom.startswith("POLYGON"):
            geomtype = "Polygon"
        else:
            geomtype = geom[:geom.index["("]]
            raise Error("Unsupported geometry type %s" % geomtype)
        return {"type": geomtype, "coordinates": coords}


    def find_nearest_edge(self, x, y):    
        sql = """SELECT gid, source, target, the_geom,  
    			 distance(the_geom, GeometryFromText(
                      'POINT(%s %s)', -1)) AS dist 
                FROM  %s 
                WHERE the_geom && setsrid(
                      'BOX3D(%s %s, %s %s))'::box3d, -1) 
                ORDER BY dist LIMIT 1""" % (x, y, self.table, x-2000, 
                                            y-2000,  x+2000,  y+2000)
        con = psycopg2.connect(self.dsn)
        cur = con.cursor()
        cur.execute(sql)
        data = cur.fetchone()
        con.close() 
        
        edge = None 
        if data:
            edge = {
              'gid': data[0],
              'source': data[1],
              'target': data[2]
            }
        
        return edge 
