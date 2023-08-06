from base import *

class Ticket(Command):
    """Edit a new or existing ticket."""
    name = 'ticket'
    usage = "(id | :new)"
    options = """
        squash ticket --help
         --edit
         --name
         --description
         --project
         --move   #change project
         --close -x
         --state
         --tags
         --tag+
         --tag-
         --delete
         --comment
         --update
    """
    
    option_list = [
        make_option("-n", "--name", action="store", type="string", dest="name", default=None),
        make_option("-d", "--description", action="store", type="string", dest="description", default=None),
        make_option("-s", "--state", action="store", type="string", dest="state", default=None),
        make_option("-e", "--edit", action="store_true", dest="edit"),
        make_option("-x", "--delete", action="store_true", dest="delete"),
        make_option("-p", "--project", action="store", type="string", dest="project", default=None),
        make_option("-f", "--folder", action="store", type="string", dest="folder", default=None),
        make_option("-o", "--owner", action="store", type="string", dest="owner", default=None),
        make_option("--noinput", action="store_true", dest="noinput"),
    ]
    
    def execute(self):
        from changeset import update
        
        try:
            ticket = self.find_ticket(self.args[0])
        except ObjectDoesNotExist:
            raise CommandError("Cannot find ticket %r." % self.args[0])
        except IndexError:
            print self.parser.print_usage()
            return
        
        if self.options.delete:
            return self.delete(ticket, self.options.noinput)
        
        if not ticket.id:
            if not self.options.name:
                self.options.edit = True
        
        details = {
            'name': self.options.name,
            'description': self.options.description,
            'state': self.options.state,
            'owner': self.options.owner,
        }
        
        update(ticket, clean(details), self)
        
        if (self.options.folder):
            ticket.folder = ticket.project.folder_set.get(slug=self.options.folder)
        
        if (self.options.edit):
            details.update( self.edit( ticket ) )
            update(ticket, details, self)
        
        ticket.save()
        print self.yaml(ticket)
    
    def yaml(self, ticket):
        if ticket.user:
            username = ticket.user.username
        else:
            username = ''
        return "\n".join([
            '## %s ##' % ticket.pk,
            'name:     %s' % ticket.name,
            'project:  %s' % ticket.project.slug,
            'folder:   %s' % ticket.folder.slug,
            'state:    %s' % ticket.state.slug,
            'owner:    %s' % username,
            'description: \n  %s\n' % ticket.description,
        ])
    
    def edit(self, instance):
        from squash.changeset import update
        
        src = self.yaml(instance)
        src_hash = hash(src)

        src = self.edit_src(src, '/tmp/squash-ticket-%s' % random_key())

        if hash(src) == src_hash:
            print 'No changes made.'
            return

        details = yaml.load(src)

        update(instance, details, self)
        src = self.yaml(instance)
        if hash(src) == src_hash:
            print 'No changes made.'
            return
    
    def delete(self, instance, noinput):
        if not noinput:
            try:
                confirm = raw_input("Enter 'delete' to confirm deleting ticket %s: \n   " % instance.name)
            except:
                confirm = None
        else:
            confirm = 'delete'
        
        if confirm == 'delete':
            instance.delete()
            print "Ticket deleted."
        else:
            raise CommandError("\nAborted")
    
Command.all.append(Ticket)
