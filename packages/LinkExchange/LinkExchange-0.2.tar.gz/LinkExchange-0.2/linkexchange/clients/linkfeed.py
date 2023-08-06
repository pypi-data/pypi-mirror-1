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

import xml.dom
import xml.dom.pulldom
import logging

from linkexchange.clients.sape import SapeLikeTestServer, SapeLikeClient
from linkexchange.utils import normalize_uri

log = logging.getLogger('linkexchange.clients.linkfeed')

class LinkFeedTestServer(SapeLikeTestServer):
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
        '__linkfeed_start__' : '<!--12345-->',
        '__linkfeed_end__' : '<!--12345-->',
        '__linkfeed_delimiter__' : '. ',
        '__linkfeed_before_text__' : '',
        '__linkfeed_after_text__' : '',
        }

    def format_data_xml(self, data):
        def make_page(uri, links):
            return '<page url="%s">%s</page>' % (uri,
                    ''.join(['<link><![CDATA[%s]]></link>' % s
                        for s in links]))

        pages = '\n'.join([make_page(uri, links)
            for uri, links in data.items() if uri.startswith('/')])

        lines = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<data>',
                '<config>',
                '<item name="start"><![CDATA[%s]]></item>' % data.get(
                    '__linkfeed_start__', ''),
                '<item name="end"><![CDATA[%s]]></item>' % data.get(
                    '__linkfeed_end__', ''),
                '<item name="delimiter"><![CDATA[%s]]></item>' % data.get(
                    '__linkfeed_delimiter__', ''),
                '<item name="before_text"><![CDATA[%s]]></item>' % data.get(
                    '__linkfeed_before_text__', ''),
                '<item name="after_text"><![CDATA[%s]]></item>' % data.get(
                    '__linkfeed_after_text__', ''),
                '</config>',
                '<pages>',
                pages,
                '</pages>',
                '</data>',
                ]
        return '\n'.join(lines)

class LinkFeedClient(SapeLikeClient):
    """
    LinkFeed.ru client.

    >>> from linkexchange.clients.base import PageRequest
    >>> test_server = LinkFeedTestServer()
    >>> cl = LinkFeedClient(user = 'user123456789', db_driver = ('mem',),
    ...                 use_xml = True, xml_server_list = [test_server.url])
    >>> lx = cl.get_raw_links(PageRequest(url = 'http://example.com/'))
    >>> lx[0]
    u'<!--12345--><a href="url1">link1</a><!--12345-->'
    >>> lx[1]
    u'<!--12345--><a href="url2">link2</a><!--12345-->'
    >>> cl = LinkFeedClient(user = 'user123456789', db_driver = ('mem',),
    ...                 use_xml = True, xml_server_list = ['file:///does_not_exists'])
    >>> cl.get_raw_links(PageRequest(url = 'http://example.com/'))
    []
    >>> cl.get_raw_links(PageRequest(url = 'http://example.com/'))
    []
    """
    
    server_list = [
            'http://db.linkfeed.ru/%(user)s/%(host)s/UTF-8']
    xml_server_list = [
            'http://db.linkfeed.ru/%(user)s/%(host)s/UTF-8.xml']

    def get_links_new_page(self, data, request):
        if self.force_show_code or self.is_bot(data, request):
            if (data.get('__linkfeed_start__', '') +
                    data.get('__linkfeed_end__', '')):
                return ['']
        return []

    def get_delimiter(self, data, request):
        return data.get('__linkfeed_delimiter__', '')

    def is_bot(self, data, request):
        bot_ips = data.get('__linkfeed_robots__', [])
        return request.remote_addr and request.remote_addr in bot_ips

    def transform_code(self, data, request, code):
        if self.force_show_code or self.is_bot(data, request):
            start = data.get('__linkfeed_start__', '')
            end = data.get('__linkfeed_end__', '')
        else:
            start = end = u''
        if code:
            before_text = data.get('__linkfeed_before_text__', '')
            after_text = data.get('__linkfeed_after_text__', '')
        else:
            before_text = after_text = u''
        return start + before_text + code + after_text + end

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
                if path == ['data', 'pages','page']:
                    data.expandNode(node)
                    path.pop()
                    uri = normalize_uri(node.getAttribute('url'))
                    link_nodes = node.getElementsByTagName('link')
                    yield (uri, [self.parse_link(node_text(x))
                        for x in link_nodes])
                elif path == ['data', 'config', 'item']:
                    data.expandNode(node)
                    path.pop()
                    name = str(node.getAttribute('name'))
                    if name:
                        yield ("__linkfeed_%s__" % name,
                                node_text(node))
                elif path == ['data', 'bot_ips']:
                    data.expandNode(node)
                    path.pop()
                    ip_nodes = node.getElementsByTagName('ip')
                    yield ("__linkfeed_robots__",
                            [node_text(x) for x in ip_nodes])
            elif event == xml.dom.pulldom.END_ELEMENT:
                path.pop()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
