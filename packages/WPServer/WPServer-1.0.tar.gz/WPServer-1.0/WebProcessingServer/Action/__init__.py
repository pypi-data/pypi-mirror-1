from vectorformats.Feature import Feature

class Action(object):
    title = "No title"
    description = "No description"
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)
    
    def action(self, request, **kwargs):
        raise NotImplementedError("No action defined.")     
    
    def title(self):
        "Return title of service."
        return self.title 
    
    def description(self):
        """Return description of the service."""
        return self.description 
    
    def args(self):
        """Metadata about arguments. Should return list of key, type pairs."""
        return []
