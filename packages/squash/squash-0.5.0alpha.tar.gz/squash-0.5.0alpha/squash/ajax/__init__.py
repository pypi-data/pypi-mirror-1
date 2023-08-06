import datetime
import sys, traceback

from django.utils import simplejson
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError

# Encoder
class Encoder(simplejson.JSONEncoder):
    """ Serializes dates as well. """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.time):
            return obj.strftime('%H:%M:%S')
        return simplejson.JSONEncoder.default(self, obj)

def json(data):
    return Encoder().encode(data)

def unjson(str, encoding=None):
    return simplejson.loads(str, encoding=encoding or settings.DEFAULT_CHARSET)

# Ajax / Json
class JsonResponse(HttpResponse):
    """ JSON's up your response content. """
    def __init__(self, content):
        super(JsonResponse, self).__init__(json(content), mimetype='application/json')

class Forbidden(Exception):
    pass

def ajaxHandler(func, scope, request, args, kwargs):
    try:
        if scope:
            return JsonResponse(func(scope, request, *args, **kwargs))
        else:
            return JsonResponse(func(request, *args, **kwargs))
    except Forbidden, e:
        return HttpResponseForbidden()
    except Exception, e:
        if not settings.DEBUG:
            return HttpResponseServerError()

        if request.META['SERVER_NAME'] == 'testserver':
            raise

        # Build a traceback to send to the client:
        lines = ["Python Error:\n"]
        lines.extend(traceback.format_tb(sys.exc_traceback)[1:])
        lines.append("%s: %s" % (e.__class__.__name__, str(e)))

        lines.append("\n\nLocals:\n")
        tb = sys.exc_info()[2]
        while tb.tb_next:
            tb = tb.tb_next
        frame = tb.tb_frame
        for key, value in frame.f_locals.items():
            try:
                value = "%r" % value
            except:
                value = '<not representable>'
            lines.append("\t%s: %s\n" % (key,value))

        msg = "".join(lines)
        return JsonResponse({'__failure__': msg})

def ajax(func):
    def inner_func(request, *a, **ka):
        return ajaxHandler(func, None, request, a, ka)
    return inner_func
