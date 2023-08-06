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


from database import ObjectProvider, Getter
from rdflib import Literal, URIRef, RDF, BNode
from urlparse import urljoin

from __init__ import ns_ourse
from __init__ import ns_xsd

class ResourceClass:
    def __init__(self,  classMap, confGraph):

        res = confGraph.query("""PREFIX ourse: <file://ourse.owl#>
                                    SELECT ?uri ?prov ?targetCls WHERE {
                                           ?clsmap ourse:class         ?targetCls;
                                                   ourse:uriPattern    ?uri.
                                    OPTIONAL {
                                           ?clsmap  ourse:objectProvider ?prov.
                                             }.
                                  } """, initBindings = {"?clsmap" : classMap})
        
        for (uri, prov, targetCls) in res:
            self.__uriPattern = uri
            if prov:
                self.__objectProvider = ObjectProvider.create(confGraph, prov)
            self.__targetCls = targetCls

        self.__bindings = {}
        res2 = confGraph.query("""PREFIX ourse: <file://ourse.owl#>
                                    SELECT ?getter ?parameter WHERE {
                                           ?clsmap ourse:bind        ?binding.
                                           ?binding ourse:getter     ?getter;
                                                    ourse:parameter  ?parameter;
                                  } """, initBindings = {"?clsmap" : classMap})

        for (getter, parameter) in res2:
            self.__bindings[str(parameter)] = Getter.create(confGraph, getter)


        self.__mappings = {}
        res3 = confGraph.query("""PREFIX ourse: <file://ourse.owl#>
                                     SELECT ?propMap ?prop WHERE {
                                            ?clsmap ourse:propertyMapping   ?propMap.
                                            ?propMap ourse:property ?prop.
                                      }""", initBindings={'?clsmap': classMap})

        for (propMap, prop) in res3:
            self.__mappings[propMap] = ClassProperty.create(confGraph, propMap)

    def getURIForObject(self, object, baseURI):
        uri = self.__uriPattern
        if uri == ns_ourse['blankURI']:
            return BNode()
        else:            
            for (param, getter) in self.__bindings.iteritems():
                uri = uri.replace('@@%s@@' % param, getter.apply(object))
            return URIRef(urljoin(baseURI, uri))

    def getPropertyMappings(self):
        return self.__mappings

    def getObjectProvider(self):
        return  self.__objectProvider

    def getTargetClass(self):
        return self.__targetCls

class ClassProperty:
    @classmethod
    def create(cls, graph, propMapping):
        trType = graph.value(subject=propMapping, predicate=RDF.type, object=None)
        if (trType == ns_ourse['SimplePropertyMapping']):
            return LiteralClassProperty(graph.value(subject=propMapping, predicate=ns_ourse['property'], object=None),
                                     Getter.create(graph, graph.value(subject=propMapping, predicate=ns_ourse['getter'], object=None)),
                                     graph.value(subject=propMapping, predicate=ns_ourse['datatype'], object=None))
        elif (trType == ns_ourse['ComplexPropertyMapping']):
            return ResourceClassProperty(graph.value(subject=propMapping, predicate=ns_ourse['property'], object=None),
                                      Getter.create(graph, graph.value(subject=propMapping, predicate=ns_ourse['getter'], object=None)),
                                      graph.value(subject=propMapping, predicate=ns_ourse['targetClassMap'], object=None))
        else:
            raise Exception("This type of ClassProperty is not supported (%s)!" % str(trType))
                                                    
    def __init__(self, prop, getter):
        self._property = prop
        self._getter = getter

    def getPredicate(self):
        return self._property
    
class LiteralClassProperty(ClassProperty):

    def __init__(self, prop, getter, datatype):
        ClassProperty.__init__(self, prop, getter)
        self.__datatype = datatype

    def getValue(self, object):
        value = self._getter.apply(object)
        if self.__datatype == ns_xsd['anyURI']:
            value = URIRef(value)
        return value

class ResourceClassProperty(ClassProperty):

    def __init__(self, prop, getter, targetClassMap):
        ClassProperty.__init__(self, prop, getter)
        self.__targetClassMap = targetClassMap

    def getResourceObject(self, object):
        return self._getter.apply(object)

    def getTargetClass(self):
        return self.__targetClassMap
