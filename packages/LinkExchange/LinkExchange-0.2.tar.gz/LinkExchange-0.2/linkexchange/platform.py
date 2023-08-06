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

from linkexchange.utils import is_plugin_specifier, load_plugin
from linkexchange.clients.base import ClientError, PageRequest

class Platform(object):
    """
    Platform combines various clients into one object. It have methods to get
    total list of raw links, to get links divided by blocks with custom
    formatting rules.

    >>> from linkexchange.clients.sape import SapeTestServer
    >>> srv = SapeTestServer()
    >>> clients = [('sape', [], dict(user = 'user123456789',
    ...    db_driver = ('mem',),
    ...    use_xml = True, xml_server_list = [srv.url]))]
    >>> pl = Platform(clients = clients)
    >>> lx = pl.get_raw_links('http://example.com/')
    >>> lx[0]
    u'<a href="url1">link1</a>'
    >>> lx[1]
    u'<a href="url2">link2</a>'
    >>> formatters = [('inline', [2], dict(
    ...    class_ = 'links', class_for_empty = 'empty', suffix = '. ')),
    ...    ('list', [2], dict(id = 'links'))]
    >>> bx = pl.get_blocks('http://example.com/', formatters)
    >>> bx[0]
    u'<div class="links"><a href="url1">link1</a>. <a href="url2">link2</a>. </div>'
    >>> bx[1]
    u'<span id="links"></span>'
    >>> bx = pl.get_blocks('http://example.com/notexists', formatters)
    >>> bx[0]
    u'<div class="empty"></div><!--12345-->'
    >>> bx[1]
    u'<span id="links"></span>'
    >>> bx = pl.get_blocks('http://example.com/path/1', formatters)
    >>> bx[0]
    u'<div class="links"><a href="url1">link1</a>. <a href="url2">link2</a>. </div>'
    >>> bx[1]
    u'<ul id="links"><li><a href="url3">link3</a></li><li><a href="url4">link4</a></li></ul>'
    """

    def __init__(self, clients = None):
        """
        @param clients: list of clients instances or clients specifiers

        """
        self.clients = []
        if clients:
            for cl in clients:
                self.add_client(cl)

    def add_client(self, client):
        """
        Add link exchange service client to the platform.

        The client parameter is instance of BaseClient or client specifier.
        Client specifier is (name, args, kwargs) tuple where name is client
        name (link exchange service name), args and kwargs is list of
        positional arguments and dictionary of keyword arguments for the client
        constructor respectively.

        @param client: instance of BaseClient or client specifier
        """
        if is_plugin_specifier(client):
            client = load_plugin('linkexchange.clients', client)
        self.clients.append(client)

    def get_raw_links(self, request):
        """
        Returns list of links, just like clients returns, but catches clients
        errors and use HTML comments for errors reporting.

        @param request: PageRequest object or URL string
        @return: list of links as unicode strings
        """
        if isinstance(request, basestring):
            request = PageRequest(url = request)
        result = []
        for cl in self.clients:
            try:
                links = cl.get_raw_links(request)
            except ClientError, e:
                links = [u'<!-- %s -->' % str(e)]
            result.extend(links)
        return result

    def get_blocks(self, request, formatters):
        """
        Returns links grouped by blocks. Catches clients errors and use HTML
        comments for errors reporting.

        The request parameter is a PageRequest object or URL string. The
        formatters parameter is a sequence of BaseFormatter instances. The
        result is list of unicode strings with HTML formatted blocks of links.

        @param request: PageRequest object or URL string
        @param formatters: sequence of blocks formatters
        @return: list of links blocks as unicode strings
        """
        links = self.get_raw_links(request)
        blocks = []

        for fmt in formatters:
            if is_plugin_specifier(fmt):
                fmt2 = load_plugin('linkexchange.formatters', fmt)
            else:
                fmt2 = fmt
            tag_list = []
            link_list = []
            while links and ((fmt2.count and
                len(link_list) < fmt2.count) or (not fmt2.count)):
                x = links.pop(0)
                if '<a ' in x:
                    link_list.append(x)
                else:
                    tag_list.append(x)
            blocks.append(fmt2.format(tag_list, link_list))
        return blocks

    def content_filter(self, request, content):
        """
        @param request: PageRequest object or URL string
        @param content: HTML content (full page or fragment) as unicode string
        @return: filtered content as unicode string
        """
        if isinstance(request, basestring):
            request = PageRequest(url = request)
        for cl in self.clients:
            try:
                content = cl.content_filter(request, content)
            except ClientError, e:
                pass
        return content

    def refresh_db(self, request):
        """
        Force to refresh clients databases.

        @param request: PageRequest object or URL string
        """
        if isinstance(request, basestring):
            request = PageRequest(url = request)
        for cl in self.clients:
            try:
                cl.refresh_db(request)
            except ClientError, e:
                pass

if __name__ == "__main__":
    import doctest
    doctest.testmod()
