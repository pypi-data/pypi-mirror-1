# -*- coding: utf-8 -*-
from django.db.models.fields.related import ForeignKey
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from dojoserializer import serialize, DojoDataJSONResponse

def create(request, model, form_class):
    """
    Creates a valid model instance and returns it dojo data serialized. 
    """
    if request.method in ['POST', 'PUT']:
        data = model().__dict__
        data.update(request.REQUEST.items())
        form = form_class(data)
        if form.is_valid():
            obj = form.save()
            return DojoDataJSONResponse(obj, status=201)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=405)

def read(request, model, id=None):
    """
    Reads and returns a model instance and returns it dojo data serialized.
    """    
    if request.method == 'GET' and id:
        obj = get_object_or_404(model, pk=id)
        return DojoDataJSONResponse(obj, status=200)
    elif request.method == 'HEAD' and id:
        obj = get_object_or_404(model, pk=id)
        return HttpResponse(status=200)
    elif request.method in ['GET', 'HEAD'] and not id:
        return HttpReponse(status=400)
    else:
        return HttpResponse(status=405)
        
def update(request, model, form_class, id):
    """
    Updates and returns a model instance dojo data serialized.
    """
    if request.method in ['POST', 'PUT']:
        obj = get_object_or_404(model, pk=id)
        data = { }
        fk_fields = [fk_field for fk_field in obj._meta.fields if isinstance(
            fk_field, ForeignKey)]
        for fk_field in fk_fields:
            foreign_obj = getattr(obj, fk_field.name)
            if foreign_obj and foreign_obj.id:
                data.update({ fk_field.name: foreign_obj.id })
        data.update(dict(request.REQUEST.items()))
        obj.__dict__.update(data)
        form = form_class(obj.__dict__)
        if form.is_valid():
            obj.save()
            return DojoDataJSONResponse(obj, status=202)
        else:
            print form.errors
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=405)
        
def delete(request, model, id):
    """
    Deletes a model instance.
    """
    if request.method == 'DELETE':
        obj = get_object_or_404(model, pk=id)
        obj.delete()
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=405)
        
def dump(request, model):
    """
    Returns a dojo data serialized list of model instances.
    """
    if request.method == 'GET':
        queryset = model._default_manager.all()
        return DojoDataJSONResponse(queryset, status=200)
    elif request.method == 'HEAD':
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=405)
        
def restful_dispatcher(request, model, form_class, id=None):
    """
    Dispatches requests in a RESTful manner.
    """
    if request.method in ['POST', 'PUT'] and not id:
        return create(request, model, form_class)
    elif request.method in ['POST', 'PUT'] and id:
        return update(request, model, form_class, id)
    elif request.method == 'DELETE':
        if not id:
            return HttpResponse(status=400)
        return delete(request, model, id)
    elif request.method in ['GET', 'HEAD']:
        if id:
            return read(request, model, id)
        else:
            return dump(request, model)