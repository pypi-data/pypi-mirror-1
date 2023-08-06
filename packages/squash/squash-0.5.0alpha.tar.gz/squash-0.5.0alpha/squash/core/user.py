from django.db import models
from django.contrib.auth.models import Group, User, AnonymousUser

import schema
from changeset import ChangesetManager, ref, json, unjson
from project import Project, Tag, format_date

### Users ###
def user_details(self, request):
    yield {
        'username': self.username,
        'is_authenticated': True
    }
    
    yield {
        'email': self.email,
        'is_active': self.is_active,
        'is_staff': self.is_staff,
        'is_superuser': self.is_superuser,
        'last_login': format_date(self.last_login),
        'date_joined': format_date(self.date_joined),
    }

def user_create(cls, details, request):
    self = cls.objects.create_user(details['username'], details.get('email', None), details.get('password', None))
    if details.get('project', None):
        self.groups.add( Project.objects.get(pk=details['project']).members )
    return self
    
def user_update(self, details, request):
    if details.get('password', None):
        self.set_password(details['password'])
    self.is_active = self.has_usable_password()
    
    return {
        'email': schema.lower, #TODO Add Email Validator
    }
    
def user_query(cls, request):    
    group = request.REQUEST.get('group', None)
    if (group):
        q = Group.objects.get(pk=group).user_set.all()
    else:    
        project = request.REQUEST.get('project', None)
        if (project):
            q = Project.objects.get(pk=project).members.user_set.all()
        else:
            q = User.objects.all()
    
    term = request.REQUEST.get('term', None)
    if term:
        q = q.filter(username__icontains=term)
    return q

def user_get(cls, username):
    try:
        return User.objects.get(username=username)
    except:
        return None

if not hasattr(User, 'details'):
    User.add_to_class('details', user_details)
    User.add_to_class('update', user_update)
    User.add_to_class('create', classmethod(user_create))
    User.add_to_class('query', classmethod(user_query))
    User.add_to_class('get', classmethod(user_get))

    User.add_to_class('ajax', ChangesetManager())

### Group ###
def group_details(self, request):
    yield {'name': self.name, 'slug': self.slug}
    
    count = self.user_set.count()
    if (count == 1):
        members = '%d member' % count
    else:
        members = '%d members' % count
    
    yield {
        'members': members,
        'locked': self.slug in ('members', 'managers')
    }

def group_create(cls, details, request):
    project = Project.objects.get(details['project'])
    self = project.group_set.create(slug=details['slug'], name=details.get['name'])
    return self
    
def group_update(self, details, request):
    return {
        'name': str,
        'slug': schema.slug,
    }

def group_query(cls, request):
    q = Group.objects.all()
    term = request.REQUEST.get('name', None)
    if term:
        q = q.filter(name__icontains=term) | q.filter(slug__icontains=term)
    project = request.REQUEST.get('project', None)
    if (project):
        q = q.filter(project=project)
    return q

if not hasattr(Group, 'details'):
    Group.add_to_class('details', group_details)
    Group.add_to_class('update', group_update)
    Group.add_to_class('create', classmethod(group_create))
    Group.add_to_class('query', classmethod(group_query))

    Group.add_to_class('ajax', ChangesetManager())

    Group.add_to_class('project', models.ForeignKey(Project, blank=True, null=True))
    Group.add_to_class('slug', models.SlugField())
    Group._meta.get_field_by_name('name')[0]._unique = False

### Permissions ###
class PermissionManager(models.Manager):
    def _may(self, project, user, key):
        if (user is None or isinstance(user, AnonymousUser)):
            return self.filter(project=project, user__isnull=True, group__isnull=True, key=key).count() > 0
            
        u = self.filter(project=project, user=user, key=key)
        g = self.filter(project=project, group__user=user, key=key)
        return (u | g).count() > 0
    
    def may(self, project, user, key):
        if (user.is_superuser):
            return True
            
        if user.is_authenticated():
            user = None
        
        if ':' in key:   # See if we're allowed to edit anything '*'.
            first, second = key.split(':', 1)
            if self._may(project, user, '%s:*' % first):
                return True
        return self._may(project, user, key)
    
    def allow(self, project, who, key):
        if isinstance(who, User):
            p, created = self.get_or_create(project=project, user=who, key=key)
            if (created): p.save()
        elif isinstance(who, Group):
            p, created = self.get_or_create(project=project, group=who, key=key)
            if (created): p.save()
        elif who is None or not who.is_authenticated():
            p, created = self.get_or_create(project=project, key=key)
            if (created): p.save()
        else:
            raise RuntimeError("'who' not set to User or Group instance: %r" % who)

    def disallow(self, project, who, key):
        if isinstance(who, User):
            self.filter(project=project, user=who, key=key).delete()
        elif isinstance(who, Group):
            self.filter(project=project, group=who, key=key).delete()
        elif who is None or not who.is_authenticated():
            self.filter(project=project, key=key, user__isnull=True, group__isnull=True).delete()
        else:
            raise RuntimeError("'who' not set to User or Group instance: %r" % who)
            
    def what_is_allowed(self, project, user):
        if user is None or not user.is_authenticated():
            permissions = self.filter(project=project, user__isnull=True, group__isnull=True)
        else:
            u = self.filter(project=project, user=user)
            g = self.filter(project=project, group__user=user)
            permissions = (u | g)
        
        keys = {}
        star = {}
        for p in permissions:
            key = p.key
            if ':' in key:
                one, two = key.split(':', 1)
                if (two == '*'):
                    star[one] = True
                    continue
                if one in star:
                    continue
            keys[key] = True
        stars = star.keys()
        stars.sort()
        stars = ['%s:*' % k for k in stars]
        keys = keys.keys()
        keys.sort()
        return stars + keys
        
class Permission(models.Model):
    project = models.ForeignKey(Project)
    key = models.CharField(max_length=255)
    group = models.ForeignKey(Group, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    
    objects = PermissionManager()
    
    def __unicode__(self):
        if (self.user_id):
            return "%r may %r" % (self.user, self.key)
        else:
            return "%r may %r" % (self.group, self.key)

### Module Functions ###
def may(project, who, key):
    return Permission.objects.may(project, who, key)

def allow(project, who, key):
    return Permission.objects.allow(project, who, key)

def disallow(project, who, key):
    return Permission.objects.disallow(project, who, key)

def what_is_allowed(project, user):
    return Permission.objects.what_is_allowed(project, user)
    
def get_members(project):
    if not hasattr(project, '_members'):
        project._members = project.group_set.get(slug='members')
    return project._members

def get_managers(project):
    if not hasattr(project, '_managers'):
        project._managers = project.group_set.get(slug='managers')
    return project._managers

### Tack-On ###
Project.add_to_class('may', may)
Project.add_to_class('allow', allow)
Project.add_to_class('disallow', disallow)
Project.add_to_class('what_is_allowed', what_is_allowed)
Project.add_to_class('members', property( get_members ))
Project.add_to_class('managers', property( get_managers ))

### Hookups ###
from django.db.models import signals
from django.conf import settings

def default_project_groups(instance=None, created=False, **ka):
    if not created: return
    
    # Anonymous can see anyone:
    try:
        instance.allow(None, 'view:*')
    except:
        return
    
    managers = instance.group_set.create(slug='managers', name='Managers')
    instance.allow(managers, 'view:*')
    instance.allow(managers, 'create:*')
    instance.allow(managers, 'update:*')
    instance.allow(managers, 'delete:*')
    
    if (instance.owner):
        instance.owner.groups.add(managers)
    
    members = instance.group_set.create(slug='members', name='All Members')
    instance.allow(members, 'view:*')
    instance.allow(members, 'create:ticket')
    instance.allow(members, 'update:ticket')
    instance.allow(members, 'delete:ticket')
    
    if (instance.owner):
        instance.owner.groups.add(members)

signals.post_save.connect(default_project_groups, sender=Project)

def default_project_groups_for_all(app=None, **ka):
    for instance in Project.objects.all():
        default_project_groups(instance=instance)

signals.post_syncdb.connect(default_project_groups_for_all)