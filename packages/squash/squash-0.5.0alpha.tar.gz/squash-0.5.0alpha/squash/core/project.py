import re
re_slug = re.compile('^[\w-]+$')

from django.db import models
from django.contrib.auth import models as auth

import schema
from changeset import ChangesetManager, ref, json, unjson, get_delegate

### Project Templates ###
templates = {
    'agile': {
        'folders': [('product', 'Product Backlog'), ('sprint', 'Sprint Backlog')],
        'states': [('open', 'Open'), ('complete', 'Complete'), ('verified', 'Verified')],
        'outstanding': ['open'],
        'terms': {
            'folder': ['sprint', 'release'],
            'ticket': [('story', 'stories'), 'task'],
        },
    },
    'tracker': {
        'folders': [('ongoing', 'Ongoing')],
        'states': [('open', 'Open'), ('wont-fix', 'Won\'t Fix'), ('invalid', 'Invalid'), ('closed', 'Closed')],
        'outstanding': ['open'],
        'terms': {
            'folder': ['milestone', 'release'],
            'ticket': ['ticket'],
        },
    }
}

### Classes ###
class Project(models.Model):
    slug = models.SlugField(primary_key=True)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(auth.User)
    
    description = models.TextField(blank=True)
    settings_cache = models.TextField(default='{}')
    
    active = models.BooleanField(default=True)
    
    objects = ChangesetManager()
    
    def __repr__(self):
        return self.slug
    
    def __str__(self):
        return self.name
        
    def get_url(self):
        return "/%s/" % self.slug
    
    def details(self, request=None):
        # Ref
        yield {
            'slug': self.slug,
            'name': self.name,
            'description': self.description,
            'active': self.active,
        }
        
        # Summary
        yield {
            'members': [ref( x ) for x in self.members.user_set.all()],
            'permissions': dict((x, True) for x in self.what_is_allowed(request.user)),
            'settings': self.settings,
            'owner': ref( self.owner ),
        }
        
    def update(self, details, request=None):
        if not self.slug:
            details['settings'] = templates[details.get('type', 'agile')]
        
        return {
            'slug': schema.slug,
            'name': str,
            'description': str,
            'settings': dict,
            'owner': schema.Default(get_delegate(auth.User, 'username'), request.user),
            'active': bool,
        }
    
    def validate(self):
        print "Validating", self.slug
        errors = super(Project, self).validate()
        if not re_slug.match(self.slug):
            print "Not working..."
            errors.setdefault('slug', []).append('This field must be only lowercase letters and the "-" symbol.')
        return errors
    
    @classmethod
    def query(cls, request=None):
        from django.conf import settings
        
        query = cls._default_manager.all();
        
        if not request.REQUEST.get('browse', True) and request.user.is_authenticated():
            query = query   #TODO: fix.
        
        term = request.REQUEST.get('term', '').strip()
        if (term):
            if (settings.DATABASE_ENGINE == 'mysql'):
                query = query.filter(name__search=term) | query.filter(description__search=term)
            else:
                query = query.filter(name__icontains=term) | query.filter(description__icontains=term)
        
        return query
    
    def get_default_folder(self):
        return self.folder_set.filter()[0]
    
    def get_settings(self):
        if not hasattr(self, '_settings'):
            self._settings = unjson(self.settings_cache or '{}')
        return self._settings
    
    def set_settings(self, settings):
        self._settings = settings
    
    settings = property(get_settings, set_settings)
    
    def get_default_ticket_state(self):
        t, _ = Tag.objects.get_or_create(slug=self.settings['states'][0][0])
        return t
    
    def save(self, **kw):
        if hasattr(self, '_settings'):
            self.settings_cache = json(self._settings)
        models.Model.save(self, **kw)
        
    @classmethod
    def new(cls, slug=None, name=None, description='', template='agile', owner=None):
        if (not slug):
            slug = schema.slug(name)
        
        project = Project(slug=slug, name=name)
        project.description = description
        project.settings = templates[template]
        project.owner = owner
        project.save()
        return project

class Tag(models.Model):
    slug = models.SlugField(primary_key = True)
    name = models.CharField(max_length=255)

    objects = ChangesetManager()
        
    def __str__(self):
        return self.name

    def __repr__(self):
        return self.slug
        
    def details(self, request=None):
        yield {'slug': self.slug, 'name': self.name}
        
    def update(self, details, request=None):
        return {'slug': schema.slug, 'name': str}

### Dates ###
from django.utils.dateformat import DateFormat

def format_date(date, format='F jS', default=''):
    if (date):
        return DateFormat(date).format(format)
    else:
        return default