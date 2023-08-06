from base import *

class Project(Command):
    """Project manipulation."""
    name = 'project'
    usage = '(slug | name | :new | :current)'
    
    option_list = [
        make_option("-e", "--edit", action="store_true", dest="edit"),
        make_option("-x", "--delete", action="store_true", dest="delete"),
        make_option("-d", "--description", action="store", type="string", dest="description", default=None),
        make_option("-s", "--slug", action="store", type="string", dest="slug", default=None),
        make_option("-n", "--name", action="store", type="string", dest="name", default=None),
        make_option("-t", "--type", action="store", type="string", dest="type", default='agile'),
        make_option("--inactive", action="store_false", dest="active"),
        make_option("--active", action="store_true", dest="active", default=True),
        make_option("--noinput", action="store_true", dest="noinput"),
    ]
    
    def yaml(self, project):
        parts = [
            'slug:    %s' % project.slug,
            'name:    %s' % project.name,
            'description: \n  %s\n' % project.description,
        ]
        if not project.active:
            parts.insert(2, "active:  False")
            
        return "\n".join(parts)
    
    def execute(self):
        from changeset import update
        
        try:
            project = self.find_project(self.args[0])
        except ObjectDoesNotExist:
            raise CommandError("Cannot find project %r." % self.args[0])
        except IndexError:
            print self.parser.print_usage()
            return
        
        if self.options.delete:
            return self.delete(project, self.options.noinput)
        
        if not project.pk:
            if not self.options.slug:
                if self.options.name:
                    self.options.slug = schema.slug(self.options.name)
                else:
                    self.options.edit = True
        
        details = {
            'name': self.options.name,
            'slug': self.options.slug,
            'description': self.options.description,
            'active': self.options.active
        }
        
        update(project, clean(details), self)
        
        if (self.options.edit):
            details.update( self.edit( project ) )
            update(project, details, self)
        
        project.save()
        self.set_project(project)
        
        print self.yaml(project)
        
    def edit(self, instance):
        from squash.changeset import update
        
        src = self.yaml(instance)
        src_hash = hash(src)

        src = self.edit_src(src, '/tmp/squash-project-%s' % random_key())

        if hash(src) == src_hash:
            raise CommandError('No changes made.')

        details = yaml.load(src)
        return details
    
    def delete(self, instance, noinput):
        if not noinput:
            try:
                confirm = raw_input("Enter 'delete' to confirm deleting the project '%s': \n   " % instance.name)
            except:
                confirm = None
        else:
            confirm = 'delete'
        
        if confirm == 'delete':
            instance.delete()
            print "Project %s was deleted." % instance.name
        else:
            raise CommandError("\nAborted")
    
Command.all.append(Project)


class ListProjects(Command):
    """Lists all the projects."""
    name = 'projects'
    usage = ""
    
    option_list = [
        make_option('-a', "--all", action="store_true", dest="all", default=False),
    ]
    
    def execute(self):
        from squash.core.models import Project
        
        if self.options.all:
            projects = Project.objects.all().order_by('slug')
        else:
            projects = Project.objects.filter(active=True).order_by('slug')
        if projects.count() == 0:
            print "No projects found."
        else:
            for project in projects:
                print project.slug

Command.all.append(ListProjects)