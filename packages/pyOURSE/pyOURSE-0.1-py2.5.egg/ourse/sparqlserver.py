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


from cgi import parse_qs

# TEST QUERIES:
#
# All titles with word 'hadron'
# http://localhost:8080/sparql?query=PREFIX+ical%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2002%2F12%2Fcal%2Fical%23%3E+PREFIX+foaf%3A+%3Chttp%3A%2F%2Fxmlns.com%2Ffoaf%2F0.1%2F%3E+PREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0ASELECT+%3Ftitle+WHERE+%7B+%3Fevt+rdfs%3Alabel+%3Ftitle.+FILTER+regex%28%3Ftitle%2C%22hadron%22%2C%22i%22%29+%7D
#
# All CERN-affiliated people
# http://localhost:8080/sparql?query=PREFIX+foaf%3A+%3Chttp%3A%2F%2Fxmlns.com%2Ffoaf%2F0.1%2F%3E+PREFIX+swc%3A+%3Chttp%3A%2F%2Fdata.semanticweb.org%2Fns%2Fswc%2Fontology%23%3E%0ASELECT+%3Fname+%3Faff+WHERE+%7B+%3Fperson+swc%3Aaffiliation+%3Faff+%3B+foaf%3Aname+%3Fname.+FILTER+regex%28%3Faff%2C%22cern%22%2C%22i%22%29+%7D

class SPARQLEndPoint:

    def __init__(self, regExp):
        self.__regExp = regExp

    def getRegExp(self):
        return self.__regExp

    def requestHandler(self, ourseInstance, bindings, environ):

        parameters = parse_qs(environ.get('QUERY_STRING', ''))


        qtext = parameters.get('query',None)
        format = parameters.get('format',None)

        if not qtext:
            return ('text/plain','No query specified...')  

        if not format:
            format = 'json'
        else:
            format = format[0]
        
        if not format in ['xml','json']:
            return ('text/plain','Format %s is not known...' % format)

        return self.sparqlRequestHandler(ourseInstance, qtext[0], format)


    def sparqlRequestHandler(self, ourseInstance, qtext, format):

        g = ourseInstance.getConjunctiveGraph()

        try:
            r = g.query(qtext)

            result = r.serialize(format = format)
            result = result.encode('utf-8')

            if format == 'json':
                mimeType = 'application/json'
            elif format == 'xml':
                mimeType = 'text/xml'
        
            return (format, result)
        except Exception, e:
            return ('text/plain',str(qtext)+'\n\n'+str(e))
        
