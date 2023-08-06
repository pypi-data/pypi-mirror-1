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

import logging
import re

from trac.core import *
from trac.web import IRequestFilter, ITemplateStreamFilter
from genshi import XML, ParseError
from genshi.output import XMLSerializer

from linkexchange.trac import support
from linkexchange.utils import rearrange_blocks, parse_rearrange_map

log = logging.getLogger('linkexchange.trac')

class LinkExchangePlugin(Component):
    implements(IRequestFilter)
    implements(ITemplateStreamFilter)

    def __init__(self):
        super(LinkExchangePlugin, self).__init__(self)
        support.configure(self)
        self.lx_filter_template_match = re.compile(
                self.lx_options.get('filter_template_match',
                    '^wiki_view\.html$'))
    
    def pre_process_request(self, req, handler):
        return handler

    def post_process_request(self, req, template, data, content_type):
        if data is None:
            return (template, data, content_type)
        if self.lx_platform is None:
            return (template, data, content_type)

        lx_request = support.convert_request(req, self.lx_options)

	if self.lx_formatters:
            data['linkexchange_blocks'] = self.lx_platform.get_blocks(
                    lx_request, self.lx_formatters)
            try:
                rearrange_map = parse_rearrange_map(
                        self.lx_options['rearrange_map'])
            except KeyError:
                pass
            except ValueError:
                log.warning("Unable to parse rearrange_map")
            else:
                data['linkexchange_blocks'] = rearrange_blocks(page_request,
                        data['linkexchange_blocks'], rearrange_map)

        if self.lx_options.get('use_raw_links', False):
            data['linkexchange_links'] = self.lx_platform.get_raw_links(
                    lx_request)

        return (template, data, content_type)

    def filter_stream(self, req, method, filename, stream, data):
        if method != 'xhtml':
            return stream
        if self.lx_platform is None:
            return stream
        if not self.lx_options.get('content_filtering', False):
            return stream
        if not self.lx_filter_template_match.match(filename):
            return stream

        log.debug("Filtering event stream: method=%s; filename=%s",
                method, filename)

        content = ''.join(XMLSerializer()(stream))
        lx_request = support.convert_request(req, self.lx_options)
        new_content = self.lx_platform.content_filter(lx_request, content)
        try:
            stream = XML(new_content)
        except ParseError:
            log.error("Error parsing XML", exc_info = True)
            log.debug("Invalid XML data:\n%s", new_content)
            stream = XML(content)
        return stream
