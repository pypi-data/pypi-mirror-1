import urllib
from sape.client import Client

from django.conf import settings

def sape(request):
    path = urllib.quote(request.path.encode('utf-8'), safe='/')
    qs = request.META.get('QUERY_STRING', '')
    url = '%s%s%s' % (path, (qs and '?' or ''), qs)
    client = Client(settings.SAPE_DATABASE, url)
    return {'sape': client}
