from base import *
from getpass import getpass

class Pass(Command):
    """Change the password."""
    name = 'pass'
    usage = "[user]"
    
    option_list = [
        make_option("--set", action="store", dest="password"),
    ]
    
    def execute(self):
        from django.contrib.auth.models import User
        
        if self.args:
            username = self.args[0]
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                print "User does not exist."
                return
        else:
            user = self.get_user()
        
        if self.options.password:
            user.set_password(self.options.password)
            user.save()
            print "User %s password set." % user.username
            return
        
        try:
            while 1:
                first = getpass("Please enter a new password: ")
                second = getpass("Please re-enter the new password: ")
                if first != second:
                    print "Entries are not the same; please try again."
                    continue
                else:
                    break
        except KeyboardInterrupt:
            print "\nAborted."
            return
        
        user.set_password(first)
        user.save()
        
Command.all.append(Pass)

class Users(Command):
    """List all squash users."""
    name = 'users'
    
    def execute(self):
        from django.contrib.auth.models import User
        users = User.objects.all()
        if not users.count() > 0:
            print "No users found."
        else:
            for u in users:
                print u.username
        
Command.all.append(Users)