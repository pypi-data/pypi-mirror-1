# -*- coding: utf-8 -*-
import datetime

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.test import TestCase
from dojoserializer import DojoDataJSONResponse, serialize


class GenericSomething(models.Model):
    content_type = models.ForeignKey(ContentType,
        related_name='generic_somethings')
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    class Meta:
        app_label = 'dojoserializer'


class TestModel(models.Model):
    """An ordinary django model to test with"""
    booleanfield = models.BooleanField(default=True)
    charfield = models.CharField(max_length=200, default='Foo')
    datefield = models.DateField(default=datetime.date(2009, 7, 3))
    datetimefield = models.DateTimeField(default=datetime.datetime(2009, 7, 3,
        13, 59, 00))
    decimalfield = models.DecimalField(max_digits=5, decimal_places=2,
        default='123.45')
    floatfield = models.FloatField(default=123.45)
    integerfield = models.IntegerField(default=123)
    nullbooleanfield = models.NullBooleanField(default=None)
    timefield = models.TimeField(default=datetime.time(23, 59, 59))
    urlfield = models.URLField(verify_exists=False,
        default='http://www.foo.bar')
    # Relationships
    another_testmodel = models.ForeignKey('self', blank=True, null=True)
    many_other_testmodels = models.ManyToManyField('self', blank=True,
        null=True)
    # Generic relationships
    generic_somethings = generic.GenericRelation(GenericSomething)
    class Meta:
        app_label = 'dojoserializer'
    
    def __unicode__(self):
        return u'%s' % self.charfield
        

class DojoSerializerTestCase(TestCase):
    def setUp(self):
        self.tm_1 = TestModel.objects.create(charfield='tm_1')
        self.tm_2 = TestModel.objects.create(charfield='tm_2')
        self.tm_3 = TestModel.objects.create(charfield='tm_3')
        self.testmodel = TestModel.objects.create(charfield='testmodel',
            another_testmodel=self.tm_1)
        self.testmodel.many_other_testmodels.add(self.tm_2, self.tm_3)
        self.testmodel.generic_somethings.create()
        self.testmodel.generic_somethings.create()
        self.testmodel.generic_somethings.create()
    
    def test_setup(self):
        self.assertTrue(self.tm_1)
        self.assertTrue(self.tm_2)
        self.assertTrue(self.tm_3)
        self.assertTrue(self.testmodel)
        self.assertTrue(self.testmodel.another_testmodel)
        self.assertEquals(self.testmodel.many_other_testmodels.count(), 2)
        self.assertEquals(self.testmodel.generic_somethings.count(), 3)
        
    def test_serialize(self):
        ser_testmodel = serialize(self.testmodel)
        ref_json = """{}&&\n{"numRows": 1, "items": [{"datefield": "2009-07-03", "integerfield": 123, "generic_somethings": [1, 2, 3], "many_other_testmodels": [2, 3], "id": 4, "_unicode": "testmodel", "urlfield": "http://www.foo.bar", "nullbooleanfield": null, "floatfield": 123.45, "timefield": "23:59:59", "charfield": "testmodel", "_pk": 4, "booleanfield": true, "datetimefield": "2009-07-03T13:59:00", "another_testmodel": 1, "decimalfield": "123.45"}], "identifier": "_pk", "label": "_unicode"}"""
        self.assertEquals(ser_testmodel, ref_json)
        
    def test_serialize_id_only(self):
        ser_testmodel = serialize(self.testmodel, fields=('id',))
        ref_json = """{}&&\n{"numRows": 1, "items": [{"_unicode": "testmodel", "id": 4, "_pk": 4}], "identifier": "_pk", "label": "_unicode"}"""
        self.assertEquals(ser_testmodel, ref_json)
        
    def test_serialize_id_and_charfield_but_exclude_charfield(self):
        ser_testmodel = serialize(self.testmodel, fields=('id', 'charfield',),
            exclude_fields=('charfield',))
        ref_json = """{}&&\n{"numRows": 1, "items": [{"_unicode": "testmodel", "id": 4, "_pk": 4}], "identifier": "_pk", "label": "_unicode"}"""
        self.assertEquals(ser_testmodel, ref_json)
        
    def test_serialize_exclude_urlfield_with_model_info(self):
        ser_testmodel = serialize(self.testmodel, exclude_fields=('urlfield',),
            add_model_info=True)
        ref_json = """{}&&\n{"numRows": 1, "items": [{"datefield": "2009-07-03", "integerfield": 123, "generic_somethings": [1, 2, 3], "many_other_testmodels": [2, 3], "id": 4, "_unicode": "testmodel", "nullbooleanfield": null, "floatfield": 123.45, "timefield": "23:59:59", "charfield": "testmodel", "_pk": 4, "booleanfield": true, "datetimefield": "2009-07-03T13:59:00", "another_testmodel": 1, "decimalfield": "123.45"}], "identifier": "_pk", "label": "_unicode"}"""
        self.assertEquals(ser_testmodel, ref_json)
        
    def test_dojodatajsonresponse(self):
        response = DojoDataJSONResponse(self.testmodel)
        self.assertEquals(response.content, serialize(self.testmodel))
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.has_header('Last-Modified'))
        self.assertTrue(response.has_header('Pragma'))
        self.assertTrue(response.has_header('Cache-Control'))
        self.assertTrue(response.has_header('Content-Type'))
        self.assertTrue(response.has_header('Expires'))
        
    def test_test_dojodatajsonresponse_argumentpassing(self):
        response = DojoDataJSONResponse(self.testmodel, ('id', 'charfield',),
            ('charfield',), True)
        ser_testmodel = serialize(self.testmodel, ('id', 'charfield',),
            ('charfield',), True)
        self.assertEquals(response.content, ser_testmodel)