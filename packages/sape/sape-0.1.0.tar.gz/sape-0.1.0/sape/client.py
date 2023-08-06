import itertools
import logging

from provider import read_database_key


class Client(object):
    def __init__(self, path, url):
        """
        Args:
            path: path to local database file
            url: the *escaped* url of site page for which links should be
                extracted from local database
        """

        self.path = path
        self.url = url
        self.error = ''


    def links(self):
        """
        Return all links on current page.
        """

        if not hasattr(self, '_links'):
            try:
                self._links = read_database_key(self.path, self.url)
            except Exception, ex:
                self._links = []
                self.error = unicode(ex)
                logging.error(u'sape: %s' % unicode(ex))
        return self._links


    def next_links(self, number=1):
        """
        Return next `number` links on current page.
        """

        if not hasattr(self, '_iterator'):
            self._iterator = itertools.chain(self.links())
        return list(itertools.islice(self._iterator, number))


if __name__ == '__main__':
    client = Client('/tmp/links.db', 'five')
    print client.next_links(1)
    print client.next_links(2)
    print client.next_links(10)
