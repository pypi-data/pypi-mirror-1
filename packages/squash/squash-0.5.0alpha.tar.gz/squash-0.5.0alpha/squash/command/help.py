from base import Command

class Help(Command):
    """Squash commands, '[command] -h' for help on each command:"""
    name = 'help'
    usage = ''
    option_list = []
    description = "Lists all commands available"
    
    def execute(self):
        print self.__doc__
        print ''
        sz = max(len(command.name) for command in Command.all)
        for command in Command.all:
            print '  ', command.name.ljust(sz + 4), ' ', command.usage
        print ''
    
Command.all.append(Help)