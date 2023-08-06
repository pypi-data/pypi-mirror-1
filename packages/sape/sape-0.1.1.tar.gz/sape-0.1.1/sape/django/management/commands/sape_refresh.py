import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from sape.provider import refresh_local_database

class Command(BaseCommand):
    help = 'Refresh local database containing sape.ru links'

    def handle(self, *args, **kwargs):
        logging.basicConfig(level=logging.DEBUG)
        refresh_local_database(settings.SAPE_DATABASE, settings.SAPE_USER,
                               settings.SAPE_HOST)
