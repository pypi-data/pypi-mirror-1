# Create your views here.
import time

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404

from django.conf import settings as s

## import dj_paginas.guia.models as models
#import dj_paginas.settings as settings

def index(request):
    return HttpResponse('django live')


def chat(request, channel=None, username='guest', manager_channel="MANAGE"):
##    return render_to_response('live/chat.html', {'MEDIA_URL': settings.MEDIA_URL})

    if channel is None:
        channel = str(time.time())

    return render_to_response('live/chat.html',
                              {'ORBITED_HOST': s.ORBITED_HOST,
                               'ORBITED_PORT': s.ORBITED_PORT,
                               'STOMP_PORT': s.STOMP_PORT,
                               'channel': channel,
                               'manager_channel': manager_channel,
                               'username': username
                               })
def manage(request):
    return render_to_response('live/manage.html',
                              {'ORBITED_HOST': s.ORBITED_HOST,
                               'ORBITED_PORT': s.ORBITED_PORT,
                               'STOMP_PORT': s.STOMP_PORT,
                               'manage_channel': "MANAGE"}
                               )

def public(request, room="PUBLIC"):
    return chat(request, channel=room)
    
## #    t = 

## ##     t = loader.get_template('guia/manage.html')
## ##     c = Context({
## ##         'titulo': 'manage me'
## ##         })
## ##     return HttpResponse(t.render(c))

##     if request.POST:
## #        f = models.ChatMessage(request.POST)
## #        f.save()
##         return HttpResponse('success')
        
##     else:
##  ##        form = models.RubroForm()
    
## ##         return render_to_response('manage.html',
## ##                                   {'titulo': 'manageate esta',
## ##                                    'form': form
## ##                                    })
##         return HttpResponse('success tambien')

