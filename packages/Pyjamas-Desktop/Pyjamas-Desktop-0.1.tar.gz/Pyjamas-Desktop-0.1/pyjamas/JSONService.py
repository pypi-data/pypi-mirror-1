""" JSONService is a module providing JSON RPC Client side proxying.
"""

from HTTPRequest import HTTPRequest
import pygwt
from jsonrpc.json import dumps, loads, JSONDecodeException

# no stream support
class JSONService:
    def __init__(self, url, handler = None):
        """
        Create a JSON remote service object.  The url is the URL that will receive
        POST data with the JSON request.  See the JSON-RPC spec for more information.
        
        The handler object should implement onRemoteResponse(value, requestInfo) to 
        accept the return value of the remote method, and 
        onRemoteError(code, message, requestInfo) to handle errors.
        """
        self.url = url
        self.handler = handler
    
    def callMethod(self, method, params, handler = None):
        if handler == None:
            handler = self.handler
            
        if handler == None:
            return self._sendNotify(method, params)
        else:
            return self._sendRequest(method, params, handler)
    
    def onCompletion(self):
        pass

    def _sendNotify(self, method, params):
        msg = {"id":None, "method":method, "params":params}
        msg_data = dumps(msg)
        if not HTTPRequest().asyncPost(self.url, msg_data, self):
            return -1
        return 1

    def _sendRequest(self, method, params, handler):
        id = pygwt.getNextHashId()
        msg = {"id":id, "method":method, "params":params}
        msg_data = dumps(msg)
        
        request_info = JSONRequestInfo(id, method, handler)
        if not HTTPRequest().asyncPost(self.url, msg_data, JSONResponseTextHandler(request_info)):
            return -1
        return id


class JSONRequestInfo:
    def __init__(self, id, method, handler):
        self.id = id
        self.method = method
        self.handler = handler
    

class JSONResponseTextHandler:
    def __init__(self, request):
        self.request = request

    def onCompletion(self, json_str):

        try:
            response = loads(json_str)
        except JSONDecodeException:
            # err.... help?!!
            self.request.handler.onRemoteError(0, "decode failure", None)
            return

        if not response:
            self.request.handler.onRemoteError(0, "Server Error or Invalid Response", self.request)
        elif response.get("error"):
            error = response["error"]
            self.request.handler.onRemoteError(error["code"], error["message"], self.request)
        else:
            self.request.handler.onRemoteResponse(response["result"], self.request)
    
    def onError(self, error_str, error_code):
        self.request.handler.onRemoteError(error_code, error_str, self.request)

class ServiceProxy(object):
    def __init__(self, svc, serviceURL, serviceName=None):
        self.__serviceURL = serviceURL
        self.__serviceName = serviceName
        self.__svc = svc

    def _sendNotify(self, method, params):
        return self.__svc._sendNotify(method, params)

    def _sendRequest(self, method, params, handler):
        return self.__svc._sendRequest(method, params, handler)

    def __getattr__(self, name):
        if name == '__svc':
            return self.__svc
        if self.__serviceName != None:
            name = "%s.%s" % (self.__serviceName, name)
        return ServiceProxy(self.__svc, self.__serviceURL, name)

    def __call__(self, *params):
        if hasattr(params[-1], "onRemoteResponse"):
            handler = params[-1]
            return self._sendRequest(self.__serviceName,
                                            params[:-1], handler)
        else:
            return self._sendNotify(self.__serviceName, params)

# reserved names: callMethod, onCompletion
class JSONProxy(JSONService, ServiceProxy):
    def __init__(self, url, methods=None):
        url = "http://127.0.0.1/%s" % url # TODO: allow alternate locations
        JSONService.__init__(self, url)
        ServiceProxy.__init__(self, self, url)

