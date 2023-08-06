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

from rdflib import RDF

from __init__ import ns_ourse

class ObjectProvider:
      @classmethod
      def create(cls, graph, provider):
            provType = graph.value(subject=provider, predicate=RDF.type, object=None)
            if (provType == ns_ourse['PathObjectProvider']):
                  return PathObjectProvider(graph.value(subject=provider, predicate=ns_ourse['DBPath'], object=None),
                                            graph.value(subject=provider, predicate=ns_ourse['dataStorage'], object=None))
            else:
                  raise Exception("This type of ObjectProvider is not supported (%s)!" % str(provType))

      def __init__(self, dbStorage):
            self.__dbStorage = dbStorage

      def getDBMapping(self):
            return self.__dbStorage

class PathObjectProvider(ObjectProvider):

      def __init__(self, dbPath, dataStorage):
            ObjectProvider.__init__(self, dataStorage)
            self._dbPath = dbPath
      
      def createRunner(self, driver):
            return driver.PathRunner(driver, self._dbPath)


class Getter:
      @classmethod
      def create(cls, graph, getter):
            getType = graph.value(subject=getter, predicate=RDF.type, object=None)
            if (getType == ns_ourse['MethodGetter']):
                  return MethodGetter(graph.value(subject=getter, predicate=ns_ourse['method'], object=None))
            elif (getType == ns_ourse['ViewGetter']):
                  return ViewGetter(graph.value(subject=getter, predicate=ns_ourse['view'], object=None))
            elif (getType == ns_ourse['IdentityGetter']):
                  return IdentityGetter()
            else:
                  raise Exception("This type of Getter is not supported (%s)!" % str(getType))
            
class IdentityGetter(Getter):
# The simplest, passes the object as it is
      def apply(self, object):
            return object

class ViewGetter(Getter):

      def __init__(self, view):
            self.__viewName = view
            
      def apply(self, object):
            moduleName = '.'.join(self.__viewName.split('.')[:-1])
            className = self.__viewName.split('.')[-1]    
            clazz = getattr(__import__(moduleName.replace('.','/'),globals(),locals(),['']), className)
            obj = clazz(object).run()
            return clazz(object).run()    
    

class MethodGetter(Getter):

      def __init__(self, method):
            self._method = method
            
      def apply(self, object):
            return getattr(object,self._method)()
                                                                                                          
