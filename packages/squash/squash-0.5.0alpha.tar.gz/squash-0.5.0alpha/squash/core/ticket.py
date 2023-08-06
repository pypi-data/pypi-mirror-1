from django.db import models
from django.contrib.auth import models as auth
from django.conf import settings

import schema
import creole
from changeset import ChangesetManager, ref, json, unjson, get_delegate
from project import Project, Tag, format_date

class Folder(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    project = models.ForeignKey(Project)
    
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('slug', 'created')
        unique_together = ('slug', 'project')

    def __str__(self):
        return self.name
        
    def details(self, context=None):
        yield { 'slug': self.slug, 'name': self.name }
        
        if (self.start and self.end):
            dates = "Starts: %s | Ends: %s" % (format_date(self.start), format_date(self.end))
        elif (self.start):
            dates = "Starts: %s" % format_date(self.start)
        elif (self.end):
            dates = "Ends: %s" % format_date(self.end)
        else:
            dates = "Persistant"
        outstanding = self.ticket_set.filter(state='open').count()
        if (outstanding == 1): outstanding = "%d outstanding" % outstanding
        else: outstanding = "%d outstanding" % outstanding
        
        yield {
            'project': ref( self.project ),
            'creator': self.creator.username,
            'start': format_date(self.start),
            'end': format_date(self.end),
            'dates': dates,
            'outstanding': outstanding,
            'permissions': {
                'update': self.project.may( context.user, 'update:folder' ),
                'delete': self.project.may( context.user, 'delete:folder' ),
            },
        }
        
        yield {
            'userpool': [ref( u ) for u in User.objects.all()]
        }
        
    def change_project(self, project):
        if not self.id:
            self.project = project
            return  
        if (project != self.project):
            self.project = project
            for ticket in self.ticket_set.all():
                ticket.project = project
                ticket.save()

    def update(self, details, context=None):
        if self.is_locked():
            return
        
        self.creator = context.user
            
        return {
            'name': str,
            'slug': schema.slug,
            'project': get_delegate(Project, 'slug'),
        }

    @classmethod
    def query(cls, request):
        project = request.REQUEST.get('project', None)
        q = cls.objects.all()
        if (project):
            q = q.filter(project=project)
        if ('term' in request.REQUEST):
            q = q.filter(name__icontains=request.REQUEST['term'])
        return q

    objects = ChangesetManager()

class Ticket(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(auth.User)
    
    parent = models.ForeignKey("self", blank=True, null=True)
    
    state = models.ForeignKey(Tag, blank=True, null=True)
    project = models.ForeignKey(Project)
    folder = models.ForeignKey(Folder, blank=True)
    group = models.ForeignKey(auth.Group, null=True, blank=True, related_name='assigned')
    user = models.ForeignKey(auth.User, null=True, blank=True, related_name='assigned')
    
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    description = models.TextField(blank=True)
    
    objects = ChangesetManager()
    
    def __str__(self):
        if self.id:
            return "#%d - %s" % (self.id, self.name)
        else:
            return ":new - %s" % self.name
        
    def get_url(self):
        return "/%s/" % self.slug
    
    def details(self, request=None):
        # Ref
        yield {'name': self.name}
        
        print self.project_id
        
        # Summary
        if (self.user):
            owner = ref( self.user )
        else:
            owner = {'username': '<em>unassigned</em>'}
        yield {
            'project': ref( self.project ),
            'folder': ref( self.folder ),
            'state': ref( self.state ),
            
            'creator': ref( self.creator ),
            'parent': ref( self.parent ),
            'created': self.created,
            'modified': self.modified,
            
            'owner': owner,
            
            'description': self.description,
            
            'permissions': {
                'update': self.project.may( request.user, 'update:ticket' ),
                'delete': self.project.may( request.user, 'delete:ticket' ),
            },
        }
    
    def change_folder(self, folder):
        if (folder == None):
            folder = self.project.get_default_folder()
        self.folder = folder
        self.project = self.folder.project
    
    def update_relation(self, details, key, model, attr=None):
        if (attr is None): attr = key
        if (key in details):
            if ('pk' not in details[key] or details[key]['pk'] is None):
                return setattr(self, attr, None)
            setattr(self, attr, model.objects.get(pk=details[key]['pk']))
    
    def update(self, details, request=None):
        self.creator = request.user
        
        return {
            'name': str,
            'description': str,
            'folder': get_delegate(Folder, 'pk'),
            'project': get_delegate(Project, 'slug'),
            'state': get_delegate(Tag, 'slug'),
            ('owner', 'user'): get_delegate(auth.User, 'username'),   #Meaning, get 'owner' from details, but assign it as 'user'.
        }

    def validate(self):
        errors = super(Ticket, self).validate()
        return errors

    @classmethod
    def query(cls, request):
        q = cls.objects.all()
        
        params = request.REQUEST
        
        if ('user' in params):
            q = q.filter(user__pk=params['user'])
        if ('project' in params):
            q = q.filter(project=params['project'])
        if ('folder' in params):
            q = q.filter(folder=params['folder'])
        if ('term' in params):
            q = q.filter(name__icontains=params['term']) | q.filter(description__icontains=params['term'])
        
        if params.get('outstanding'):
            q = q.filter(state__slug__in=settings.TICKET_OUTSTANDING)
        
        return q.order_by('-state')
    
    def save(self):
        if not self.state:
            self.state, _ = Tag.objects.get_or_create(slug='open', name='Open')
        if not self.folder_id:
            self.folder = self.project.get_default_folder()
        models.Model.save(self)

class Comment(models.Model):
    ticket = models.ForeignKey(Ticket)
    author = models.ForeignKey(auth.User)
    text = models.TextField()
    
    created = models.DateTimeField(auto_now_add=True)
    objects = ChangesetManager()
    
    def details(self, request=None):
        yield {}
        
        yield {
            'ticket': ref( self.ticket ),
            'author': self.author.username,
            'created': format_date(self.created),
            'text': self.text,
        }
    
    def update(self, details, request=None):
        self.author = request.user
        
        return {
            'text': schema.Default(str, ''),
            'ticket': Ticket.get
        }
    
    @classmethod
    def query(cls, request):
        params = request.REQUEST
        return cls.objects.filter(ticket=params.get('ticket'))

    class Meta:
        ordering = ('-created',)

### Hookups ###
from django.db.models import signals

def default_project_folders(instance=None, created=False, **ka):
    if not created: return
    for slug, name in instance.settings.get('folders', ()):
        instance.folder_set.get_or_create(slug=slug, name=name)

signals.post_save.connect(default_project_folders, sender=Project)

def default_state_tags(instance=None, created=False, **ka):
    if not created: return
    for slug, name in instance.settings.get('states', ()):
        Tag.objects.get_or_create(name=name, slug=slug)

signals.post_save.connect(default_state_tags, sender=Project)