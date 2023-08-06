from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.safestring import mark_safe
import cPickle
import datetime
import cjson
from django.utils.translation import ugettext_lazy as _
from yadayada.managers import StdManager
try:
    import cPickle as pickle
except ImportError:
    import pickle


class SerializedObject(str):
    pass


class SerializedObjectField(models.Field):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, SerializedObject):
            # If the value is definitely serialized; and an error is raised
            # in de-serialization, it should be allowed to propogate.
            return cjson.decode(str(value))
        else:
            try:
                return cjson.decode(str(value))
            except:
                # If an error was raised, just return the plain value
                return value
    
    def get_db_prep_save(self, value):
        if value is not None and not isinstance(value, SerializedObject):
            value = SerializedObject(cjson.encode(value))
        return value
    
    def get_internal_type(self): 
        return 'TextField'
    
    def get_db_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            value = self.get_db_prep_save(value)
            return super(SerializedObjectField, self).get_db_prep_lookup(
                    lookup_type, value)
        elif lookup_type == 'in':
            value = [self.get_db_prep_save(v) for v in value]
            return super(SerializedObjectField, self).get_db_prep_lookup(
                    lookup_type, value)
        else:
            raise TypeError('Lookup type %s is not supported.' % lookup_type)


class PickledObject(str):
    """A subclass of string so it can be told whether a string is
       a pickled object or not (if the object is an instance of this class
       then it must [well, should] be a pickled one)."""
    pass


class PickledObjectField(models.Field):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, PickledObject):
            # If the value is a definite pickle; and an error is raised in de-pickling
            # it should be allowed to propogate.
            return pickle.loads(str(value))
        else:
            try:
                return pickle.loads(str(value))
            except:
                # If an error was raised, just return the plain value
                return value
    
    def get_db_prep_save(self, value):
        if value is not None and not isinstance(value, PickledObject):
            value = PickledObject(pickle.dumps(value))
        return value
    
    def get_internal_type(self): 
        return 'TextField'
    
    def get_db_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            value = self.get_db_prep_save(value)
            return super(PickledObjectField, self).get_db_prep_lookup(lookup_type, value)
        elif lookup_type == 'in':
            value = [self.get_db_prep_save(v) for v in value]
            return super(PickledObjectField, self).get_db_prep_lookup(lookup_type, value)
        else:
            raise TypeError('Lookup type %s is not supported.' % lookup_type)

        
class HTMLField(models.TextField):
    """ Field containing raw HTML, does not need to be filtered
    through <<safe>> when displayed in templates. """
    safe = True

    def __init__(self, *args, **kwargs):
        kwargs['blank'] = kwargs.get('blank', True)

        try:
            self.safe = kwargs["safe"]
        except KeyError:
            pass
        else:
            del(kwargs["safe"])

        super(HTMLField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value is None:
            return None
        if self.safe:
            value = mark_safe(value)
        return value


class __StdModel(models.Model):
    sort_initial_value = -1
    sort = models.SmallIntegerField(_(u"sort order"))
    date_created = models.DateTimeField(_(u"date created"), auto_now_add=True)
    date_changed = models.DateTimeField(_(u"date changed"), auto_now=True)
    is_active = models.BooleanField(_(u"is active"), default=True)

    manager = StdManager()

    class Meta:
        abstract = True


class StdModel(__StdModel):
    #site = models.ForeignKey(Site)

    class Meta:
        abstract = True


class StdSharedModel(__StdModel):
    #sites = models.ManyToManyField(Site)

    class Meta:
        abstract = True

class Language(models.Model):
    """ Language model for internationalization, follows the
        list of ISO 639-1 codes """
    code = models.CharField(_(u"code"), max_length=7) 
    name = models.CharField(_(u"name"), max_length=40) 

    class Meta:
        verbose_name = _(u"language")
        verbose_name_plural = _(u"languages")
    
    def __unicode__(self):
        return "%s (%s)" % (self.code, self.name)
