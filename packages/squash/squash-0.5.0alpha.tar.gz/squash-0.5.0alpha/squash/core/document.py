from datetime import datetime

from django.db import models
from django.contrib.auth import models as auth

import schema
import creole
from changeset import ChangesetManager, ref

from project import Project, format_date

class Document(models.Model):
    project = models.ForeignKey(Project)
    slug = models.SlugField(max_length=255)
    special = models.BooleanField(default=False)
    
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    author = models.ForeignKey(auth.User, blank=True, null=True)
    src = models.TextField(blank=True)

    def __repr__(self):
        return self.slug

    def __str__(self):
        return self.slug

    def get_url(self):
        return "/%s/%s/" % (self.project.slug, self.slug)
    
    def details(self, context=None):
        # Ref
        yield {'slug': self.slug}
        
        yield {
            'project': ref( self.project ),
            'project_pk': self.project.slug,
            'author': self.author.username,
            'modified': format_date(self.modified, "M jS \\a\\t P"),
            'src': self.src,
            'html': creole.convert(self.src),
            'permissions': {
                'update': self.project.may( context.user, 'update:document' ),
                'delete': self.project.may( context.user, 'delete:document' ),
            },
        }
    
    def update(self, details, context=None):
        return {
            'project': Project.get,
            'slug': schema.slug,
            'src': unicode,
            'author': schema.Default(auth.User.get, context.user),
        }
    
    @classmethod
    def query(cls, context):
        project = context.REQUEST.get('project', None)
        q = cls.objects.all()
        if (project):
            q = q.filter(project=project)
        return q

    objects = ChangesetManager()
    
    class Meta:
        ordering = ('special', 'modified')
        unique_together = ("project", "slug")