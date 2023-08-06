from schema import DictSchema
from ajax import json
from models import Changeset, uuid

def get_model_sig(instance):
    return instance._meta.app_label + '.' + instance.__class__.__name__

def details(instance, context=None, get=None):
    """
    Loops through the generated details of a model instance.
    - 'context' optionally specifies the context that the details()
      function of the instance will recieve as its argument.
    - If 'get' is specified, it will loop only until that key appears.
    """
    
    if instance is None: return None
    result = {
        '_pk': instance.pk,
        '_model': get_model_sig(instance),
    }
    for dct in instance.details(context):
        result.update(dct)
        if get and get in result:
            break
    
    return result

def ref(instance, context=None):
    return {
        '_pk': instance.pk,
        '_model': get_model_sig(instance),
    }

def info(instance, context=None):
    return instance.details(context).next()

def get_delegate(model, key):
    def get(value):
        return model.objects.get(**{key: value})
    return get

def update(instance, value, context=None):
    schema = instance.update(value, context)
    
    if not instance.uuid:
        instance.uuid = uuid()
    
    changeset = Changeset(
        username = context.user.username,
        desc = getattr(context, 'desc', 'Update to %r by %s' % (instance, context.user.username)),
        target = "%s|%s" % (get_model_sig(instance), instance.uuid),
        data = value
    )
    
    if schema:
        schema = DictSchema(schema, all_optional=True)
        for k, v in schema(value).items():
            setattr(instance, k, v)
    
    instance._changeset = changeset