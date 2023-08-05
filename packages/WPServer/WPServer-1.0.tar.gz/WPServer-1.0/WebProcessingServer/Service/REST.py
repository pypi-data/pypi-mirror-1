from WebProcessingServer.Service import Request, Service
from WebProcessingServer.Exceptions import *

import urllib, urlparse

supported = {} 

supported_order = ['GeoRSS','KML','HTML','WKT','GeoJSON'] 

try:
    from vectorformats.Formats.GeoRSS import GeoRSS
    supported['GeoRSS'] = {
      'class': GeoRSS,
      'encode': True,
      'decode': True,
      'content_types': ['georss', 'atom', 'application/atom+xml','application/rss+xml','text/xml'],
      'output_content_type': 'application/atom+xml'
    }
except:
    pass

try:
    from vectorformats.Formats.KML import KML
    supported['KML'] = {
        'class': KML,
        'encode': True,
        'decode': True,
        'content_types': ['kml', 'application/vnd.google-earth.kml+xml'],
        'output_content_type': 'application/vnd.google-earth.kml+xml'
    }
except:
    pass

try:
    from vectorformats.Formats.HTML import HTML 
    supported['HTML'] = {
        'class': HTML,
        'encode': True,
        'decode': False,
        'content_types': ['html', 'text/html'],
        'output_content_type': 'text/html'
    }
except:
    pass

try:
    from vectorformats.Formats.WKT import WKT
    supported['WKT'] = {
      'class': WKT,
      'encode': True,
      'decode': True,
      'content_types': ['wkt', 'text/x-wkt'],
      'output_content_type':'text/plain'
    }
except:
    pass

try:
    from vectorformats.Formats.GeoJSON import GeoJSON
    supported['GeoJSON'] = {
      'class': GeoJSON,
      'encode': True,
      'decode': True,
      'content_types': ['geojson', 'text/plain', 'application/json'],
      'output_content_type':'text/plain'
    }
except:
    pass


class REST(Service):
    def parse(self, params = {}, path_info = "/", host = "", post_data = "", request_method = "GET", content_type = None):
        self.content_type = None
        r = Service.parse(self, params, path_info, host, post_data, request_method, content_type)
        data = ""
        if request_method == "GET":
            if params.has_key("data"):
                data = params['data']
            elif params.has_key("url"):
                url = params['url']
                urlparts = urlparse.urlparse(url)
                if self.server.metadata.has_key('allowed_hosts'):
                    hosts = self.server.metadata['allowed_hosts'].split(",")
                    if urlparts[1] not in hosts:
                        raise RemoteHostError(url, hosts)
                u = urllib.urlopen(params['url'])
                data = u.read()
                content_type = u.headers.get("Content-Type")
            r.features = self.extract_features(data, content_type)
        return r    
    
    def extract_parameters(self, params, data = ""):
        output = {}
        for key,value in params.items():
            if key not in ['data', 'url', 'inputformat', 'outputformat']:
                output[key] = value
        return output        

    def extract_features(self, data, content_type = None):
        if not data: return []
        features = []
        parse_exceptions = []
        for format_name in supported_order:
            try:
                if content_type in supported[format_name]['content_types'] and \
                    supported[format_name]['decode']:
                    format = supported[format_name]['class']()
                    features = format.decode(data)
            except Exception, E:
                parse_exceptions.append((format_name, E))
        
        # Fallback - loop through everything.
        if not features:
            for format_name in supported_order:
                try:
                    if not supported[format_name]['decode']: continue 
                    format = supported[format_name]['class']()
                    features = format.decode(data)
                except Exception, E:
                    parse_exceptions.append((format_name, E))
        
        if not features and parse_exceptions:
            message = ["Unable to parse. Formats returned the following messages:"]
            for format, exception in parse_exceptions:
                message.append("%s: %s" % (format, str(exception)))
            raise ParseError("\n".join(message))

        return features            
    
    def encode(self, response, content_type = None):
        output = format = None
        if self.output_content_type:
            content_type = self.output_content_type
        try:
            for format_name in supported:
                if content_type in supported[format_name]['content_types'] and \
                    supported[format_name]['encode']:
                    format = supported[format_name]['class']()
                    output = format.encode(response.features)
                    content_type = supported[format_name]['output_content_type']
        except Exception, E:
            raise ExportError("Failed to export using %s. (%s) \n%s" % (format_name, E, response))
        
        return (content_type, output)
        
