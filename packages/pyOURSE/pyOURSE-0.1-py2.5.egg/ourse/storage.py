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


from rdflib import BNode, RDF, URIRef, Literal
from rdflib.Graph import Graph
from translation import ResourceClass, LiteralClassProperty, ResourceClassProperty


class GraphFiller:
    def __init__(self, ourse, objGraphMap, graph, storage, database):
        self.__graph = graph
        self.__storage = storage
        self.__objectGraphMap = objGraphMap
        self.__ourse = ourse
        self.__database = database

    def loadObject(self, this, resourceClass, object, expand=True, uri="/"):
        existing = self.__objectGraphMap.get(this, None)

        if existing:
            return this

        graph = Graph(store = self.__storage, identifier = this)
        self.__objectGraphMap[this] = graph
        graph.add((this, RDF.type, resourceClass.getTargetClass()))

        for propMap,prop in resourceClass.getPropertyMappings().iteritems():            
            if prop.__class__ == LiteralClassProperty:
                value = prop.getValue(object)

                # handle cardinality
                # default: process as different triples
                # TODO: handle different types of cardinality (collections, etc...)
                
                if not self.__database.isList(value):
                    value = [value]

                for v in value:
                    if (type(v) != URIRef):
                    # convert to literal only if it's not a URIRef
                        v = Literal(v)
                    graph.add((this, prop.getPredicate(), v))
                    
            elif prop.__class__ == ResourceClassProperty:
                propObjectList = prop.getResourceObject(object)

                # old cardinality story...
                 
                if not self.__database.isList(propObjectList):
                    propObjectList = [propObjectList]

                for propObject in propObjectList:
                    
                    try:
                        classMapping = self.__ourse.getClassMappings()[prop.getTargetClass()]
                    except KeyError:
                        raise Exception("No mapping for target class '%s' was found" % prop.getTargetClass())

                    resource = self.__ourse.getObjectReference(classMapping, propObject, uri)

                    # if we want the graph to be complete, or it's a BNode
                    if expand or resource.__class__ == BNode:
                        resource = self.loadObject(resource, classMapping, propObject, expand=True, uri = uri)
                                        
                    graph.add((this, prop.getPredicate(), resource))
        return this




