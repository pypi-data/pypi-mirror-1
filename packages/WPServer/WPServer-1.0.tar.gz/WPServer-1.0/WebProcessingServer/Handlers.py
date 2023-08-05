import sys, cgi, time, os, traceback, ConfigParser
from WebProcessingServer.Exceptions import *

def modPythonHandler (apacheReq, service):
    """Mod Python handler reads data from an apache request
       and passes it into dispatchRequest."""
    from mod_python import apache, util
    try:
        
        if apacheReq.headers_in.has_key("X-Forwarded-Host"):
            host = "http://" + apacheReq.headers_in["X-Forwarded-Host"]
        else:
            host = "http://" + apacheReq.headers_in["Host"]
        host += apacheReq.uri
        
        input_content_type = "text/plain"
        output_content_type = "text/plain"
        if apacheReq.headers_in.has_key("Accept"):
            output_content_type = apacheReq.headers_in["Accept"]
        
        if apacheReq.headers_in.has_key("Content-Type"):
            input_content_type = apacheReq.headers_in["Content-Type"]
        
        post_data = apacheReq.read()
        request_method = apacheReq.method

        params = {}
        if request_method != "POST":
            fs = util.FieldStorage(apacheReq) 
            for key in fs.keys():
                params[key.lower()] = fs[key] 
       
        format, content = service.dispatchRequest( 
                                params, 
                                apacheReq.path_info,
                                host,
                                post_data, 
                                request_method,
                                input_content_type,
                                output_content_type
                                )
        apacheReq.content_type = format
        apacheReq.send_http_header()
        content = content.encode("utf-8")
        apacheReq.write(content)
    except WebProcessingServerException, E:
        apacheReq.content_type = "text/plain"
        apacheReq.status = apache.HTTP_INTERNAL_SERVER_ERROR
        apacheReq.send_http_header()
        apacheReq.write("An error occurred: %s\n" % (
            str(E) 
            ))
    except Exception, E:
        apacheReq.content_type = "text/plain"
        apacheReq.status = apache.HTTP_INTERNAL_SERVER_ERROR
        apacheReq.send_http_header()
        apacheReq.write("An error occurred: %s\n%s\n" % (
            str(E), 
            "".join(traceback.format_tb(sys.exc_traceback))))
    return apache.OK

def wsgiHandler (environ, start_response, service):
    """wsgiHandler reads data from a wsgi request. Uses paste.reques
       parse_formvars method."""
    try:
        from paste.request import parse_formvars
        request_method = hpath_info = host = post_data = ""
        fields = {}

        request_method = environ['REQUEST_METHOD']
        
        if request_method != "GET" and request_method != "DELETE":
            post_data = environ['wsgi.input'].read(int(environ['CONTENT_LENGTH']))
        fields = parse_formvars(environ)

        if "PATH_INFO" in environ: 
            path_info = environ["PATH_INFO"]

        if "HTTP_X_FORWARDED_HOST" in environ:
            host      = "http://" + environ["HTTP_X_FORWARDED_HOST"]
        elif "HTTP_HOST" in environ:
            host      = "http://" + environ["HTTP_HOST"]

        host += environ["SCRIPT_NAME"]

        input_content_type = "text/plain"
        output_content_type = "text/plain"
        
        if "HTTP_ACCEPT" in environ:
            output_content_type = environ['HTTP_ACCEPT']
        
        if "CONTENT_TYPE" in environ:
            input_content_type = environ['CONTENT_TYPE']

        format, content = service.dispatchRequest( fields, path_info, host, post_data, request_method, input_content_type, output_content_type )
        content = content.encode("utf-8")
        start_response("200 OK", [('Content-Type',format)])
        return [content]

    except WebProcessingServerException, E:
        start_response("500 Internal Server Error", [('Content-Type','text/plain')])
        return ["An error occurred: %s" % (
            str(E)) 
            ] 
    except Exception, E:
        start_response("500 Internal Server Error", [('Content-Type','text/plain')])
        return ["An error occurred: %s\n%s\n" % (
            str(E), 
            "".join(traceback.format_tb(sys.exc_traceback)))]

def cgiHandler (service = None):
    """cgiHandler used to create a CGI endpoint.""" 
    try:
        from WebProcessingServer import Server
        cfgfiles = Server.cfgfiles
        if not service:
            service = Server.Server.load(*cfgfiles)
        params = {}
        
        request_method = os.environ["REQUEST_METHOD"]
        
        input_content_type = "text/plain"
        output_content_type = "text/plain"
        
        if "HTTP_ACCEPT" in os.environ:
            output_content_type = os.environ['HTTP_ACCEPT']
        
        if "CONTENT_TYPE" in os.environ:
            input_content_type = os.environ['CONTENT_TYPE']

        post_data = None 
        if request_method != "GET" and request_method != "DELETE":
            post_data = sys.stdin.read()
            for key, value in cgi.parse_qsl(os.environ['QUERY_STRING']):
                params[key.lower()] = value

        else:
            input = cgi.FieldStorage()
            try:
                for key in input.keys(): params[key.lower()] = input[key].value
            except TypeError:
                pass

        path_info = host = ""

        if "PATH_INFO" in os.environ: 
            path_info = os.environ["PATH_INFO"]

        if "HTTP_X_FORWARDED_HOST" in os.environ:
            host      = "http://" + os.environ["HTTP_X_FORWARDED_HOST"]
        elif "HTTP_HOST" in os.environ:
            host      = "http://" + os.environ["HTTP_HOST"]

        host += os.environ["SCRIPT_NAME"]
        format, content = service.dispatchRequest( params, path_info, host, post_data, request_method, input_content_type, output_content_type )
        print "Content-type: %s\n" % format

        print content.encode("utf-8")
    except WebProcessingServerException, E:
        print "Cache-Control: max-age=10, must-revalidate" # make the client reload        
        print "Content-type: text/plain\n"
        print "An error occurred: %s\n" % E
    except Exception, E:
        print "Cache-Control: max-age=10, must-revalidate" # make the client reload        
        print "Content-type: text/plain\n"
        print "An error occurred: %s\n%s\n" % (
            str(E), 
            "".join(traceback.format_tb(sys.exc_traceback)))

theServer = None

def handler (apacheReq):
    global theServer
    from WebProcessingServer import Server
    cfgfiles = Server.cfgfiles
    options = apacheReq.get_options()
    cfgs    = cfgfiles
    if options.has_key("WebProcessingServerConfig"):
        cfgs = (options["WebProcessingServerConfig"],) + cfgs
    if not theServer:
        theServer = Server.Server.load(*cfgs)
    return modPythonHandler(apacheReq, theServer)

def wsgiApp (environ, start_response):
    global theServer
    from WebProcessingServer import Server
    cfgfiles = Server.cfgfiles
    cfgs    = cfgfiles
    if not theServer:
        theServer = Server.Server.load(*cfgs)
    return wsgiHandler(environ, start_response, theServer)

