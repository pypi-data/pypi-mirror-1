"""
    Unused ideas that I'd like to keep around.
"""

class Pull(Command):
    """Pull a squash project from a specific url or file path, creating a clone or updating the current project."""
    name = 'pull'
    usage = "[options] path-or-url"
    option_lst = Command.option_list
    
    def execute(self):
        print "Pulling changes from %s to this project..." % self.args[0]

Command.all.append(Pull)

class Push(Command):
    """Push changes from the local project to another url or file path."""
    name = 'push'
    usage = "[options] path-or-url"
    option_lst = Command.option_list
    
    def execute(self):
        print "Pushing changes from this project to %s..." % self.args[0]

Command.all.append(Push)

class Create(Command):
    """Create a new project."""
    name = 'create'
    usage = "name [options]"
    
    option_list = [
        make_option("-d", "--description", action="store", type="string", dest="description", default=''),
        make_option("-s", "--slug", action="store", type="string", dest="slug", default=''),
        make_option("-t", "--type", action="store", type="string", dest="type", default='agile')
    ]
    
    def execute(self):
        from squash.core.models import Project
        
        project = Project.new(
            name=self.args[0], 
            slug=self.options.slug,
            description=self.options.description,
            template=self.options.type,
            owner=self.get_user())
            
        self.set_project(project)
        print project.yaml()

Command.all.append(Create)

class Drop(Command):
    """Drop a project."""
    name = 'drop'
    usage = 'name'
    
    def execute(self):
        project = self.find_project(self.args[0])
        if not project:
            print "Project not found: %s" % self.args[0]
            return
        
        try:
            confirm = raw_input("Enter 'delete' to confirm deleting the project '%s': \n   " % project.name)
        except:
            confirm = None
        
        if confirm == 'delete':
            project.delete()
            print "Project %s was deleted." % project.name
        else:
            print "\nAborted"
        
Command.all.append(Drop)

import yaml, os, random
from squash.changeset import update
from django.db import loading

def edit(instance):
    if not project:
        print "Project not found: %s" % self.args[0]
        return
    
    src = project.yaml()
    src_hash = hash(src)
    filename = '/tmp/squash-%s-edit' % ''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(8)])
    
    o = open(filename, 'w')
    o.write(src)
    o.close()
    
    result = os.system('%s %s' % (os.environ['EDITOR'], filename))
    
    o = open(filename)
    src = o.read()
    o.close()
    
    if os.path.exists(filename):
        os.unlink(filename)
        
    if (result != 0):
        print "Aborted"
        return
    
    if hash(src) == src_hash:
        print 'No changes made.'
        return
    
    details = yaml.load(src)
    if details.get('description', None) is None:
        details['description'] = ''
    
    class context:
        user = self.get_user()
    
    update(project, details, context)
    src = project.yaml()
    if hash(src) == src_hash:
        print 'No changes made.'
        return
        
    project.save()
    print src