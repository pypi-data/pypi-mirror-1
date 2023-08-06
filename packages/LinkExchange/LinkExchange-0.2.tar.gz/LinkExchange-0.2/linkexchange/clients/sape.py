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

import random
import urllib2
import httplib
import socket
import datetime
import re
import xml.sax
import xml.sax.saxutils
import xml.dom
import xml.dom.pulldom
import StringIO
import HTMLParser
import htmlentitydefs
import logging

try:
    set
except NameError:
    from sets import Set as set

try:
    import phpserialize
except ImportError:
    phpserialize = None

from linkexchange.clients.base import BaseClient, SimpleFileTestServer
from linkexchange.clients.base import ClientError, \
        ClientNetworkError, ClientDataError, ClientDataAccessError
from linkexchange.utils import is_plugin_specifier, load_plugin
from linkexchange.utils import urlopen_with_timeout, default_user_agent
from linkexchange.utils import normalize_uri

log = logging.getLogger('linkexchange.clients.sape')

class SapeLikeTestServer(SimpleFileTestServer):
    data = None
    extra_data = None
    use_xml = True

    def __init__(self, filename = None, data = None, extra_data = None,
            use_xml = None):
        if data is not None:
            self.data = data
        if extra_data is not None:
            self.extra_data = extra_data
        if self.extra_data:
            self.data.update(self.extra_data)
        if use_xml is not None:
            self.use_xml = use_xml
        if self.use_xml:
            raw_data = self.format_data_xml(self.data)
        else:
            raw_data = self.format_data(self.data)
        super(SapeLikeTestServer, self).__init__(filename = filename,
                raw_data = raw_data)

    def format_data(self, data):
        return phpserialize.dumps(data)

    def format_data_xml(self, data):
        return ''

class SapeLikeClient(BaseClient):
    """
    Base class for Sape-like clients.
    """
    db_lifetime = datetime.timedelta(seconds = 3600)
    db_reloadtime = datetime.timedelta(seconds = 600)
    socket_timeout = 6
    force_show_code = True
    server_list = []
    xml_server_list = []
    use_xml = True
    user_agent = default_user_agent

    def __init__(self, user, db_driver, **kw):
        """
        SapeLikeClient constructor.
        
        The user is hash code string that assigned to user on link exchange
        service.

        The db_driver argument is multihash database driver instance or plugin
        specifier. In second case plugin specifier is used to create new
        instance. The database driver instance is used to store links database.

        The db_lifetime keyword argument specifies database lifetime. Database
        older than this time interval will be updated be calling refresh_db().
        Value can be datetime.timedelta object or number of seconds as integer
        or float value. None value disables database refreshing, but refreshing
        will occur if database is not exist even if db_lifetime is None.

        The db_reloadtime specifies the time interval during which the database
        refreshing is not happens if the previous attempt to refreshing was
        failed. This prevents remote server overloading when problem on client
        side. Value can be datetime.timedelta object or number of seconds as
        integer or float value. None value means that db_lifetime value should
        be used.

        The socket_timeout is socket timeout for remote connections in seconds.

        @param user: user hash code string on link exchange service
        @param db_driver: multihash database driver instance or plugin specifier
        @keyword db_lifetime: DB lifetime as datetime.timedelta object or
                              number of seconds as numeric value or None
        @keyword db_reloadtime: DB reload time as datetime.timedelta object or
                              number of seconds as numeric value or None
        @keyword socket_timeout: socket timeout in seconds
        @keyword force_show_code: if True force to show check code
        @keyword server_list: list of servers URLs that returns PHP data
        @keyword xml_server_list: list of servers URLs that returns XML data
        @keyword use_xml: fetch database in XML format from servers in
                          xml_server_list
        @keyword user_agent: user agent string
        """
        self.user = user
        if is_plugin_specifier(db_driver):
            db_driver = load_plugin('linkexchange.multihash_drivers', db_driver)
        self.db_driver = db_driver
        for param in ('db_lifetime', 'db_reloadtime', 'socket_timeout',
                'force_show_code', 'server_list', 'xml_server_list',
                'use_xml', 'user_agent'):
            if param in kw:
                setattr(self, param, kw[param])
        for param in ('db_lifetime', 'db_reloadtime'):
            value = getattr(self, param)
            if type(value) in (int, long, float):
                setattr(self, param, datetime.timedelta(seconds = value))
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
                        'xml_server_list',
                        'use_xml',
                        'user_agent')]))

    def normalize_host(self, request):
        host = request.host.lower()
        if host.startswith('www.'):
            host = host[len('www.'):]
        return host

    def load_data(self, request):
        def save_error(host, data, error):
            new_data = {}
            new_data.update(data)
            new_data['__error_time__'] =  datetime.datetime.now()
            new_data['__error_value__'] = error
            return self.db_driver.save(host, new_data, blocking = False)

        host = self.normalize_host(request)
        data = None
        force_refresh = False
        try:
            data = self.db_driver.load(host)
        except KeyError:
            log.debug("No existing database found, creating new one")
        if data is not None and self.db_lifetime is not None:
            reloadtime = self.db_reloadtime
            if reloadtime is None:
                reloadtime = self.db_lifetime
            try:
                refresh_after = data['__error_time__'] + reloadtime
            except KeyError:
                refresh_after = (self.db_driver.get_mtime(host) +
                        self.db_lifetime)
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

    def get_links(self, data, request):
        try:
            return data[str(request.uri)]
        except KeyError:
            return self.get_links_new_page(data, request)

    def get_links_new_page(self, data, request):
        return []

    def get_delimiter(self, data, request):
        return ''

    def is_bot(self, data, request):
        return False

    def transform_code(self, data, request, code):
        return code

    def get_raw_links(self, request):
        log.debug("Getting raw links for: %s", request.url())
        data = self.load_data(request)
        links = self.get_links(data, request)
        return [self.transform_code(data, request, code) for code in links]

    def get_html_links(self, request):
        log.debug("Getting HTML links for: %s", request.url())
        data = self.load_data(request)
        links = self.get_links(data, request)
        delim = self.get_delimiter(data, request)
        html = delim.join(links)
        return self.transform_code(data, request, html)

    def parse_link(self, link):
        if type(link) == str:
            link = unicode(link, 'utf-8')
        return link

    def parse_data(self, data):
        for key, value in data.items():
            if key.startswith('/'):
                if type(value) == dict:
                    value = value.values()
                yield (normalize_uri(key), map(self.parse_link, value))
            else:
                if type(value) == str:
                    value = unicode(value, 'utf-8')
                yield (key, value)

    def load_from_server(self, server, host):
        url = server % dict(user = self.user, host = host)
        req = urllib2.Request(url)
        req.add_header('User-Agent', self.user_agent)
        try:
            log.debug("Fetching: %s", url)
            f = urlopen_with_timeout(req, self.socket_timeout)
            raw_data = f.read()
            f.close()
        except (urllib2.URLError, httplib.HTTPException, OSError,
                socket.error), e:
            log.error("Network error: %s: %s", str(e), url)
            raise ClientNetworkError('Network error: %s' % str(e))
        if raw_data.startswith('FATAL ERROR:'):
            log.error("Server error: %s: %s", raw_data, url)
            raise ClientError(raw_data)
        try:
            data = phpserialize.loads(raw_data)
        except ValueError, e:
            log.error("Could not deserialize response from server: %s: %s", str(e), url)
            raise ClientDataError('Could not deserialize response '
                    'from server: %s' % str(e))
        return self.parse_data(data)

    def parse_data_xml(self, data):
        return []

    def load_from_server_xml(self, server, host):
        url = server % dict(user = self.user, host = host)
        req = urllib2.Request(url)
        req.add_header('User-Agent', self.user_agent)
        try:
            log.debug("Fetching: %s", url)
            f = urlopen_with_timeout(req, self.socket_timeout)
            events = xml.dom.pulldom.parse(f)
            for x in self.parse_data_xml(events):
                yield x
            f.close()
        except (urllib2.URLError, httplib.HTTPException, OSError,
                socket.error), e:
            log.error("Network error: %s: %s", str(e), url)
            raise ClientNetworkError('Network error: %s' % str(e))
        except xml.sax.SAXParseException, e:
            log.error("Could not parse XML data: %s: %s", str(e), url)
            raise ClientDataError('Could not parse XML data: %s' % str(e))

    def refresh_db(self, request):
        host = self.normalize_host(request)
        if self.use_xml:
            server_list = self.xml_server_list[:]
        else:
            server_list = self.server_list[:]
        random.shuffle(server_list)
        server_list = iter(server_list)
        data = None
        error = None

        while data is None:
            try:
                server = server_list.next()
                if self.use_xml:
                    data = self.load_from_server_xml(server, host)
                else:
                    data = self.load_from_server(server, host)
            except StopIteration:
                raise error
            except ClientError, e:
                error = e
                continue
        if not self.db_driver.save(host, data, blocking = False):
            log.warning("Other process/tread is currently writes to the database")
            raise ClientDataAccessError(
                    "Other process/tread is currently writes to the database")

class SapeTestServer(SapeLikeTestServer):
    filename = 'sape_test_server_data.txt'
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
        '__sape_new_url__': '<!--12345-->',
        '__sape_delimiter__': '. ',
        }

    def format_data_xml(self, data):
        def make_page(uri, links):
            return '<page uri="%s">%s</page>' % (uri,
                    ''.join(['<link><![CDATA[%s]]></link>' % s
                        for s in links]))

        pages = '\n'.join([make_page(uri, links)
            for uri, links in data.items() if uri.startswith('/')])

        lines = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<sape delimiter="%s">' % data.get('__sape_delimiter__', ''),
                pages,
                '<page uri="*"><![CDATA[%s]]></page>' % data.get(
                    '__sape_new_url__', ''),
                '</sape>']
        return '\n'.join(lines)

class SapeClient(SapeLikeClient):
    """
    Sape.ru client.

    >>> from linkexchange.clients.base import PageRequest
    >>> test_server = SapeTestServer()
    >>> cl = SapeClient(user = 'user123456789', db_driver = ('mem',),
    ...                 use_xml = True, xml_server_list = [test_server.url])
    >>> lx = cl.get_raw_links(PageRequest(url = 'http://example.com/'))
    >>> lx[0]
    u'<a href="url1">link1</a>'
    >>> lx[1]
    u'<a href="url2">link2</a>'
    >>> cl = SapeClient(user = 'user123456789', db_driver = ('mem',),
    ...                 use_xml = True, xml_server_list = ['file:///does_not_exists'])
    >>> cl.get_raw_links(PageRequest(url = 'http://example.com/'))
    []
    >>> cl.get_raw_links(PageRequest(url = 'http://example.com/'))
    []
    """

    server_list = [
            'http://dispenser-01.sape.ru/code.php?user=%(user)s&host=%(host)s&charset=utf-8',
            'http://dispenser-02.sape.ru/code.php?user=%(user)s&host=%(host)s&charset=utf-8']
    xml_server_list = [
            'http://dispenser-01.sape.ru/code.php?user=%(user)s&host=%(host)s&charset=utf-8&as_xml=1',
            'http://dispenser-02.sape.ru/code.php?user=%(user)s&host=%(host)s&charset=utf-8&as_xml=1']

    def get_links_new_page(self, data, request):
        if self.is_bot(data, request) or self.force_show_code:
            try:
                return [data['__sape_new_url__']]
            except KeyError:
                pass
        return []

    def get_delimiter(self, data, request):
        return data.get('__sape_delimiter__', '')

    def is_bot(self, data, request):
        return request.cookies.get('sape_cookie') == self.user

    def transform_code(self, data, request, code):
        if self.is_bot(data, request):
            code = '<sape_noindex>%s</sape_noindex>' % code
        return code

    def parse_data(self, data):
        for key, value in data.items():
            if key.startswith('/'):
                if type(value) == dict:
                    value = value.values()
                yield (normalize_uri(key), map(self.parse_link, value))
            else:
                if type(value) == str:
                    value = unicode(value, 'utf-8')
                yield (key, value)

    def parse_data_xml(self, data):
        def node_text(node):
            return u''.join([sn.nodeValue for sn in node.childNodes
                if sn.nodeType == xml.dom.Node.TEXT_NODE])
        path = []
        for (event, node) in data:
            if event == xml.dom.pulldom.START_ELEMENT:
                path.append(node.tagName)
                if path == ['sape', 'page']:
                    data.expandNode(node)
                    path.pop()
                    uri = node.getAttribute('uri')
                    if uri == '*':
                        yield ('__sape_new_url__', node_text(node))
                    else:
                        uri = normalize_uri(uri)
                        link_nodes = node.getElementsByTagName('link')
                        yield (uri, [self.parse_link(node_text(x))
                            for x in link_nodes])
                elif path == ['sape', 'sape_ips']:
                    data.expandNode(node)
                    path.pop()
                    ip_nodes = node.getElementsByTagName('ip')
                    yield ('__sape_ips__',
                            [node_text(x) for x in ip_nodes])
                elif path == ['sape']:
                    delimiter = node.getAttribute('delimiter')
                    if delimiter:
                        yield ('__sape_delimiter__', delimiter)
            elif event == xml.dom.pulldom.END_ELEMENT:
                path.pop()

class ContextLinksGenerator(HTMLParser.HTMLParser):
    def __init__(self, out, links,
            is_fragment, show_code, new_url_code,
            force_body_sape_index = False,
            exclude_tags = None,
            include_tags = None):
        HTMLParser.HTMLParser.__init__(self)
        self.out = out
        self.char_buf = []
        self.links = links
        self.is_fragment = is_fragment
        self.show_code = show_code
        self.new_url_code = new_url_code
        self.force_body_sape_index = force_body_sape_index
        self.exclude_tags = (exclude_tags or set()) | set(['a',
            'textarea', 'select', 'script', 'style',
            'label', 'noscript' , 'noindex', 'button'])
        self.exclude_ctx = []
        self.include_tags = include_tags or set()
        self.include_ctx = []

    def handle_starttag(self, tag, attrs):
        self.handle_realdata()
        if self.is_fragment:
            ignore = tag in ('html', 'body')
        else:
            ignore = not self.show_code and tag == 'sape_index'
        if not ignore:
            self.out.write(u'<' + tag)
            for k, v in attrs:
                self.out.write(' %s="%s"' % (k, xml.sax.saxutils.escape(v)))
            self.out.write(u'>')
        if tag == 'body' and self.show_code:
            if ((not self.is_fragment and self.force_body_sape_index) or
                    self.is_fragment):
                self.out.write('<sape_index>')
        if tag in self.exclude_tags:
            self.exclude_ctx.append(tag)
        elif tag in self.include_tags:
            self.include_ctx.append(tag)

    def handle_endtag(self, tag):
        self.handle_realdata()
        if tag == 'body' and self.show_code:
            if ((not self.is_fragment and self.force_body_sape_index) or
                    self.is_fragment):
                self.out.write('</sape_index>')
                if self.new_url_code:
                    self.out.write(self.new_url_code)
        if self.is_fragment:
            ignore = tag in ('html', 'body')
        else:
            ignore = not self.show_code and tag == 'sape_index'
        if not ignore:
            self.out.write('</%s>' % tag)
            if tag == 'sape_index' and self.show_code and self.new_url_code:
                self.out.write(self.new_url_code)
        if tag in self.exclude_tags:
            self.exclude_ctx.pop()
        elif tag in self.include_tags:
            self.include_ctx.pop()

    def handle_startendtag(self, tag, attrs):
        self.handle_realdata()
        self.out.write(u'<' + tag)
        for k, v in attrs:
            self.out.write(' %s="%s"' % (k, xml.sax.saxutils.escape(v)))
        self.out.write(u'/>')

    def handle_data(self, data):
        self.char_buf.append(data)

    def handle_charref(self, name):
        self.char_buf.append('&#%s;' % name)

    def handle_entityref(self, name):
        self.char_buf.append('&%s;' % name)

    def handle_realdata(self):
        content = ''.join(self.char_buf)
        self.char_buf[:] = []
        if not self.exclude_ctx:
            if set(self.include_ctx) == self.include_tags:
                for sentence_re, link in self.links:
                    content = sentence_re.sub(link, content, count = 1)
        self.out.write(content)

    def handle_comment(self, data):
        self.char_buf.append('<!--%s-->' % data)

    def handle_decl(self, data):
        self.char_buf.append('<!%s>' % data)

    def handle_pi(self, data):
        self.char_buf.append('<?%s>' % data)

class SapeContextClient(SapeClient):
    """
    Sape.ru client for context links.

    >>> from linkexchange.clients.base import PageRequest
    >>> test_server = SapeTestServer()
    >>> cl = SapeContextClient(user = 'user123456789', db_driver = ('mem',),
    ...                 use_xml = True, xml_server_list = [test_server.url],
    ...                 force_show_code = False)
    >>> html = lambda x: u'<html>\\n<body>\\n%s\\n</body>\\n</html>' % x
    >>> req = PageRequest(url = 'http://example.com/',
    ...                   cookies = dict(sape_cookie = cl.user))
    >>> print cl.content_filter(req, u'This&#x20;text contains the link1.')
    <sape_index>This&#x20;text contains the <a href="url1">link1</a>.</sape_index><!--12345-->
    >>> print cl.content_filter(req, u'foo <textarea>link1 bar</textarea>')
    <sape_index>foo <textarea>link1 bar</textarea></sape_index><!--12345-->
    >>> print cl.content_filter(req, html(u'Text link2'))
    <html>
    <body><sape_index>
    Text <a href="url2">link2</a>
    </sape_index><!--12345--></body>
    </html>
    >>> print cl.content_filter(req, html(u'<sape_index>Text link1</sape_index> &amp; Text link2.'))
    <html>
    <body>
    <sape_index>Text <a href="url1">link1</a></sape_index><!--12345--> &amp; Text link2.
    </body>
    </html>
    >>> req = PageRequest(url = 'http://example.com/',
    ...                   cookies = dict())
    >>> print cl.content_filter(req, u'This&#x20;text contains the link1.')
    This&#x20;text contains the <a href="url1">link1</a>.
    >>> print cl.content_filter(req, u'foo <textarea>link1 bar</textarea>')
    foo <textarea>link1 bar</textarea>
    >>> print cl.content_filter(req, html(u'Text link2'))
    <html>
    <body>
    Text <a href="url2">link2</a>
    </body>
    </html>
    >>> print cl.content_filter(req, html(u'<sape_index>Text link1</sape_index> &amp; Text link2.'))
    <html>
    <body>
    Text <a href="url1">link1</a> &amp; Text link2.
    </body>
    </html>
    """

    force_show_code = False
    server_list = [
            'http://dispenser-01.sape.ru/code_context.php?user=%(user)s&host=%(host)s&charset=utf-8',
            'http://dispenser-02.sape.ru/code_context.php?user=%(user)s&host=%(host)s&charset=utf-8']
    xml_server_list = [
            'http://dispenser-01.sape.ru/code_context.php?user=%(user)s&host=%(host)s&charset=utf-8&as_xml=1',
            'http://dispenser-02.sape.ru/code_context.php?user=%(user)s&host=%(host)s&charset=utf-8&as_xml=1']

    def __init__(self, user, db_driver, **kw):
        super(SapeContextClient, self).__init__(user, db_driver, **kw)
        self.tags_re = re.compile(r'<[^>]*>')
        self.start_doc_re = re.compile(r'^\s*<(\?xml|!DOCTYPE|html|HTML)\b', re.S)

    def get_raw_links(self, request):
        return []

    def get_html_links(self, request):
        return u''

    def content_filter(self, request, content):
        data = self.load_data(request)
        show_code = self.is_bot(data, request) or self.force_show_code
        links = data.get(str(request.uri), [])
        force_body_sape_index = False
        include_tags = set()
        if self.start_doc_re.match(content):
            is_fragment = False
            include_tags = set(['body'])
            if '<sape_index>' not in content:
                force_body_sape_index = True
            else:
                include_tags |= set(['sape_index'])
        else:
            is_fragment = True
            content = '<html><body>%s</body></html>' % content
        out = StringIO.StringIO()
        generator = ContextLinksGenerator(out, links,
                is_fragment = is_fragment,
                show_code = show_code,
                new_url_code = data.get('__sape_new_url__', ''),
                force_body_sape_index = force_body_sape_index,
                include_tags = include_tags)
        generator.feed(content)
        generator.close()
        return out.getvalue()

    def parse_link(self, link):
        link = super(SapeContextClient, self).parse_link(link)
        sentence = re.escape(xml.sax.saxutils.unescape(
            self.tags_re.sub('', link)))
        sentence.replace(' ', r'(\s|(&nbsp;))+')
        return (re.compile(sentence, re.S + re.UNICODE), link)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
