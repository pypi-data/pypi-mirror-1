class Request(object):
    action = None
    features = None
    parameters = None
    
    def __init__(self, **kwargs):
        pass

class Service(object):
    server = None

    output_content_type = None

    def __init__(self, server):
        self.server = server
    
    def parse(self, params = {}, path_info = "/", host = "", post_data = "", request_method = "GET", content_type = None):
        if params.has_key("inputformat"):
            content_type = params['inputformat']
        
        if params.has_key("outputformat"):
            self.output_content_type = params['outputformat'] 
        
        r = Request()
        r.action = self.get_action(path_info, params, post_data)
        r.parameters = self.extract_parameters(params, post_data)
        r.features = self.extract_features(post_data, content_type)
        return r
    
    def extract_parameters(self, params = {}, data = ""):
        return {} 
    
    def extract_features(self, string, content_type = None):
        return [] 
    
    def get_action(self, path_info, params = {}, data = ""):        
        """Return action based on path"""        
        path = path_info.split("/")        
        if len(path) > 1:            
            parts = path[1].split(".")
            if len(parts) > 1:
                self.output_content_type = parts[-1]
            return parts[0]  
        return None    
            
    def encode(self, data, content_type = None):
        return ("text/plain", data)

from WebProcessingServer.Service.REST import REST        
