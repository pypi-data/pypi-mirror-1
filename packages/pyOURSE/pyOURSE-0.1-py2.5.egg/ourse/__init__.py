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
from rdflib import Namespace, RDF
from rdflib.Graph import Graph, ConjunctiveGraph
from rdflib.store.IOMemory import IOMemory

ns_ourse = Namespace('file://ourse.owl#')
ns_xsd = Namespace('http://www.w3.org/2001/XMLSchema#')

class OURSE:
    def __init__(self, configGraph, absoluteURL="/", storage = IOMemory()):
        self.__config = configGraph
        self.__databases = {}
        self.__classMappings = {}
        self.__absoluteURL = absoluteURL

        self.__storage = storage
        self.__graph = ConjunctiveGraph(store = storage)
        self.__objectGraphMap = {}
        
        self.setupSources()
        self.setupProvidedClassMappings()

    def setupSources(self):
        res = self.__config.query("""PREFIX ourse: <file://ourse.owl#>
                             SELECT ?db ?dsn ?driver ?username ?password WHERE {
                             ?db     ourse:DSN      ?dsn;
                                     ourse:Driver   ?driver.
                             OPTIONAL {
                                ?db    ourse:username ?username;
                                       ourse:password ?password.}}""")

        for (db, dsn, driver, username, password) in res:
            m = re.match(r"(?P<protocol>.+)://(?P<address>.+)",dsn)
            if m == None:
                raise Exception("DSN %s is not valid" % dsn)
            protocol = m.group('protocol')
            address = m.group('address')

            driverName = "%sDriver" % driver

            clazz = getattr(__import__("driver.%s" % driverName ,globals(),locals(),['']), driverName)
            self.__databases[db] = clazz(protocol, address.encode('latin-1'), username, password)


    def getSourceList(self):
        return self.__databases

    def setupProvidedClassMappings(self):
        from translation import ResourceClass
        for node in self.__config.subjects(RDF.type,ns_ourse['ClassMap']):
            self.__classMappings[node] = ResourceClass(node, self.__config)

    def getClassMappings(self):
        return self.__classMappings

    def getConjunctiveGraph(self):
        return self.__graph

    # "big graph"
    def getGraphFromMapping(self, mapping, bindings, expand=False):
    
        try:
            resourceClass = self.__classMappings[mapping]
        except KeyError:
            return None
        
        provider = resourceClass.getObjectProvider()                
        database = self.__databases[provider.getDBMapping()]

        database.startRequest()
        runner = provider.createRunner(database)        

        storage = self.__storage
        graph = self.__graph
        
        from storage import GraphFiller
        filler = GraphFiller(self, self.__objectGraphMap, graph, storage, database)

        obj = runner.execute(bindings)
        this = self.getObjectReference(resourceClass, obj, self.__absoluteURL)
        filler.loadObject(this, resourceClass, obj, expand=expand, uri=self.__absoluteURL)
        
        database.endRequest()
        return self.__objectGraphMap[this]

    def getObjectReference(self, resourceClass, object, baseURI):
        return resourceClass.getURIForObject(object, baseURI)
        


        
