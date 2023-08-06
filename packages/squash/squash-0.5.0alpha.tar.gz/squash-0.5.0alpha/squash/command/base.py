import sys, os, yaml
from optparse import OptionParser, make_option
from django.core.exceptions import ObjectDoesNotExist
from squash import schema

def clean(dict):
    for k, v in dict.items():
        if v is None:
            del dict[k]
    return dict

class CommandError(Exception):
    pass

class Command(object):
    name = ''
    usage = ''
    description = ""
    
    option_list = [
        make_option("-f", "--filename",
                    action="store", type="string", dest="filename"),
        make_option("-q", "--quiet",
                    action="store_false", dest="verbose"),
    ]
    
    def __init__(self):
        self.parser = OptionParser(
            usage = "usage: %%prog %s %s" % (self.name, self.usage), 
            option_list = self.option_list, 
            description = self.description,
        )
        
    def parse(self, args=None):
        if args is None:
            args=sys.argv[2:]
        self.options, self.args = self.parser.parse_args(args=args)
    
    def execute(self):
        raise NotImplementedError()
        
    def sync_db(self):
        from django.core.management.commands.syncdb import Command
        Command().handle_noargs(verbosity=0, interactive=False)
    
    all = []
    @classmethod
    def resolve(self, arg):
        for cls in self.all:
            if cls.name.startswith(arg):
                return cls
        return None
    
    def set_project(self, project):
        from squash import settings

        slug = project.slug
        os.environ['SQUASH_PROJECT'] = slug
        o = open(os.path.abspath(os.path.join(settings.SQUASH_HOME, '.project')), 'w')
        o.write(slug)
        o.close()
    
    def find_project(self, q):
        from squash.core.models import Project
        
        if (q == ':new'):
            self.sync_db()
            return Project(owner=self.user)
        
        if (q == None):
            raise Project.DoesNotExist
        
        searches = [
            Project.objects.filter(slug__iexact=q),
            Project.objects.filter(slug__istartswith=q),
            Project.objects.filter(name__iexact=q),
            Project.objects.filter(name__istartswith=q),
            Project.objects.filter(name__icontains=q),
        ]
        
        for query in searches:
            try:
                return query[0]
            except IndexError:
                continue
        
        raise Project.DoesNotExist
    
    def find_folder(self, q):
        from squash.core.models import Folder
        
        try:
            project = self.get_current_project()
        except Project.DoesNotExist:
            raise CommandError("Cannot find project.")
        
        if (q == ':new'):
            return Folder(project=project)
        
        if (q == None):
            raise Folder.DoesNotExist
        
        searches = [
            project.folder_set.filter(slug__iexact=q),
            project.folder_set.filter(slug__istartswith=q),
            project.folder_set.filter(name__iexact=q),
            project.folder_set.filter(name__istartswith=q),
            project.folder_set.filter(name__icontains=q),
        ]
        
        for query in searches:
            try:
                return query[0]
            except IndexError:
                continue
        
        raise Project.DoesNotExist
    
    def find_ticket(self, q):
        from squash.core.models import Ticket, Project
        
        if (q == ':new'):
            try:
                project = self.get_current_project()
            except Project.DoesNotExist:
                raise CommandError("Cannot find project.")
        
            ticket = Ticket(project=project)
            ticket.folder = ticket.project.get_default_folder()
            ticket.state = ticket.project.get_default_ticket_state()
            return ticket
                
        return Ticket.objects.get(pk=q)
    
    def get_current_project(self):
        from squash import settings
        from squash.core.models import Project
        
        if hasattr(self.options, 'project') and self.options.project:
            return self.find_project(self.options.project)
        
        def search():
            yield Project.objects.filter(pk=os.environ.get('SQUASH_PROJECT', None))
            
            path = os.path.abspath(os.path.join(settings.SQUASH_HOME, '.project'))
            if os.path.exists(path):
                yield Project.objects.filter(pk=open(path).read())
            
            if Project.objects.all().count() == 1:
                yield Project.objects.all()
        
        for filter in search():
            if filter.count() > 0:
                return filter[0]
        
        raise Project.DoesNotExist
            
    def get_user(self):
        from squash import settings
        from django.contrib.auth.models import User
        user, _ = User.objects.get_or_create(username = settings.USER)
        return user
        
    user = property(get_user)
    
    def edit_src(self, src, filename):
        o = open(filename, 'w')
        o.write(src)
        o.close()
        
        result = os.system('%s %s' % (os.environ['EDITOR'], filename))
        
        if (result != 0):
            raise CommandError("Edit aborted.")
        
        o = open(filename)
        src = o.read()
        o.close()
        
        if os.path.exists(filename):
            os.unlink(filename)
        
        return src

def random_key():
    import random
    return ''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(8)])

def run():
    from squash import settings
    from django.core.management import setup_environ
    setup_environ(settings)
    
    if len(sys.argv) < 2 or sys.argv[1].startswith('-'):
        parser = OptionParser(usage="usage: %prog [command] [options]")
        parser.print_usage()
        sys.exit(2)

    commandCls = Command.resolve(sys.argv[1])
    if commandCls is None:
        print "Unknown command: %s" % sys.argv[1]
        sys.exit(2)

    command = commandCls()
    command.parse()
    
    try:
        command.execute()
    except CommandError, e:
        print e