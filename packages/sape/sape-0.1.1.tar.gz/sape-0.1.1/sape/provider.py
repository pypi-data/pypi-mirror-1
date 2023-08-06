import anydbm
import urllib2
from StringIO import StringIO
from gzip import GzipFile
import logging
import socket
import os
import shutil
import warnings
from traceback import format_exc

import version
import phpserialize

USER_AGENT = 'python-sape/%s http://bitbucket.org/lorien/sape' % version.VERSION
REMOTE_DATABASE_PATH = '/code.php?user=%(user)s&host=%(host)s&charset=utf-8'
SAPE_SERVERS = ['dispenser-01.sape.ru', 'dispenser-02.sape.ru']
DEFAULT_TIMEOUT = 10
DB_DELIMITER = '||'

warnings.filterwarnings('ignore', 'tmpnam')
socket.setdefaulttimeout(DEFAULT_TIMEOUT)

def display_error(msg):
    """
    Display error message and dump exception traceback.
    """

    logging.error(msg)
    logging.error(format_exc())


def build_database_url(user, client_host, sape_server):
    """
    Build absolute URL of remote file containing links.

    Args:
        user: sape.ru account ID
        host: hostname of the client site
    """

    path = REMOTE_DATABASE_PATH % ({'user': user, 'host': client_host})
    return 'http://%s%s' % (sape_server, path)


def fetch_remote_file(url):
    """
    Retreive remove file and save it locally.

    Args:
        url: absolute URL of remote file
        localpath: local path where file should be saved

    Return:
        Content of retreived file or None if somthing went wrong.
    """

    logging.debug(u'Fetching remote file from %s' % url)
    req = urllib2.Request(url)
    req.add_header('User-Agent', USER_AGENT)
    req.add_header('Accept-Encoding', 'gzip')
    opener = urllib2.build_opener()

    try:
        response = opener.open(url)
    except Exception, ex:
        display_error(u'Error while opening remote database')
    else:
        if response.code == 200:
            data = response.read()
            logging.debug(u'Response headers: %s' % dict(response.headers))
            if 'gzip' in response.headers.get('Content-Encoding', ''):
                data = GZipFile(fileobj=StringIO(data)).read()
            return data
        else:
            logging.error(u'Invalid response status: %d' % response.code)

    return None


def fetch_database(user, host):
    """
    Return content of remote database for given `user` and `host`.

    Args:
        user: sape.ru account ID
        host: hostname of the client site
    """

    for sape_server in SAPE_SERVERS:
        url = build_database_url(user, host, sape_server)
        data = fetch_remote_file(url)
        if data:
            if data.startswith('FATAL ERROR'):
                logging.error(u'Sape.ru error: %s' % data)
            else:
                return data
    return None


def refresh_local_database(path, user, host):
    """
    Fetch remote database, parse it and replace the local database.
    """

    data = fetch_database(user, host)
    if data:
        try:
            mapping = parse_database(data)
        except Exception, ex:
            display_error(u'Invalid database structure')
        else:
            logging.debug('Found %d items in dump' % len(mapping))
            save_database(path, mapping)


def parse_database(data):
    """
    Parse the raw data fetched from sape.ru server.
    """

    links = {}
    dump = phpserialize.loads(data)
    for key, value in dump.iteritems():
        if isinstance(value, dict):
            value = value.values()
        else:
            value = [value]
        links[key] = value
    return links


def save_database(path, mapping):
    """
    Save database in dbm file.

    Args:
        mapping: str -> (str,)
    """

    try:
        tmp_path = os.tmpnam()
        db = anydbm.open(tmp_path, 'c')
        for key, value in mapping.iteritems():
            value = DB_DELIMITER.join(value)
            db[key] = value
        db.sync()
        shutil.move(tmp_path, path)
    except Exception, ex:
        display_error(u'Error while saving database')


def read_database_key(path, key):
    """
    Read the key value from database.

    If key was not found try to read "__sape_new_url__" key.
    If nothing was found return empty string.
    """

    db = anydbm.open(path)
    try:
        value = db[key]
    except KeyError:
        value = db.get('__sape_new_url__', '')
    value = value.split(DB_DELIMITER)
    return value


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
    #fetch_remote_database('http://a.local')
    #fetch_database('user', 'host')
    print read_database('/tmp/links.db', 'foo')
