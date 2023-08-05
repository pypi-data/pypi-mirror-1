class WebProcessingServerException(Exception):
    pass
class ParseError(WebProcessingServerException):
    pass
class ExportError(WebProcessingServerException):
    pass
class RemoteHostError(WebProcessingServerException):
    def __init__ (self, url, hosts):
        self.url = url
        self.hosts = hosts
    def __str__ (self):
        message = ["You can't load data from %s." % self.url,
                   "Allowed hosts are: \n * %s" % "\n * ".join(self.hosts)  ] 
        return "\n".join(message)           
