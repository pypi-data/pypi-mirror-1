"""
  Copyright (c) 2007 Jan-Klaas Kollhof
  Copyright (c) 2008 Luke Kenneth Casson Leighton

  This file is part of jsonrpc.

  jsonrpc is free software; you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License as published by
  the Free Software Foundation; either version 2.1 of the License, or
  (at your option) any later version.

  This software is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with this software; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import urllib
from jsonrpc.json import dumps, loads, JSONDecodeException

class JSONRequestInfo:
    def __init__(self, id, method, handler):
        self.id = id
        self.method = method
        self.handler = handler

class JSONRPCException(Exception):
    def __init__(self, rpcError):
        Exception.__init__(self)
        self.error = rpcError
        
class ServiceProxy(object):
    def __init__(self, serviceURL, serviceName=None):
        self.__serviceURL = serviceURL
        self.__serviceName = serviceName

    def __getattr__(self, name):
        if self.__serviceName != None:
            name = "%s.%s" % (self.__serviceName, name)
        return ServiceProxy(self.__serviceURL, name)

    def __call__(self, *args):
        postdata = dumps({"method": self.__serviceName, 'params': args[:-1], 'id':'jsonrpc'})
        # TODO: make this asynchronous - because we can.
        respdata = urllib.urlopen(self.__serviceURL, postdata).read()
        try:
            resp = loads(respdata)
        except JSONDecodeException:
            # err.... help?!!
            args[-1].onRemoteError(0, "decode failure", None)
            return -1

        resp_info = JSONRequestInfo(resp['id'],
                                  self.__serviceName, args[-1])
        print "resp", resp
        if not resp:
            args[-1].onRemoteError(0, "decode failure", None)
            return -1
        if not resp.has_key('error') or resp['error'] == None:
            args[-1].onRemoteResponse(resp['result'], resp_info)
            return resp['id']
        else:
            args[-1].onRemoteError(resp.get('code'), resp['error'], resp_info)
            return -1
         


class JSONProxy(ServiceProxy):
    def __init__(self, location, fns):
        # XXX fake for now to 127.0.0.1
        ServiceProxy.__init__(self, "http://127.0.0.1/%s" % location)
    
class EchoServicePython(JSONProxy):
    def __init__(self):
            JSONProxy.__init__(self, "/cgi-bin/EchoService.py", ["echo", "reverse", "uppercase", "lowercase"])

if __name__ == '__main__':

    class test:
        def __init__(self):
            self.s = EchoServicePython()
            self.s.echo('hello', self)
            self.s.reverse('reverse', self)
            self.s.sodyou('reverse', self)

        def onRemoteError(self, code, message, resp_info):
            print code, message, resp_info

        def onRemoteResponse(self, response, resp_info):
            if resp_info.method == 'echo':
                print "echo", response
            if resp_info.method == 'echo':
                print "reverse", response

    test()
