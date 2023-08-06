from base import Command
import squash.settings

class Serve(Command):
    """Starts up the squash server for web access."""
    name = 'serve'
    usage = "[port number, or ipaddr:port]"
    option_lst = Command.option_list
    
    def execute(self):
        ip = '127.0.0.1'
        port = '8000'
        if (self.args):
            sig = self.args[0]
            if (':' in sig):
                ip, port = sig.split(':', 1)
            else:
                port = sig
        runserver(ip, port)

import os, sys

def runserver(addr, port):
    import django
    from django.core.servers.basehttp import run, AdminMediaHandler, WSGIServerException
    from django.core.handlers.wsgi import WSGIHandler
    
    from django.conf import settings
    from django.utils import translation
    
    # django.core.management.base forces the locale to en-us. We should
    # set it up correctly for the first request (particularly important
    # in the "--noreload" case).
    translation.activate(settings.LANGUAGE_CODE)
    
    admin_media_path = None
    shutdown_message = None
    quit_command = 'CONTROL-C'
    
    if (sys.platform == 'win32'): quit_command = 'CTRL-BREAK'
    
    print "Squash is now running at http://%s:%s" % (addr, port)
    print "Quit the server with %s." % quit_command
    
    try:
        path = admin_media_path or django.__path__[0] + '/contrib/admin/media'
        handler = AdminMediaHandler(WSGIHandler(), path)
        run(addr, int(port), handler)
    except WSGIServerException, e:
        # Use helpful error messages instead of ugly tracebacks.
        ERRORS = {
            13: "You don't have permission to access that port.",
            98: "That port is already in use.",
            99: "That IP address can't be assigned-to.",
        }
        try:
            error_text = ERRORS[e.args[0].args[0]]
        except (AttributeError, KeyError):
            error_text = str(e)
        sys.stderr.write("Error: %s\n" % error_text)
        os._exit(1)
    except KeyboardInterrupt:
        if shutdown_message:
            print shutdown_message
        sys.exit(0)
        
Command.all.append(Serve)