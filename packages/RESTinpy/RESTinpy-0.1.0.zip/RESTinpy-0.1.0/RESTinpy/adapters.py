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

from django.db import models
import re

class IdentityAdapter:
    
    def direct(self, source):
        return dict(source)
        
    def inverse(self, source):
        return dict(source)

#####################################################################

class UriAdapter:
    
    def __init__(self, all_resources, baseurl = ""):
        self.all_resources = all_resources
        self.baseurl = baseurl
    
    def direct(self, source):
        if isinstance(source, models.Model):
            return self.baseurl + source.get_absolute_url()
        elif isinstance(source, dict):
            result = {}
            for k,v in source.items():
                result[k] = self.direct(v)
            return result
        elif isinstance(source, list) or isinstance(source, models.query.QuerySet):
            return [self.direct(x) for x in source]
        else:
            return source
        
    def inverse(self, source):
        if isinstance(source, dict):
            if "collection" in source:
                for resource in self.all_resources:
                    # add a regex terminator ($) and the trailing slash
                    regex = "/" + resource.get_url_regex() + "$"
                    args = re.match(regex, source["collection"])
                    if args:
                        source["resource"] = resource
                        source["model_class"] = resource.model_class
                        request = None # FIXME!! fake a request if needed
                        source["object"] = resource.get_object(request, **(args.groupdict()))
            return source
        elif isinstance(source, list):
            return [self.inverse(x) for x in source]
        else:
            return source

#####################################################################

class DirectoryUriAdapter:
    
    def __init__(self, all_resources, baseurl = ""):
        self.all_resources = all_resources
        self.baseurl = baseurl
    
    def direct(self, source):
      if (type(source)==dict and source.has_key('collection')):
        collection = source['collection']
        source['collection'] = None
        for resource in self.all_resources:
            if resource.model_class is collection:
                if resource.is_directory_resource():
                    source['collection']=self.baseurl + "/" + resource.get_url_regex() #FIXME. How to obtain the URL

      #Seguimos iterando
      if (type(source)==dict and source.has_key('objects')):
        for object in source['objects']: #  I know that it is a list.
            if (type(object)==dict and object.has_key('field')): 
                for k,v in object['field'].items():
                    self.direct(v)
      return source
        
    def inverse(self, source):
        return source
