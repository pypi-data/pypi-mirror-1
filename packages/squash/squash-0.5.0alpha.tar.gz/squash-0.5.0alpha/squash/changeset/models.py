from uuid import uuid4
from datetime import datetime

from django.db import models
from django.contrib.auth import models as auth
from django.db.models import signals

from ajax import json, unjson
import schema

def uuid():
    # TODO: Need to provide an alternative if this doesn't exist (pre 2.5)
    return str(uuid4())
    
### Classes ###
class Changeset(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid)
    username = models.CharField(max_length=255)
    desc = models.CharField(max_length=255)
    
    created = models.DateTimeField(default=datetime.now)
    
    target = models.CharField(max_length=255)
    data = models.TextField(default='{}')
    
    def __repr__(self):
        return '<Changeset %s>' % self.desc
    
    def __str__(self):
        return self.desc

class ChangesetManager(models.Manager):
    def contribute_to_class(self, model, name):
        super(ChangesetManager, self).contribute_to_class(model, name)
        
        signals.pre_save.connect(self.save_changeset, sender=model)
        model.add_to_class('uuid', models.CharField(max_length=36, default=None, null=True))
    
    def save_changeset(self, instance=None, created=False, **ka):
        if hasattr(instance, '_changeset'):
            instance._changeset.data = json(instance._changeset.data)
            instance._changeset.save()
            del instance._changeset