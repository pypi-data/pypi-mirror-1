#
# (c) 2010 Johannes Dollinger, Andreas Kostyrka
#
# initial idea, initial implementation: Johannes Dollinger
# debugging, unittests: Andreas Kostyrka
#

from collections import namedtuple
from django.db import models
from django.utils.datastructures import SortedDict

class DeclarativeCompoundFieldBase(type):
    def __new__(meta, name, bases, attrs):
        fields = []
        for fieldname, value in attrs.items():
            if isinstance(value, models.Field):
                fields.append((value.creation_counter, fieldname, value))
                attrs.pop(fieldname)
        fields.sort()
        attrs["subfields"] = SortedDict([(fieldname, field) for _, fieldname, field in fields])
        def __init__(self, **kw):
            for k, v in kw.items():
                setattr(self, k, v)
        attrs["new_class"] = type(name + "_helper", (object, ), {"__init__": __init__})
        return type.__new__(meta, name, bases, attrs)

class CompoundFieldValueWrapper(object):
    """ A wrapper around values returned from the CompoundField descriptor that automatically updates the underlying model fields"""
    def __init__(self, field, instance, value):
        self.__dict__["_field"] = field
        self.__dict__["_instance"] = instance
        self.__dict__["_value"] = value

    def __getattr__(self, name):
        if name.startswith("_"):
            return object.__getattr__(self, name)
        if self is not self._value:
            return getattr(self._value, name)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            return object.__setattr__(self, name, value)
        setattr(self._value, name, value)
        setattr(self._instance, self._field.get_subfield_name(name), getattr(self._value, name, value))

class CompoundField(object):
    __metaclass__ = DeclarativeCompoundFieldBase

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    def map_values(self, **subfield_values):
        return self.new_class(**subfield_values)
        
    def get_subfield_name(self, name):
        return "%s_%s" % (self.name, name)
        
    def get_subfield_value(self, instance, name):
        return getattr(instance, self.get_subfield_name(name))
        
    def __set__(self, instance, value):
        for name in self.subfields:
            setattr(self.get_subfield_name(name), getattr(value, name))
        setattr(instance, self.cache_name, value)

    def __get__(self, instance, instance_type=None):
        if not instance:
            return self
        if not hasattr(instance, self.cache_name):
            subfield_values = dict((name, self.get_subfield_value(instance, name)) for name in self.subfields)
            value = self.map_values(**subfield_values)
            setattr(instance, self.cache_name, CompoundFieldValueWrapper(self, instance, value))
        return getattr(instance, self.cache_name)

    def contribute_to_class(*args): #self, cls, name):
        self, cls, name = args
        self.name = name
        self.cache_name = "_%s_cache" % name
        setattr(cls, name, self)
        for field_name, field in self.subfields.iteritems():
            field.contribute_to_class(cls, self.get_subfield_name(field_name))


class AddressField(CompoundField):
    phone = models.CharField(max_length=30)
    mobile = models.CharField(max_length=30)
    fax = models.CharField(max_length=30)
    email = models.EmailField()
    
    
