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

from resources import *
import logging
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseGone, HttpResponseBadRequest
from django.db.models.related import RelatedObject
from django.db.models import ManyToManyField, ForeignKey

DEFAULT_CHARSET =';charset=utf-8'

class ModelBaseResource(Resource):
    """
    This class specializes Resource for applications with a Django model back-end.
    This is intended to be an abstract class, please take a look at its
    subclasses (ModelResource and ModelListResource) instead.
    """
    
    def __init__(self, name, methods, model_class, form_class = None, **kwargs):
        Resource.__init__(self, name, methods, **kwargs)
        self.model_class = model_class
        self.form_class = form_class

    def get_info_string(self, request = None, **args):
        info_string = Resource.get_info_string(self, request, **args)
        info_string += '<p>This is a model-based resource</p>'
        if self.form_class is not None:
            info_string += '<h2>Data required</h2>'
            form = self.form_class()
            for field in form:
                info_string += '<p>%s</p>' % field.name # FIXME
        return info_string

    def get_queryset(self, request, **args):
        return self.model_class.objects.all()    

    def call_fallback_get(self, request, **args):
        return Resource.call_fallback_get(self, request, queryset = self.get_queryset(request, **args), **args)

    def get_output_fields(self):
        candidate_fields = self.model_class._meta.fields + self.model_class._meta.many_to_many

        for ro in self.model_class._meta.get_all_related_objects():
            candidate_fields.append(ManyToManyField(ro.model, name=ro.field.related_query_name()))

        return [f for f in candidate_fields if f.serialize and (not self.output_fields or f.name in self.output_fields)]

    def get_post_data_as_dict(self, request):
        content_type = request.META["CONTENT_TYPE"]
        # no need to check if the content_type is in self.formatters,
        # it has been checked before
        formatter = self.formatters[content_type]
        return formatter.unformat(request.raw_post_data)
        
    def get_dict_fields(self, queryset):
        big_fat_dict = []
        for obj in queryset:

            #logging.debug("Object: %s" % obj)
            # Direct fields (including ForeignKey)
            simple_fields = {}
            for field in obj._meta.local_fields:
                if isinstance(field, ForeignKey):
                    simple_fields[field.name] = {}
                    simple_fields[field.name]['objects']=[dict([('resource', getattr(obj,field.name))])]
                elif field.name != 'id':
                    simple_fields[field.name] = obj.__dict__[field.name]
            
            # ManyToMany fields 
            many_to_many_fields = {}
            for field in obj._meta.many_to_many:
                #logging.debug("Many to many field: %s" % field)
                related = (obj.__getattribute__(field.name))  
                m2m_field_dict = {}
                m2m_field_dict['objects']=[dict([('resource', object)]) for object in related.all()]
                m2m_field_dict['collection']=related.model #obj.managed_by --> Necesitamos la url del modelo!!! A donde redirigir los Post!
                many_to_many_fields[field.name] = m2m_field_dict

            # Related objects: each object show the resources'url
            related_fields = {}
            for field in obj._meta.get_all_related_objects():
                #logging.debug("Foreign key field: %s" % field)
                related = obj.__getattribute__(field.get_accessor_name())
                name = field.field.related_query_name()
                related_fields[name] = {}
                related_fields[name]['objects']=[dict([('resource', object)]) for object in related.all()]
                related_fields[name]['collection'] = related.model #obj.managed_by --> Necesitamos la url del modelo!!! A donde redirigir los Post!

            fields = {}
            fields['resource'] = obj
            fields['field'] = simple_fields
            fields['field'].update(many_to_many_fields)
            fields['field'].update(related_fields)
        
            big_fat_dict.append(fields)
            
        return dict([('objects',big_fat_dict)])
        
    def remove_None_fields(self, dictionary):
        #TODO
        return dictionary
######################################################################

class ModelListResource(ModelBaseResource):
    """
    This class provides reasonable implementations of some methods
    for a resource that represents a collection of items (i.e., other resources)
    with a Django model back-end.
    """

    def __init__(self, name, methods, model_class, **kwargs):
        ModelBaseResource.__init__(self, name, methods, model_class, **kwargs)
        
    def is_directory_resource(self):
        return True

    def read(self, request, **args):
        objects = self.get_queryset(request, **args)
        best_format = self.get_best_format(request)
        formatter = self.formatters[best_format]
        dict_1 = self.get_dict_fields(objects)
        dict_2 = self.apply_direct_adapters(dict_1)
        dict_n = dict_2
        # dict_n = self.remove_None_fields(dict_2) #TODO?
        return HttpResponse(formatter.format(dict_n), content_type=best_format+DEFAULT_CHARSET)

    def create(self, request, **args):
        form = self.form_class(self.get_post_data_as_dict(request))
        if form.is_valid():
            obj = form.save()
            response = HttpResponse()
            response.status_code = 200
            #response.encoding = DEFAULT_CHARSET#To Try. This line adds the charset in the Content-Type header of the response
            response.location = obj.get_absolute_url()
            response.write('<p>Object created, see <a href="%s">%s</a></p>' % (obj.get_absolute_url(), obj.get_absolute_url()))
            return response
        else:
            response = HttpResponseBadRequest(content_type='text/html'+DEFAULT_CHARSET)
            response.write('<form action="%s" method="POST">' % request.path)
            response.write(form.as_p())
            response.write('<input type="submit">')
            response.write('</form>')
            return response

######################################################################

class ModelResource(ModelBaseResource):
    """
    This class provides reasonable implementations of some methods for 
    a single resource with a Django model back-end.
    """

    def __init__(self, name, methods, model_class, slug_field = None, **kwargs):
        ModelBaseResource.__init__(self, name, methods, model_class, **kwargs)
        self.slug_field = slug_field

    def get_local_url_regex(self):
        return "(?P<%s>%s)" % (self.get_regex_param_key(), self.get_param_re())

    def get_regex_param_key(self):
        return self.name + "_id";
        
    def get_param_re(self):
        return "[\w-]+" if self.slug_field else r'\d+'

    # def call_fallback_get(self, request, **args):
    #     final_args = dict(args)
    #     if ('slug_field' in self.__dict__ and self.slug_field):
    #         final_args.update({'slug': args[self.get_regex_param_key()]})
    #         del final_args[self.get_regex_param_key()]
    #     final_args.update(self.as_resource_dict())
    #     return self.fallback_get(request, **final_args)

    def read(self, request, **args):
		objects = self.get_object(request, **args)
		best_format = self.get_best_format(request)
		formatter = self.formatters[best_format]
		dict_1 = self.get_dict_fields([objects])
		dict_2 = self.apply_direct_adapters(dict_1)
		dict_n = dict_2
		# dict_n = self.remove_None_fields(dict_2) #TODO?
		return HttpResponse(formatter.format(dict_n), content_type=best_format+DEFAULT_CHARSET)

    def update(self, request, **args):
        object = self.get_object(request, **args)
        form = self.form_class(self.get_post_data_as_dict(request), instance = object)
        if form.is_valid():
            obj = form.save()
            response = HttpResponse()
            response.status_code = 200
            #response.encoding = DEFAULT_CHARSET#To Try. This line adds the charset in the Content-Type header of the response
            response.location = obj.get_absolute_url()
            response.write('<p>Object updated</p>')
            return response
        else:
            response = HttpResponseBadRequest(content_type='text/html'+DEFAULT_CHARSET)
            response.write('<form action="%s" method="PUT">' % request.path)
            response.write(form.as_p())
            response.write('<input type="submit">')
            response.write('</form>')
            return response

    def delete(self, request, **args):
        object = self.get_object(request, **args)
        object.delete()
        response = HttpResponse()
        response.status_code = 200
        return response

    def get_object(self, request, **args):
        object_id = args[self.get_regex_param_key()]
        filter_by_field = self.slug_field if 'slug_field' in self.__dict__ and self.slug_field else 'id'
        filter_param = {filter_by_field: object_id}
        return get_object_or_404(self.get_queryset(request, **args), **filter_param)

######################################################################

class ModelSingletonResource(ModelResource):
    """
    This class provides default implementations of some methods for a
    singleton resource, a resource with a Django model back-end, but with
    a singularity. This class is abstract, you *must* override the get_object
    method in your subclass.
    """
    
    def __init__(self, name, methods, model_class, **kwargs):
        ModelResource.__init__(self, name, methods, model_class, **kwargs)

    def get_local_url_regex(self):
        return self.name

    def get_object(self, request, **args):
        raise Exception("Subclasses of ModelSingletonResource must override get_object")

    def call_fallback_get(self, request, **args):
        return ModelResource.call_fallback_get(self, request, object_id = self.get_object(request, **args).pk, **args)
