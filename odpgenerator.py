#!/usr/bin/env python
#
# Copyright (c) 2014, Thorsten Behrens
# Copyright (c) 2010, Bart Hanssens
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

# use of lpod inspired by Bart Hanssens' odflinkchecker.py,
# https://lists.oasis-open.org/archives/opendocument-users/201008/msg00004.html
# and lpod-python-recipes
#
import sys
import mistune
from lpod.document import odf_get_document
from lpod.frame import odf_create_text_frame
from lpod.draw_page import odf_create_draw_page
from lpod.list import odf_create_list_item, odf_create_list

class ODFRenderer(mistune.Renderer):
    def __init__(self, document):
        self.document = document
        self.page = None
        self.textframe = None
        self.list_items = []

    def finalize(self):
        if self.page is not None:
            if self.textframe is not None:
                self.page.append(self.textframe)
            self.document.get_body().append(self.page)

    def paragraph(self, text):
        if self.page is not None:
            if self.textframe is not None:
                self.page.append(self.textframe)
        self.textframe = odf_create_text_frame(
            unicode(text),
            presentation_style=u'pr4',
            size = (u'22cm', u'12cm'),
            position = (u'2cm', u'5cm'),
            presentation_class = u'outline')
        return ''

    def list_item(self, text):
        self.list_items.append( odf_create_list_item( unicode(text)) )
        return ''

    def list(self, body, ordered=True):
        if self.page is not None:
            if self.textframe is not None:
                self.page.append(self.textframe)
                self.textframe = None
            lst = odf_create_list(style=u'L2')
            for i in self.list_items:
                lst.append(i)
            self.page.append(
                odf_create_text_frame(
                    lst,
                    presentation_style=u'pr4',
                    size = (u'22cm', u'12cm'),
                    position = (u'2cm', u'5cm'),
                    presentation_class = u'outline'))
        self.list_items = []
        return ''

    def header(self, text, level, raw=None):
        if self.page is not None:
            if self.textframe is not None:
                self.page.append(self.textframe)
                self.textframe = None
            self.document.get_body().append(self.page)
        self.page = odf_create_draw_page('page1', name=unicode(text),
                                         master_page=u'No-Logo_20_Content',
                                         presentation_page_layout=u'AL3T1')
        self.page.append(
            odf_create_text_frame(
                unicode(text),
                presentation_style=u'pr3',
                size = (u'20cm', u'3cm'),
                position = (u'2cm', u'1cm'),
                presentation_class = u'title'))
        return ''


mkdwn_in = sys.argv[1]
odf_in = sys.argv[2]
odf_out = sys.argv[3]
presentation = odf_get_document(odf_in)

odf_renderer = ODFRenderer(presentation)
mkdown = mistune.Markdown(renderer=odf_renderer)

markdown = open(mkdwn_in, 'r')
mkdown.render(markdown.read())
odf_renderer.finalize()

presentation.save(target=odf_out, pretty=True)
