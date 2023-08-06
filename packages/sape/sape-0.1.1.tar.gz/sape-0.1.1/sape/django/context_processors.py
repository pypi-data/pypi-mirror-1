import urllib
from sape.client import Client

from django.conf import settings

def sape(request):
    path = urllib.quote(request.path.encode('utf-8'), safe='/')
    qs = request.META.get('QUERY_STRING', '')
    if qs:
        path += '?' + qs
    client = Client(settings.SAPE_DATABASE, path)
    return {'sape': client}
