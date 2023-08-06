import time

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404

import settings as s


def index(request):
    return HttpResponse('django live')


def chat(request, channel=None, username='guest', manager_channel="MANAGE"):

    if channel is None:
        channel = str(time.time())

    return render_to_response('live/chat.html',
                              {'ORBITED_HOST': s.ORBITED_HOST,
                               'ORBITED_PORT': s.ORBITED_PORT,
                               'STOMP_PORT': s.STOMP_PORT,
                               'STOMP_BROKER': s.STOMP_BROKER.lower(),
                               'channel': channel,
                               'manager_channel': manager_channel,
                               'username': username
                               })
def manage(request):
    return render_to_response('live/manage.html',
                              {'ORBITED_HOST': s.ORBITED_HOST,
                               'ORBITED_PORT': s.ORBITED_PORT,
                               'STOMP_PORT': s.STOMP_PORT,
                               'STOMP_BROKER': s.STOMP_BROKER.lower(),
                               'manage_channel': "MANAGE"}
                               )

def public(request, room="PUBLIC"):
    return chat(request, channel=room)
    
