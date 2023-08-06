Installation
============

Just install `sape` package via easy_install, pip or from repository.

Repository URL: http://bitbucket.org/lorien/sape


Usage in django project
=======================

 * Create directory where local links database should be saved
 * Put 'sape.django' into settings.INSTALLED_APPS
 * Put 'sape.django.context_processors.sape'
   into settings.TEMPLATE_CONTEXT_PROCESSORS
 * Put path to local links database into settings.SAPE_DATABASE
 * Put sape.ru account ID to settings.SAPE_USER
 * Put site hostname to settings.SAPE_HOST
 * Setup cron to run periodically the command `manage.py sape_refresh`.
   That command download fresh version of links database.
   Sample cron entry: * * * * * cd /web/project; ./manage.py sape_refresh
 * Put `{{ sape.links|safeseq|join:", " }} in the template


Usage in arbitrary python project
=================================

 * Write script which calls sape.provider.refresh_local_database function and passes
   it correct arguments (path to local database, sape.ru account ID, site hostname)
 * Call that script periodically with cron or anything else
 * Use sape.client.Client instance to get links for the page.


Example of Client usage
=======================

    from sape.client import Client

    url = 'http://mydomain.com/cat/subcat/?foo=bar'
    client = Client('var/links.db', url)
    links = client.links()


Example of Provider usage
=========================

    from sape.provider import refresh_local_database

    refresh_local_database('var/links.db', 'sape.ru ID', 'mydomain.com')
