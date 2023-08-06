# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db import models
from django.db.models.fields.related import ForeignKey
from django.http import HttpResponse, HttpResponseBadRequest, \
    HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.views.generic.create_update import get_model_and_form_class
from dojoserializer import DojoDataJSONResponse

def create_object(request, model=None, form_class=None, login_required=False,
    fields=(), exclude_fields=(), add_model_info=False):
    """
    Creates a valid model instance and returns it dojo data serialized. 
    """
    if login_required and not request.user.is_authenticated():
        return HttpResponseForbidden()
    if request.method in ['POST', 'PUT']:
        model, form_class = get_model_and_form_class(model, form_class)
        data = model().__dict__              # default values
        data.update(request.POST.items())
        data.update(request.FILES.items())
        form = form_class(data)
        if form.is_valid():
            new_obj = form.save()
            return DojoDataJSONResponse(new_obj, fields=fields, exclude_fields=\
                exclude_fields, add_model_info=add_model_info, status=201)
        else:
            return HttpResponseBadRequest(content=form.errors)
    else:
        return HttpResponseNotAllowed()

def read_object(request, model, object_id, login_required=False, fields=(),
    exclude_fields=(), add_model_info=False):
    """
    Reads and returns a model instance and returns it dojo data serialized.
    """
    if login_required and not request.user.is_authenticated():
        return HttpResponseForbidden()
    if request.method in ['GET', 'HEAD']:
        obj = get_object_or_404(model, pk=object_id)
        if request.method == 'GET':
            return DojoDataJSONResponse(obj, fields=fields, exclude_fields=\
                exclude_fields, add_model_info=add_model_info)
        return HttpResponse()
    else:
        return HttpResponseNotAllowed()
        
def update_object(request, object_id, model=None, form_class=None,
    login_required=False, fields=(), exclude_fields=(), add_model_info=False):
    """
    Updates and returns a model instance dojo data serialized.
    """
    if login_required and not request.user.is_authenticated():
        return HttpResponseForbidden()
    if request.method in ['POST', 'PUT']:
        model, form_class = get_model_and_form_class(model, form_class)
        obj = get_object_or_404(model, pk=object_id)
        data = { }
        fk_fields = [fk_field for fk_field in obj._meta.fields if isinstance(
            fk_field, ForeignKey)]
        for fk_field in fk_fields:
            foreign_obj = getattr(obj, fk_field.name)
            if foreign_obj and foreign_obj.id:
                data.update({ fk_field.name: foreign_obj.id })
        data.update(dict(request.REQUEST.items()))
        data.update(request.FILES.items())
        obj.__dict__.update(data)
        form = form_class(obj.__dict__)
        if form.is_valid():
            obj.save()
            return DojoDataJSONResponse(obj, fields=fields, exclude_fields=\
                exclude_fields, add_model_info=add_model_info)
        else:
            return HttpResponseBadRequest()
    else:
        return HttpResponseNotAllowed()
        
def delete_object(request, model, object_id, login_required=False):
    """
    Deletes a model instance.
    """
    if login_required and not request.user.is_authenticated():
        return HttpResponseForbidden()
    if request.method == 'DELETE':
        obj = get_object_or_404(model, pk=object_id)
        obj.delete()
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed()
        
def object_list(request, queryset, paginate_by=None, page=None,
    login_required=False, allow_empty=False, fields=(), exclude_fields=(),
    add_model_info=False):
    """
    Returns a dojo serialized list of model instances defined in a queryset.
    
    Allow_empty returns the status code 200 if lists are empty, when set to
    False this would return status code 404 (which is the default behavior).
    
    Using the arguments or request parameters 'paginate_by' (default: 10) and
    'page' (default: 1) you're able to paginate through object lists.
    
    To allow listings to logged in users only, set 'login_required' to True.
    
    To customize the fields of the resulting JSON output, you can populate the
    'fields' and/or 'exclude_fields' tuple with fieldnames. Set 'add_model_info'
    to True to get the objects app_label and module_names.
    """
    if login_required and not request.user.is_authenticated():
        return HttpResponseForbidden()
    if request.method in ['GET', 'HEAD']:
        if not page:
            try:
                page = int(request.GET.get('page', '1'))
            except ValueError:
                page = 1
        if not paginate_by:
            try:
                paginate_by = int(request.GET.get('paginate_by', '10'))
            except ValueError:
                paginate_by = 10
        try:
            paginator = Paginator(queryset, paginate_by)
            objects = paginator.page(page).object_list
        except:
            return HttpResponseBadRequest()
        if not allow_empty and not objects:
            return HttpResponseNotFound()
        elif request.method == 'GET':
            return DojoDataJSONResponse(objects, fields=fields,
                exclude_fields=exclude_fields, add_model_info=add_model_info)
        elif request.method == 'HEAD':
            return HttpResponse()
    else:
        return HttpResponseNotAllowed()
        
def object_list_filtered_by_generic_fk(request, related_object_id,
    related_object_model=None, related_object_app_label=None,
    related_object_model_name=None, related_object_id_field_name='object_id',
    related_object_content_type_field_name='content_type',
    query_object_model=None, query_object_app_label=None,
    query_object_model_name=None, allow_empty=False, paginate_by=None,
    page=None, login_required=False, fields=(), exclude_fields=(),
    add_model_info=False):
    """
    Returns a dojo serialized list of model instances filtered by a generic
    relation.
    
    E.g. you can return all BlogPost (the query object) instances that are
    tagged with the Tag (the related object) 'Foo', which has the id 4 (the
    related_object_id).
    
    Both the model for the query object and the related object can be passed
    directly ('query_object_model' and 'related_object_model') or indirectly
    using their app label and model name values ('query_object_app_label' and
    'query_object_model_name' for the query object and
    'related_object_app_label' and 'related_object_model_name' for the related
    object).
    
    Allow_empty returns the status code 200 if lists are empty, when set to
    False this would return status code 404 (which is the default behavior).
    
    Using the arguments or request parameters 'paginate_by' (default: 10) and
    'page' (default: 1) you're able to paginate through object lists.
    
    To allow listings to logged in users only, set 'login_required' to True.
    
    To customize the fields of the resulting JSON output, you can populate the
    'fields' and/or 'exclude_fields' tuple with fieldnames. Set 'add_model_info'
    to True to get the objects app_label and module_names.
    """
    if request.method in ['GET', 'HEAD']:
        if not query_object_model and query_object_app_label and \
            query_object_model_name:
            query_object_model = models.get_model(query_object_app_label,
                query_object_model_name)
        if not related_object_model and related_object_app_label and \
            related_object_model_name:
            related_object_model = models.get_model(related_object_app_label,
                related_object_model_name)
        if not query_object_model or not related_object_model:
            return HttpResponseBadRequest()
        related_object_content_type = ContentType.objects.get_for_model(
            related_object_model)
        try:
            filters = {
                related_object_content_type_field_name: \
                    related_object_content_type.id,
                related_object_id_field_name: related_object_id,
            }
            queryset = query_object_model._default_manager.filter(**filters)
            if not allow_empty and not queryset:
                return HttpResponseNotFound()
            if request.method == 'HEAD':
                return HttpResponse()
            return object_list(request, queryset, paginate_by=paginate_by,
                page=page, login_required=login_required,
                allow_empty=allow_empty, fields=fields,
                exclude_fields=exclude_fields, add_model_info=add_model_info)
        except:
            return HttpResponseBadRequest()
    else:
        return HttpResponseNotAllowed()
        
def object_list_filtered_by_fk(request, related_object_id,
    related_object_field_name=None, query_object_model=None,
    query_object_app_label=None, query_object_model_name=None,
    allow_empty=False, paginate_by=None, page=None, login_required=False,
    fields=(), exclude_fields=(), add_model_info=False):
    """
    Returns a dojo serialized list of model instances filtered by a foreign
    key relation.
    
    E.g. you can return all Comment (the query object) instances that are
    related to a BlogPost (the related object) 'First Post', which has the id
    3 (the related_object_id).
    
    The model of the query object can be passed directly ('query_object_model')
    or indirectly using its app label and model name values (
    'query_object_app_label' and 'query_object_model_name').
    
    Allow_empty returns the status code 200 if lists are empty, when set to
    False this would return status code 404 (which is the default behavior).
    
    Using the arguments or request parameters 'paginate_by' (default: 10) and
    'page' (default: 1) you're able to paginate through object lists.
    
    To allow listings to logged in users only, set 'login_required' to True.
    
    To customize the fields of the resulting JSON output, you can populate the
    'fields' and/or 'exclude_fields' tuple with fieldnames. Set 'add_model_info'
    to True to get the objects app_label and module_names.
    """
    if request.method in ['GET', 'HEAD']:
        if not query_object_model and query_object_app_label and \
            query_object_model_name:
            query_object_model = models.get_model(query_object_app_label,
                query_object_model_name)
        if not query_object_model or not related_object_id or not \
            related_object_field_name:
            return HttpResponseBadRequest()
        try:
            filters = {
                related_object_field_name: related_object_id,
            }
            queryset = query_object_model._default_manager.filter(**filters)
            if not allow_empty and not queryset:
                return HttpResponseNotFound()
            if request.method == 'HEAD':
                return HttpResponse()
            return object_list(request, queryset, paginate_by=paginate_by,
                page=page, login_required=login_required,
                allow_empty=allow_empty, fields=fields,
                exclude_fields=exclude_fields, add_model_info=add_model_info)
        except Exception:
            return HttpResponseBadRequest()
    else:
        return HttpResponseNotAllowed()
        
def restful_dispatcher(request, model, form_class=None, object_id=None,
    login_required=False, fields=(), exclude_fields=(), add_model_info=False):
    """
    Dispatches requests in a RESTful manner.
    """
    if login_required and not request.user.is_authenticated():
        return HttpResponseForbidden()
    if request.method in ['POST', 'PUT'] and not object_id:
        return create_object(request, model=model, form_class=form_class,
            login_required=login_required, fields=fields, exclude_fields=\
            exclude_fields, add_model_info=add_model_info)
    elif request.method in ['POST', 'PUT'] and object_id:
        return update_object(request, model=model, form_class=form_class,
            object_id=object_id, login_required=login_required, fields=fields,
            exclude_fields=exclude_fields, add_model_info=add_model_info)
    elif request.method == 'DELETE':
        if not object_id:
            return HttpResponseBadRequest()
        return delete_object(request, model=model, object_id=object_id,
            login_required=login_required)
    elif request.method in ['GET', 'HEAD']:
        if object_id:
            return read_object(request, model=model, object_id=object_id,
                login_required=login_required, fields=fields,
                exclude_fields=exclude_fields, add_model_info=add_model_info)
        else:
            return object_list(request, model._default_manager.all(),
                login_required=login_required, fields=fields,
                exclude_fields=exclude_fields, add_model_info=add_model_info)