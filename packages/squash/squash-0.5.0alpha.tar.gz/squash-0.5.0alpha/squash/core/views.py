from django.contrib.auth import logout as _logout
from django.contrib.auth import login as _login
from django.contrib.auth import authenticate
from django.conf import settings
from django.db.models import loading
from django.shortcuts import render_to_response
from django.conf import settings

from ajax import json, unjson, ajax
from changeset import details, ref, info, update

from models import User, Project

### Support ###
def create_anonymous_user():
    return {
        '_model': 'auth.AnonymousUser',
        '_pk': ':anonymous',
        'username': 'Anonymous',
        'is_authenticated': False,
    }

def render(request, template, *a, **ka):
    """ Helper function for rendering. """
    context = {'request': request, 'template': template}
    for dict in a:
        context.update(dict)
    context.update(ka)
    return render_to_response(template, context)


### Views ###
def index(request):
    title = 'App Index'
    
    media = settings.MEDIA_URL
    allow_anonymous = settings.ALLOW_ANONYMOUS
    allow_registration = settings.ALLOW_REGISTRATION
    
    if (request.user.is_authenticated()):
        user = details( request.user, request )
    else:
        user = create_anonymous_user()
    
    try:
        project = details( Project.objects.get(), request )
    except (Project.DoesNotExist, Project.MultipleObjectsReturned), e:
        project = None
    
    actors = [('-- select a user --', None)] + [(x.username, x.username) for x in User.query(request)]
    
    return render(request, 'index.html', locals())

@ajax
def login(request):
    """ Ajax login. """
    user = authenticate(username=request.REQUEST['username'], password=request.REQUEST['password'])
    if (not user):
        return create_anonymous_user()
    _login(request, user)
    print details(user, request)
    return details(user, request)

@ajax
def logout(request):
    """ Ajax logout. """
    try:
        _logout(request)
    except IndexError:
        pass
    return create_anonymous_user()

@ajax
def search(request, model=None):
    if isinstance(model, basestring):
        model = loading.get_model(*model.split('.'))
    
    if hasattr(model, 'query'):
        query = model.query(request)
    else:
        query = self.all()
    
    get = request.REQUEST.get('get', None)
    if (get):
        return [ details( i, request, get=get ) for i in query]
    else:
        return [ info( i, request ) for i in query]

@ajax
def handle(request, model=None):
    if isinstance(model, basestring):
        model = loading.get_model(*model.split('.'))
        
    method = request.method.lower()
    assert method in ('get', 'post', 'delete'), "DELETE, GET or POST to this resource."
    
    if (method == 'get'):
        pk = request.GET['pk']
        instance = self.get(pk=pk)
    
    if (method == 'delete' or (method == 'get' and request.GET.get('action', None) == 'delete')):
        self._audit(request, 'delete', instance)
        instance.delete()
        return True
    
    if (method == 'post'):
        pk = request.POST.get('pk', None)
        value = unjson(request.POST.get('value'))
        if (pk):
            instance = self.get(pk=pk)
            errors = update(instance, value, request)
            self._audit(request, 'update', instance, value)
        else:
            instance = model()
            errors = update(instance, value, request)
            self._audit(request, 'create', instance, value)
        
        if (errors):
            return {'__failure__': errors}
        instance.save()
    
    audit(request, 'view', instance)
    
    get = request.REQUEST.get('get', None)
    value = details(instance, request, get=get)
    return {'pk': instance._get_pk_val(), 'model': 'auth.User', 'value': value}

def audit(self, request=None, action=None, instance=None, value=None):
    from squash.core.models import Project
    
    if isinstance(instance, Project):
        project = instance
    else:
        project = getattr(instance, 'project', None)
    if (project):
        name = instance.__class__.__name__.lower()
        if not project.may(request.user, "%s:%s" % (action, name)):
            raise Forbidden


### Default Tags/Filters ###
from django.template import defaultfilters, mark_safe

def json_filter(value):
    return mark_safe(json(value))
json_filter.is_safe = True
defaultfilters.register.filter('json', json_filter)


### Store ###
from django.db.models import get_model

# TODO: This could be faster, by getting the objects in bulk per model.
def get_delegate(ref):
    Model = get_model(*ref['model'].split('.', 1))
    return Model._default_manager.get(pk=ref['pk'])

@ajax
def store(request, name):
    if request.POST:
        request.session[name + '-store'] = unjson(request.POST['value'])
        return True
    if name == 'trash' and request.GET.get('action', None) == 'empty':
        trash = request.session.get('trash-store', [])
        for ref in trash:
            get_delegate(ref).delete()
        request.session['trash-store'] = []
        return []
    else:
        store = request.session.get(name + '-store', [])
        return [info( get_delegate(x), request ) for x in store]