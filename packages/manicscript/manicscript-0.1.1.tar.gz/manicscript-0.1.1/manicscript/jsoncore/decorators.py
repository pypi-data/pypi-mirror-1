
from django.utils import simplejson
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.models import Group
import traceback

def json(view):
        def wrapped_view(*args, **kwargs):
                response = {}
                try:
                        kwargs['response'] = response
                        view(*args,**kwargs)
                except Exception, e:
                        if settings.JSON_DEBUG:
                                response['traceback'] = traceback.format_exc()
                finally:
                        json = simplejson.dumps(response)
                        return HttpResponse(json, mimetype='application/json')

        return wrapped_view

def login_required(view):
        def wrapped_view(request, *args, **kwargs):
                response = kwargs['response']
                if not request.user.is_authenticated():
                        response['result'] = 'error'
                        response['text'] = 'Login required.'
                        return
                view(request, *args, **kwargs)
        return wrapped_view

def group_required(group_name, error_msg='Group membership required.'):
        org = Group.objects.get(name=group_name)
        def decor(view):
                def wrapped_view(request, *args, **kwargs):
                        response = kwargs['response']
                        if org not in request.user.groups.all():
                                response['result'] = 'error'
                                response['text'] = error_msg
                                return
                        view(request, *args, **kwargs)
                return wrapped_view
        return decor
