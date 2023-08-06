from base import *

class List(Command):
    """Lists the tickets."""
    name = "ls"
    usage = "[folder]"
    option_list = [
        make_option("-o", "--outstanding", action="store_true", dest="outstanding"),
        make_option("-f", "--folders", action="store_true", dest="folders"),
        make_option('-a', "--all", action="store_true", dest="all", default=False),
    ]
    
    def list_tickets(self):
        from squash.core.models import Ticket, Project
        
        q = Ticket.objects.all()
        
        if len(self.args) >= 1:
            folders = [ self.find_folder(self.args[0].strip()) ]
        else:
            try:
                folders = list(self.get_current_project().folder_set.order_by('slug'))
            except Project.DoesNotExist:
                print "No project selected."
        
        for folder in tuple(folders):
            if self.options.outstanding:
                folder.tickets = folder.ticket_set.filter(state='open')
                if folder.tickets.count() == 0:
                    folders.remove(folder)
            else:
                folder.tickets = folder.ticket_set.all()
        
        if not folders:
            if self.options.outstanding:
                print "No outstanding tickets found."
                return
            else:
                print "No folders found."
                
        sz = max(len(folder.slug) for folder in folders)
        
        if len(self.args) >= 1:
            folder = folders[0]
            if not folder.tickets.count() > 0:
                print "No tickets found."
            for ticket in folder.tickets:
                print ticket
        else:
            for folder in folders:
                print folder.slug.ljust(sz + 3), folder.name
                if not self.options.folders:
                    for ticket in folder.tickets:
                        print "   ", ticket
        
    def list_folders(self):
        project = self.get_current_project()
        
        if len(self.args) > 0:
            print self.args[0]
        
        folders = list(project.folder_set.all().order_by('slug'))
        
        if folders:
            sz = max(len(folder.slug) for folder in folders)
            for folder in folders:
                print folder.slug.ljust(sz + 3), folder.name
        else:
            print "No folders found."
    
    def execute(self):
        if (self.options.folders):
            return self.list_folders()
        else:
            return self.list_tickets()

Command.all.append(List)

class Status(Command):
    """Prints out the status of a project."""
    name = 'status'
    usage = '[project]'
    
    def execute(self):
        from squash.core.models import Project
        
        try:
            if len(self.args) > 0:
                project = self.find_project(self.args[0])
            else:
                project = self.get_current_project()
        except Project.DoesNotExist:
            print "No project found."
            return
        
        print "Project:", project.name

Command.all.append(Status)

class Switch(Command):
    """Switches the current project."""
    name = 'switch'
    usage = "name"
    
    def execute(self):
        project = self.find_project(self.args[0])
        if project:
            self.set_project(project)
            print "Now using:", project.name
        else:
            print "Unnable to find project."
        
Command.all.append(Switch)

class Home(Command):
    """Outputs the current home path."""
    name = 'home'
    usage = ''
    
    def execute(self):
        from squash import settings
        
        print settings.SQUASH_HOME
        
Command.all.append(Home)