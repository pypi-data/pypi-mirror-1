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

import logging
from django.conf.urls.defaults import patterns
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseGone, HttpResponseBadRequest, HttpResponseNotAllowed
from django.utils.html import escape
from django.utils.translation import ugettext as _
import mimeparse

class Resource:
    """
    This is the base class for all REST resources.
    
    This class is not coupled with the Django model, i.e., you can subclass this class to
    create REST resources using your own Python code.
    """

    allow_method_param = True
    allow_info_param   = True
    allow_accept_param = True
    method_param = "_method"
    info_param   = "_info"
    accept_param = "_accept"
    fallback_mimetypes = []

    def __init__(self, name, methods, parent_resource = None, output_fields = None, auth_decorator_get = None, auth_decorator_update = None, template_name = None):
        self.name = name
        self.methods = methods
        self.parent_resource = parent_resource
        self.output_fields = output_fields
        self.fallback_get = self.default_fallback
        self.fallback_post = self.default_fallback
        self.auth_decorator_get = auth_decorator_get
        self.auth_decorator_update = auth_decorator_update
        if not self.auth_decorator_get and self.auth_decorator_update and self.get_methods_but_get():
            logging.warn("Resource %s has protected the GET method but not the other ones (%s)" % (self.name, str(self.get_methods_but_get())))
        self.template_name = template_name
        self.formatters = {}
        self.adapters = []

    def get_methods_but_get(self):
        return filter(lambda m: m != "GET", list(self.methods))

    def get_urlpatterns(self):
        return patterns('', (r'^' + self.get_url_regex() + r'$', self.front_controller))

    def get_url_regex(self):
        return self.get_prefix_url_regex() + self.get_local_url_regex()

    def get_local_url_regex(self):
        return (self.name + "/") if self.is_directory_resource() else self.name

    def get_prefix_url_regex(self):
        if self.parent_resource:
            prefix = self.parent_resource.get_url_regex()
            return prefix if (prefix[-1] == '/') else (prefix + "/")
        else:
            return ""
    
    def is_directory_resource(self):
        return "POST" in self.methods

    def front_controller(self, request, **args):
        logging.info("Resource %s at %s receives a %s request" %(self.name, request.path, request.method))
        method = request.method
        if self.allow_method_param and request.method == 'GET' and self.method_param in request.GET:
            method = request.GET[self.method_param].upper()
        if self.allow_info_param and method == 'GET' and self.info_param in request.GET:
            return self.info(request, **args)
        if not (method in self.methods):
            response = HttpResponseNotAllowed(list(self.methods))
            response.write('<h1>ERROR: method %s not allowed for resource %s at path %s</h1>' % (method, self.name, request.path))
            return response
        accept = self.get_accept(request)
        content_type = request.META.has_key('CONTENT_TYPE') and request.META['CONTENT_TYPE'] or ""
        return self.request_dispatcher(request, method, accept, content_type, **args)
        
    def request_dispatcher(self, request, method, accept, content_type, **args):
        if method == 'GET':
            try:
                best = mimeparse.best_match(self.formatters.keys() + self.fallback_mimetypes, accept)
            except ValueError,e:
                response = HttpResponseBadRequest(mimetype='text/html')
                response.write('<h1>ERROR: invalid Accept string: %s</h1>' % accept)
                return response
            if best in self.formatters.keys():
                return self.decorate_get(self.read)(request, **args)
            else:
                # FIXME: should we decorate the fallbacks?
                return self.call_fallback_get(request, **args)
        elif method == 'POST':
            if content_type in self.formatters.keys():
                return self.decorate_update(self.create)(request, **args)
            else:
                # FIXME: should we decorate the fallbacks?
                return self.fallback_post(request, **args)
        elif method == 'PUT':
            return self.decorate_update(self.update)(request, **args)
        elif method == 'DELETE':
            return self.decorate_update(self.delete)(request, **args)
        else:
            response = HttpResponseBadRequest(mimetype='text/html')
            response.write("<h1>ERROR: unknown HTTP method %s against resource %s at %s" % (method, self.name, request.path))
            return response
            
    def decorate_get(self, func):
        if self.auth_decorator_get:
            return self.auth_decorator_get(func)
        else:
            return func
        
    def decorate_update(self, func):
        if self.auth_decorator_update:
            return self.auth_decorator_update(func)
        else:
            return func

    def get_accept(self, request):
        if self.allow_accept_param and self.accept_param in request.REQUEST:
            return request.REQUEST[self.accept_param]
        else:
            return request.META.has_key('HTTP_ACCEPT') and request.META['HTTP_ACCEPT'] or ""

    def get_class_doc(self):
        return self.__class__.__doc__

    def get_relative_link_to_parent(self):
        return ".." if self.is_directory_resource() else "." # FIXME: this expression does not work in all cases        

    def call_fallback_get(self, request, **args):
        final_args = dict(args)
        final_args.update(self.as_resource_dict())
        return self.fallback_get(request, **final_args)
        
    def get_auth_info_get(self):
        return self.auth_decorator_get.__doc__ if self.auth_decorator_get else _("No authentication")
    
    def get_auth_info_update(self):
        return self.auth_decorator_update.__doc__ if self.auth_decorator_update else _("No authentication")

    def get_info_string(self, request = None, **args):
        url_patterns = [p.regex.pattern for p in self.get_urlpatterns()]
        actual_path = ("at path %s" % request.path) if request else ""
        info_string = ""
        info_string += '<h1>Information page for resource "%s" %s</h1>' % (self.name, actual_path)
        info_string += '<dl>'
        info_string += '<dt>Documentation string</dt><dd>%s</dd>' % self.get_class_doc()
        info_string += '<dt>Allowed HTTP methods</dt><dd>%s</dd>' % str(self.methods)
        info_string += '<dt>URL patterns</dt><dd><pre>%s</pre></dd>' % escape(str(url_patterns))
        if self.parent_resource:
            info_string += '<dt>Parent resource</dt><dd><a href="%s/?_info">%s</a></dd>' % (self.get_relative_link_to_parent(), escape(str(self.parent_resource.name)))
        info_string += '<dt>Valid mimetypes for the service<dt><dd>%s</dd>' % escape(str(self.formatters.keys()))
        info_string += '<dt>Fallback mimetypes</dt><dd>%s</dd>' % escape(str(self.fallback_mimetypes))
        info_string += '<dt>Authentication required?</dt><dd>%s</dd>' % 'Sorry, no info available yet'
        info_string += '</dl>'
        return info_string
        
    def info(self, request, **args):
        return render_info(request, [self])

    def create(self, request, **args):
        raise "ERROR: unsupported method on resource"

    def read(self, request, **args):
        raise "ERROR: unsupported method on resource"

    def update(self, request, **args):
        raise "ERROR: unsupported method on resource"

    def delete(self, request, **args):
        raise "ERROR: unsupported method on resource"

    def default_fallback(self, request, **args):
        response = HttpResponseBadRequest(mimetype='text/html')
        response.write("<h1>ERROR: please use one of the following MIME types %s in the HTTP headers of the request (Accept or Content-Type)</h1>" % str(self.formatters.keys()))
        response.write("<p>Your current 'Accept' header: %s</p>" % escape(request.META.has_key('HTTP_ACCEPT') and request.META['HTTP_ACCEPT'] or ""))
        response.write("<p>Your current 'Content-type' header: %s</p>" % escape(request.META.has_key('CONTENT_TYPE') and request.META['CONTENT_TYPE'] or ""))
        return response

    def get_best_formatter(self, request):
        return self.formatters[self.get_best_format(request)]

    def get_best_format(self, request):
        accept = self.get_accept(request)
        return mimeparse.best_match(self.formatters.keys(), accept)

    def as_resource_dict(self):
        # taken from recipe 4.13 from Python Cookbook 2nd ed
        somekeys = ['slug_field', 'form_class', 'extra_context', 'login_required', 'template_name'] # FIXME
        return dict([ (k, self.__dict__.get(k)) for k in somekeys if k in self.__dict__ and self.__dict__.get(k)])

    def apply_direct_adapters(self, dict_1):
        dict_n = dict_1
        for adapter in self.adapters:
             dict_n = adapter.direct(dict_n)
        return dict_n

    def apply_reverse_adapters(self, dict_n): #FIXME??? Same  method named
        reverse_list = list(self.adapters)
        reverse_list.reverse()
        dict_1 = dict_n
        for adapter in reverse_list:
             dict_1 = adapter.direct(dict_1)
        return dict_1

######################################################################

def render_info(request, resources):
    show_toc = len(resources)>1
    return render_to_response("RESTinpy/resource_info.html", {"resources": resources, "show_toc": show_toc}, context_instance = RequestContext(request))

def get_resources_defined_in_module(module):
    return [val for val in module.__dict__.values() if isinstance(val, Resource)]
