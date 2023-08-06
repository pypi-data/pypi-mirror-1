# 
# from django.utils import simplejson
# from django.db import models as django_models
# 
# class JSONField(django_models.Field):
#     __metaclass__ = django_models.SubfieldBase
# 
#     MAGIC = "JSON"
# 
#     def to_python(self, value):
#         if isinstance(value, basestring) and value.startswith(self.MAGIC):
#             value = simplejson.loads(value[len(self.MAGIC):])
# 
#         return value
# 
#     def get_db_prep_save(self, value):
#         return self.MAGIC + simplejson.dumps(value)
#     
#     def get_internal_type(self): 
#         return 'TextField'
#     
#     def get_db_prep_lookup(self, lookup_type, value):
#         if lookup_type == 'exact':
#             value = self.get_db_prep_save(value)
#             return super(JSONField, self).get_db_prep_lookup(lookup_type, value)
#         elif lookup_type == 'in':
#             value = [self.get_db_prep_save(v) for v in value]
#             return super(JSONField, self).get_db_prep_lookup(lookup_type, value)
#         else:
#             raise TypeError('Lookup type %s is not supported.' % lookup_type)

import datetime
from django.db import models
from django.db.models import signals
from django.conf import settings
from django.utils import simplejson as json
from django.dispatch import dispatcher

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.time):
            return obj.strftime('%H:%M:%S')
        return json.JSONEncoder.default(self, obj)
        
def dumps(data):
    return JSONEncoder().encode(data)
    
def loads(str):
    return json.loads(str, encoding=settings.DEFAULT_CHARSET)
    
class JSONField(models.TextField):
    def db_type(self):
        return 'text'
        
    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        return dumps(value)
    
    def contribute_to_class(self, cls, name):
        super(JSONField, self).contribute_to_class(cls, name)
        dispatcher.connect(self.post_init, signal=signals.post_init, sender=cls)
        
        def get_json(model_instance):
            return dumps(getattr(model_instance, self.attname, None))
        setattr(cls, 'get_%s_json' % self.name, get_json)
    
        def set_json(model_instance, json):
            return setattr(model_instance, self.attname, loads(json))
        setattr(cls, 'set_%s_json' % self.name, set_json)
    
    def post_init(self, instance=None):
        value = self.value_from_object(instance)
        if (value):
            setattr(instance, self.attname, loads(value))
        else:
            setattr(instance, self.attname, None)
