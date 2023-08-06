from django.conf import settings


ORBITED_HOST = getattr(settings, 'ORBITED_HOST', 'localhost')
ORBITED_PORT = getattr(settings, 'ORBITED_PORT', '9000')
STOMP_PORT = getattr(settings, 'STOMP_PORT', '61613')
STOMP_BROKER = getattr(settings, 'STOMP_BROKER', 'morbid')
