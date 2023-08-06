#    Copyright 2008 Pedro Ferreira <ilzogoiby@gmail.com>
#
#    This file is part of pyOURSE.
#
#    pyOURSE is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    pyOURSE is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pyOURSE.  If not, see <http://www.gnu.org/licenses/>.


import re

from cgi import parse_qs

from wsgiref.simple_server import make_server
from rdflib import ConjunctiveGraph, Namespace
from rdflib.store.IOMemory import IOMemory

from __init__ import OURSE

class URIIndex:

    def __init__(self, graph):
        self.__index = {}
        
        res = graph.query("""PREFIX ourse: <file://ourse.owl#>
                             SELECT ?clsmap ?uri WHERE {
                             ?clsmap ourse:uriPattern ?uri.
                            } """)

    
        for (clsmap, uri) in res:
            self.add(clsmap, str(uri))


    def add(self, clsmap, uri):
        regexp =  re.sub(r'@@(.*?)@@',r'(?P<\1>([^\/.]*))', uri)
        regexp = "^" + regexp
        regexp += "\/?$"
        self.__index[regexp] = clsmap
        
    def get(self, uri):
        for (pattern, clsmap) in self.__index.iteritems():
            print uri, pattern
            res = re.match(pattern, uri)
            if res:
                return (clsmap, res.groupdict())
         
        raise Exception("No match for URI %s!" % uri)


class RDFHTTPProvider:
    def __init__(self, confGraph, ourseInstance, sparqlEP=None):

        self.__urlMap = [(r'^$', rootInfo)]

        self.__ourse = ourseInstance
        
        if sparqlEP:
            self.__urlMap.append((sparqlEP.getRegExp(),sparqlHandler(self.__ourse, sparqlEP)))
        
        print self.__urlMap

        self.__index = URIIndex(confGraph)


    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        accept = environ.get('HTTP_ACCEPT', '')

        print accept
        
        for regex, callback in self.__urlMap:
            match = re.search(regex, path)
            if match is not None:
                print regex, path, match.groupdict()
                bindings = match.groupdict()
                (contentType, data) = callback(bindings, environ)
                response_headers = [('Content-type',contentType)]
                
                start_response('200 OK', response_headers)
                return data

        (mapping, bindings) = self.__index.get(path)

        dataSourceMatch = self.__ourse.getGraphFromMapping(mapping, bindings)

        if dataSourceMatch:
            # TODO: Properly parse accept headers...
            if accept.find("n3") >= 0:
                start_response('200 OK', [('Content-type','application/rdf+n3')])
                return dataSourceMatch.serialize(format='n3')
            else:
                start_response('200 OK', [('Content-type','application/rdf+xml')])
                return dataSourceMatch.serialize(format='pretty-xml')
            
        start_response('404 NOT FOUND', [('Content-type','text/plain')])
        return "Not found..."

def rootInfo(bindings, environ):
    return ('text/plain','roots! bloody roots!')

def sparqlHandler(ourse, sparqlEndpoint):
    def __innerHandler(bindings, environ):
        return sparqlEndpoint.requestHandler(ourse, bindings, environ)
    return __innerHandler

class OURSEDataServer:

    def __init__(self, confGraph, host, port, storage=IOMemory(), sparqlEP=None):
        if port == 80:
            url = "http://%s/" % host
        else:
            url = "http://%s:%s/" % (host, port)

        ourseInstance = OURSE(confGraph, absoluteURL=url, storage=storage)
            
        application = RDFHTTPProvider(confGraph, ourseInstance, sparqlEP=sparqlEP)
        
        httpd = make_server(host, port, application)

        httpd.serve_forever()

