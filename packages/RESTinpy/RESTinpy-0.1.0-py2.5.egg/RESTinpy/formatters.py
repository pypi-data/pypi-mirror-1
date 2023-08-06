# -*- coding: utf-8 -*-
# Copyright Fundacion CTIC, 2009 http://www.fundacionctic.org/
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import utils
from xml.sax.saxutils import XMLGenerator
from StringIO import StringIO

DEFAULT_CHARSET ='utf-8'

class XmlFormatter(object):

    def __init__(self):
        pass
        
    def format(self, dict):
        self.stream = StringIO()
        
        self.start_serialization()
        self.ind = 1 # initial indent
        self.start_nodes(dict.itervalues(), self.ind)
        self.end_serialization()
        
        if callable(getattr(self.stream, 'getvalue', None)):
            return self.stream.getvalue()

    def unformat(self, data):
        pass
        #return from_raw_deserialized_data_to_dictionary(self.serializer.deserialize(data))
    
    def indent(self, level):
        self.xml.ignorableWhitespace('\n' + '  ' * level)
            
    def start_serialization(self):
        """
        Start serialization -- open the XML document and the root element.
        """
        self.xml = XMLGenerator(self.stream, encoding = DEFAULT_CHARSET)
        self.xml.startDocument()
        self.xml.startElement("objects", {"version" : "1.0", "xmlns":"http://rest-in-py.sourceforge.net/ns/", "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance" ,"xsi:schemaLocation":"http://rest-in-py.sourceforge.net/ns/ http://rest-in-py.sourceforge.net/schema.xsd"})

    def end_serialization(self):
        """
        End serialization -- end the document.
        """
        self.indent(0)
        self.xml.endElement("objects")
        self.xml.endDocument()
    
    def start_nodes(self, nodes, ind):
        for objects in nodes:
            for obj in objects:
                if self.start_object(obj, ind) is not None:
                    self.end_object(ind)
    
    def start_object(self, obj, ind):
        """
        Called as each object is handled.
        """
        if obj.has_key('resource'):
            if obj.get('resource') is None:
                return None # if object resource is an empty list, there isn't object.
            else:
                self.indent(ind)
                self.xml.startElement("object", {'resource': obj.get('resource'),})
        if obj.has_key('field'):
            self.start_fields(obj.get('field'), ind+1)
        return not None
    
    def start_fields(self, value, ind):
        for k, v in value.items():
            self.indent(ind)
            if not isinstance(v, dict):
                # Direct field
                self.xml.startElement("field", {'property': k,})
                self.xml.characters(unicode(v))
                self.xml.endElement("field")
            else:
                # The field is a dictionary
                # 'rel' attribute and other attributes
                v['rel']=k
                attrs = dict((k, r) for k, r in v.items() if not isinstance(r, list) and r is not None) # FIXME!!!!
                self.xml.startElement("field", attrs)
                # children objects
                children = dict((k, r) for k, r in v.items() if isinstance(r, list))
                self.start_nodes(children.itervalues(), ind+1)
                self.xml.endElement("field")
        
    def end_object(self, ind):
        """
        Called after handling all fields for an object.
        """
        self.indent(ind)
        self.xml.endElement("object")

class JsonFormatter(object):

    def __init__(self):
        pass

    def format(self, obj, fields = None): # FIXME: remove fields parameter
        return utils.dumps(obj, ensure_ascii=False)

    def unformat(self, data):
        return simplejson.loads(data)

# def from_raw_deserialized_data_to_dictionary(raw_deserialized_data):
#     deserialized_objs = [x for x in raw_deserialized_data]
#     if (len(deserialized_objs) is not 1):
#         raise Exception('<h1>ERROR: cannot parse a single object in the body of the request</h1>') # FIXME: this should not raise an exception. It is not the programmer's fault, it's the client's fault
#     return Wrapper(deserialized_objs[0])
# 
# class Wrapper:
# 
#     def __init__(self, wrapped):
#         self.wrapped = wrapped
# 
#     def get(self, key, default):
#         try:
#             return getattr(self.wrapped.object, key)
#         except FieldDoesNotExist:
#             return default
