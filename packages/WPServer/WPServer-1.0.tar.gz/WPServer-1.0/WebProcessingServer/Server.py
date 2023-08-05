#!/usr/bin/python
# Licensed under the terms included in this distribution as LICENSE.txt.
# Copyright (c) 2006-2007 MetaCarta, Inc.

import sys, cgi, time, os, traceback, ConfigParser

from WebProcessingServer.Handlers import *
import WebProcessingServer.Service

# Windows doesn't always do the 'working directory' check correctly.
if sys.platform == 'win32':
    workingdir = os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(sys.argv[0])))
    cfgfiles = (os.path.join(workingdir, "webprocessingserver.cfg"), os.path.join(workingdir,"..","webprocessingserver.cfg"))
else:
    cfgfiles = ("webprocessingserver.cfg", os.path.join("..", "webprocessingserver.cfg"), "/etc/webprocessingserver.cfg")

class Server (object):
    """The server manages the datasource list, and does the management of
       request input/output.  Handlers convert their specific internal
       representation to the parameters that dispatchRequest is expecting,
       then pass off to dispatchRequest. dispatchRequest turns the input 
       parameters into a (content-type, response string) tuple, which the
       servers can then return to clients. It is possible to integrate
       WebProcessingServer into another content-serving framework like Django
       by simply creating your own actions (passed to the init function)
       and calling the dispatchRequest method. The Server provides a
       classmethod to load actions from a config file, which is the typical
       lightweight configuration method, but does use some amount of time at
       script startup.
       """ 
       
    def __init__ (self, actions, metadata = {}):
        self.actions   = actions
        self.metadata      = metadata
    
    def _loadFromSection (cls, config, section, module_type, **objargs):
        type  = config.get(section, "class")
        function  = config.get(section, "function")
        module = __import__("%s.%s" % (module_type, type), globals(), locals(), type)
        action = getattr(module, function)
        for opt in config.options(section):
            if opt not in  ["class", "function"]:
                objargs[opt] = config.get(section, opt)
        return action(**objargs)

    loadFromSection = classmethod(_loadFromSection)

    def _load (cls, *files):
        """Class method on Service class to load actions
           and metadata from a configuration file."""
        config = ConfigParser.ConfigParser()
        config.read(files)
        
        metadata = {}
        if config.has_section("metadata"):
            for key in config.options("metadata"):
                metadata[key] = config.get("metadata", key)

        actions = {}
        for section in config.sections():
            if section == "metadata": continue
            actions[section] = cls.loadFromSection(
                                    config, section, 'Action')

        return cls(actions, metadata)
    load = classmethod(_load)


    def dispatchRequest (self, params, path_info, host, post_data = None, request_method = "GET", input_content_type = "text/plain", output_content_type = "text/plain"):
        """Read in request data, and return a (content-type, response string) tuple. May
           raise an exception, which should be returned as a 500 error to the user."""  
        
        if len(output_content_type.split(",")) > 1:
            output_content_type = "text/plain"
        request = None
        
        service = "REST" 
        
        request = getattr(WebProcessingServer.Service, service)(self)
            
        parsed_response = request.parse(params, path_info, host, post_data, request_method, input_content_type)
        
        if not parsed_response.action:
            raise Exception("Couldn't determine which action you meant.")
        response = self.actions[parsed_response.action].action(parsed_response, **parsed_response.parameters)
        
        return request.encode(response, output_content_type)

if __name__ == '__main__':
    cgiHandler()
