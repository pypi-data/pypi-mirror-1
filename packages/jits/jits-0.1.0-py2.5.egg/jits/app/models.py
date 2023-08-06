import uuid
import pickle
from datetime import datetime

from django.db import models

class UUIDField(models.CharField):
    def __init__(self, version=None, node=None, clock_seq=None, namespace=None, name=None, **kwargs):
        kwargs['max_length'] = 36
        kwargs['blank'] = True
        kwargs['unique'] = True
        self.version = version
        if version==1:
            self.node, self.clock_seq = node, clock_seq
        elif version==3 or version==5:
            self.namespace, self.name = namespace, name
        models.CharField.__init__(self, **kwargs)

    def get_internal_type(self):
        return "CharField"      

    def pre_save(self, model_instance, add):
        def do(self, model_instance, add):
            if add:
                if not self.version or self.version==4:
                    return unicode(uuid.uuid4())
                elif self.version==1:
                    return unicode(uuid.uuid1(self.node, self.clock_seq))
                elif self.version==3:
                    return unicode(uuid.uuid3(self.namespace, self.name))
                elif self.version==5:
                    return unicode(uuid.uuid5(self.namespace, self.name))
            else:
                return super(UUIDField, self).pre_save(model_instance, add)
        result = do(self, model_instance, add)
        model_instance.uuid = result
        return result
        
# Code from http://www.djangosnippets.org/snippets/513/        
        
class PickledObject(str):
	"""A subclass of string so it can be told whether a string is
	   a pickled object or not (if the object is an instance of this class
	   then it must [well, should] be a pickled one)."""
	pass
	
class FunctionObject(object):
    def __init__(self, func):
        self.func = func
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)   

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

class Task(models.Model):
    uuid = UUIDField()
    name = models.CharField(max_length=300, null=True, default=None)
    running = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)
    callback = PickledObjectField()
    next_run = models.DateTimeField(default=datetime.now())
    frequency_days    = models.IntegerField(default=0)
    frequency_hours   = models.IntegerField(default=0)
    frequency_minutes = models.IntegerField(default=0)
    frequency_seconds = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'jits_app_task'
    
