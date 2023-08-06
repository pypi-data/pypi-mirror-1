# LinkExchange - Universal link exchange service client
# Copyright (C) 2009 Konstantin Korikov
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# NOTE: In the context of the Python environment, I interpret "dynamic
# linking" as importing -- thus the LGPL applies to the contents of
# the modules, but make no requirements on code importing these
# modules.

import urllib2
import httplib
import random
import datetime
import xml.dom.pulldom
import logging

from linkexchange.clients.base import BaseClient, SimpleFileTestServer
from linkexchange.clients.base import ClientError, \
        ClientNetworkError, ClientDataError, ClientDataAccessError
from linkexchange.utils import is_plugin_specifier, load_plugin
from linkexchange.utils import urlopen_with_timeout, get_default_user_agent

log = logging.getLogger('linkexchange.clients.linkfeed')

class LinkFeedTestServer(SimpleFileTestServer):
    filename = 'linkfeed_test_server_data.xml'
    data = {
        '/': [
            '<a href="url1">link1</a>',
            '<a href="url2">link2</a>'],
        '/path/1': [
            '<a href="url1">link1</a>',
            '<a href="url2">link2</a>',
            '<a href="url3">link3</a>',
            '<a href="url4">link4</a>'],
        '/path/2': [
            'Plain text and <a href="url">link text</a>'],
        }
    extra_data = None

    def __init__(self, filename = None, data = None, extra_data = None):
        def make_page(url, links):
            return '<page url="%s">%s</page>' % (url,
                    ''.join(['<link><![CDATA[%s]]></link>' % s
                        for s in links]))
        if data is not None:
            self.data = data
        if extra_data is not None:
            self.extra_data = extra_data
        if self.extra_data:
            self.data.update(self.extra_data)
        raw_data = """<?xml version="1.0" encoding="UTF-8"?>
        <data>
            <config>
                <item name="end"><![CDATA[<!--12345-->]]></item>
                <item name="delimiter"><![CDATA[.]]></item>
                <item name="after_text"><![CDATA[]]></item>
                <item name="start"><![CDATA[<!--12345-->]]></item>
                <item name="before_text"><![CDATA[]]></item>
            </config>
            <pages>
            %s
            </pages>
        </data>""" % '\n'.join([make_page(url, links)
            for url, links in self.data.items()])
        super(LinkFeedTestServer, self).__init__(filename = filename,
                raw_data = raw_data)

class LinkFeedClient(BaseClient):
    """
    LinkFeed.ru client.

    >>> from linkexchange.clients.base import PageRequest
    >>> test_server = LinkFeedTestServer()
    >>> cl = LinkFeedClient(user = 'user123456789', db_driver = ('mem',),
    ...                 server_list = [test_server.url])
    >>> lx = cl.get_raw_links(PageRequest(url = 'http://example.com/'))
    >>> lx[0]
    u'<!--12345--><a href="url1">link1</a><!--12345-->'
    >>> lx[1]
    u'<!--12345--><a href="url2">link2</a><!--12345-->'
    >>> cl = LinkFeedClient(user = 'user123456789', db_driver = ('mem',),
    ...                 server_list = ['file:///does_not_exists'])
    >>> cl.get_raw_links(PageRequest(url = 'http://example.com/'))
    []
    >>> cl.get_raw_links(PageRequest(url = 'http://example.com/'))
    []
    """

    def __init__(self, user, db_driver, **kw):
        """
        @param user: user ID of LinkFeed account
        @param db_driver: multihash database driver instance or plugin specifier
        @keyword db_lifetime: DB lifetime as datetime.timedelta object or
                              number of seconds as numeric value
        @keyword db_reloadtime: if an error in DB refreshing occurred don't
                                refresh DB within this time (datetime.timedelta
                                or number of seconds)
        @keyword socket_timeout: socket timeout in seconds
        @keyword force_show_code: if True force to show check code
        @keyword server_list: list of servers URLs
        @keyword user_agent: user agent string
        """
        self.user = user
        if is_plugin_specifier(db_driver):
            db_driver = load_plugin('linkexchange.multihash_drivers', db_driver)
        self.db_driver = db_driver
        self.db_lifetime = kw.get('db_lifetime',
                datetime.timedelta(seconds = 3600))
        if type(self.db_lifetime) in (int, long, float):
            self.db_lifetime = datetime.timedelta(seconds = self.db_lifetime)
        self.db_reloadtime = kw.get('db_reloadtime',
                datetime.timedelta(seconds = 600))
        if type(self.db_reloadtime) in (int, long, float):
            self.db_reloadtime = datetime.timedelta(seconds = self.db_reloadtime)
        self.socket_timeout = kw.get('socket_timeout', 6)
        self.force_show_code = kw.get('force_show_code', True)
        self.server_list = kw.get('server_list', [
            'http://db.linkfeed.ru/%(user)s/%(host)s/UTF-8.xml'])
        self.user_agent = kw.get('user_agent', get_default_user_agent())
        log.debug("New %s instance:\n%s",
                self.__class__.__name__,
                '\n'.join(["    %s: %s" % (x, repr(getattr(self, x)))
                    for x in (
                        'user',
                        'db_driver',
                        'db_lifetime',
                        'db_reloadtime',
                        'socket_timeout',
                        'force_show_code',
                        'server_list',
                        'user_agent')]))

    def _normalize_host(self, request):
        host = request.host.lower()
        if host.startswith('www.'):
            host = host[len('www.'):]
        return host

    def _load_data(self, request):
        def save_error(host, data, error):
            new_data = {}
            new_data.update(data)
            new_data['__error_time__'] =  datetime.datetime.now()
            new_data['__error_value__'] = error
            return self.db_driver.save(host, new_data, blocking = False)

        host = self._normalize_host(request)
        data = None
        force_refresh = False
        try:
            data = self.db_driver.load(host)
        except KeyError:
            log.debug("No existing database found, creating new one")
        else:
            try:
                refresh_after = data['__error_time__'] + self.db_reloadtime
            except KeyError:
                refresh_after = self.db_driver.get_mtime(host) + self.db_lifetime
            if refresh_after <= datetime.datetime.now():
                log.debug("The database too old, refreshing")
                force_refresh = True
        if data is None:
            try:
                self.refresh_db(request)
            except ClientError, e:
                if not save_error(host, {}, e):
                    raise e
            data = self.db_driver.load(host)
        elif force_refresh:
            try:
                self.refresh_db(request)
            except ClientDataAccessError:
                pass
            except ClientError, e:
                save_error(host, data, e)
            data = self.db_driver.load(host)
        return data

    def get_raw_links(self, request):
        log.debug("Getting raw links for: %s", request.url())
        data = self._load_data(request)
        bot_ips = data.get('__linkfeed_bot_ips__', [])
        if self.force_show_code or (request.remote_addr and
                request.remote_addr in bot_ips):
            start = data.get('__linkfeed_start__', '')
            end = data.get('__linkfeed_end__', '')
        else:
            start = end = u''
        before_text = data.get('__linkfeed_before_text__', '')
        after_text = data.get('__linkfeed_after_text__', '')
        links = [start + before_text + unicode(x) + after_text + end
                for x in data.get(str(request.uri), [])]
        if not links and (start or end):
            links = [start + end]
        return links

    def get_html_links(self, request):
        log.debug("Getting HTML links for: %s", request.url())
        data = self._load_data(request)
        bot_ips = data.get('__linkfeed_bot_ips__', [])
        if self.force_show_code or (request.remote_addr and
                request.remote_addr in bot_ips):
            start = data.get('__linkfeed_start__', '')
            end = data.get('__linkfeed_end__', '')
        else:
            start = end = u''
        before_text = data.get('__linkfeed_before_text__', '')
        after_text = data.get('__linkfeed_after_text__', '')
        delimiter = data.get('__linkfeed_delimiter__', '')
        links = [unicode(x) for x in data.get(str(request.uri), [])]
        return (start + before_text + delimiter.join(links) +
                after_text + end)

    def _do_load_from_server(self, url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', self.user_agent)
        try:
            log.debug("Fetching: %s", url)
            f = urlopen_with_timeout(req, self.socket_timeout)
            events = xml.dom.pulldom.parse(f)
            path = []
            node_text = lambda node: (node.firstChild is not None and
                    node.firstChild.nodeValue or u'')
            for (event, node) in events:
                if event == xml.dom.pulldom.START_ELEMENT:
                    path.append(node.tagName)
                    if path == ['data', 'pages','page']:
                        events.expandNode(node)
                        path.pop()
                        url = str(node.getAttribute('url'))
                        if url:
                            link_nodes = node.getElementsByTagName('link')
                            yield (url, [node_text(x) for x in link_nodes])
                    elif path == ['data', 'config', 'item']:
                        events.expandNode(node)
                        path.pop()
                        name = str(node.getAttribute('name'))
                        if name:
                            yield ("__linkfeed_%s__" % name,
                                    node_text(node))
                    elif path == ['data', 'bot_ips']:
                        events.expandNode(node)
                        path.pop()
                        ip_nodes = node.getElementsByTagName('ip')
                        yield ("__linkfeed_bot_ips__",
                                [node_text(x) for x in ip_nodes])
                elif event == xml.dom.pulldom.END_ELEMENT:
                    path.pop()
            f.close()
        except (urllib2.URLError, httplib.HTTPException, OSError), e:
            log.error("Network error: %s", str(e))
            raise ClientNetworkError('Network error: %s' % str(e))

    def refresh_db(self, request):
        host = self._normalize_host(request)
        server_list = self.server_list[:]
        random.shuffle(server_list)
        server_list = iter(server_list)
        data = None
        error = None

        while data is None:
            try:
                server = server_list.next() % dict(
                        user = self.user, host = host)
                data = self._do_load_from_server(server)
            except StopIteration:
                raise error
            except ClientError, e:
                error = e
                continue
        if not self.db_driver.save(host, data, blocking = False):
            log.warning("Other process/tread is currently writes to the database")
            raise ClientDataAccessError(
                    "Other process/tread is currently writes to the database")

if __name__ == "__main__":
    import doctest
    doctest.testmod()
