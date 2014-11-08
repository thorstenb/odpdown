#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from lpod.style import odf_create_style
from lpod.paragraph import odf_create_paragraph, odf_span
from lpod.element import odf_create_element

# really quite an ugly hack. but unfortunately, mistune at a few
# non-overridable places use '+' and '+=' to concatenate render method
# returns. Due to the nature of the parser, to preserve output
# ordering, we need to return odf partial trees in our own render
# methods (that will then need to be concatenated via +/+=).
class ODFPartialTree:
    def __init__(self, elements):
        self._elements = elements

    def _add_text(self, text):
        span = odf_create_element('text:span')
        span.set_text(unicode(text))
        self._elements.append( span )

    def __add__(self, other):
        tmp = ODFPartialTree(list(self._elements))
        if isinstance(other, str):
            tmp._add_text(other)
        else:
            tmp._elements += other._elements
        return tmp

    def __iadd__(self, other):
        if isinstance(other, str):
            self._add_text(other)
        else:
            self._elements += other._elements
        return self

    def __copy__(self):
        return ODFPartialTree(self._elements[:])

    def get(self):
        return self._elements


class ODFRenderer(mistune.Renderer):
    def __init__(self, document):
        self.document = document
        self.page = None
        self.page_content = ODFPartialTree([])
        self.add_style('text', u'TextEmphasisStyle',
                       [('text', {'font_style': u'italic'})])
        self.add_style('text', u'TextDoubleEmphasisStyle',
                       [('text', {'font_style': u'italic', 'font_weight': u'bold'})])
        self.add_style('text', u'TextQuoteStyle',
                       # TODO: font size increase does not work currently
                       [('text', {'size': u'150%',
                                  'color': u'#ccf4c6'})])
        self.add_style('paragraph', u'ParagraphQuoteStyle',
                       [('text', {'color': u'#18a303'}),
                        ('paragraph', {'margin_left': u'0.5cm',
                                       'margin_right': u'0.5cm',
                                       'margin_top': u'0.5cm',
                                       'margin_bottom': u'0.5cm',
                                       'text_indent': u'-0.5cm'})])
        self.add_style('text', u'TextCodeStyle',
                       # TODO: neither font, nor font size work currently
                       [('text', {'size': u'110%',
                                  'font_name': u'Courier', 'font_family': u'monospaced'})])
        self.add_style('paragraph', u'ParagraphCodeStyle',
                       # TODO: neither font, nor font size work currently
                       [('text', {'size': u'110%',
                                  'font_name': u'Courier', 'font_family': u'monospaced'}),
                        ('paragraph', {'margin_left': u'0.5cm',
                                       'margin_right': u'0.5cm',
                                       'margin_top': u'0.5cm',
                                       'margin_bottom': u'0.5cm',
                                       'text_indent': u'0cm'})])

    def add_style(self, style_family, style_name, properties):
        """Insert global style into document"""
        style = odf_create_style (
            style_family,
            name=style_name)
        for elem in properties:
            style.set_properties(properties=elem[1], area=elem[0])
        self.document.insert_style(style, automatic=True)

    def wrap_spans(self, odf_elements):
        '''For any homogeneous toplevel range of text:span elements, wrap them
           into a paragraph'''
        res = []
        para = None
        for elem in odf_elements:
            if isinstance(elem, odf_span):
                if para is None:
                    para = odf_create_paragraph()
                para.append(elem)
            else:
                if para is not None:
                    res.append(para)
                    para = None
                res.append(elem)
        if para is not None:
            res.append(para)
        return res

    def finalize_page(self):
        if len(self.page_content.get()):
            if self.page is None:
                # don't drop content just b/c there's no page
                self.page = odf_create_draw_page(
                    'page1',
                    name='page1',
                    master_page=u'Logo_20_Content',
                    presentation_page_layout=u'AL3T1')

            frame = odf_create_text_frame(
                self.page_content.get(),
                presentation_style=u'pr5',
                size = (u'22cm', u'12cm'),
                position = (u'2cm', u'5cm'),
                presentation_class = u'outline')
            self.page.append(frame)

    def finalize(self):
        self.finalize_page()
        if self.page is not None:
            self.document.get_body().append(self.page)

    def block_code(self, code, language=None):
        self.page_content = ODFPartialTree(
            [odf_create_paragraph(code,
                                  style=u'ParagraphCodeStyle')])
        return self.page_content

    def header(self, text, level, raw=None):
        self.finalize()
        if level == 1:
            self.page = odf_create_draw_page(
                'page1',
                name=''.join(e.get_formatted_text() for e in text.get()),
                master_page=u'Break',
                presentation_page_layout=u'AL3T19')
            self.page.append(
                odf_create_text_frame(
                    self.wrap_spans(text.get()),
                    presentation_style=u'pr7',
                    size = (u'20cm', u'3cm'),
                    position = (u'2cm', u'8cm'),
                    presentation_class = u'title'))
        elif level == 2:
            self.page = odf_create_draw_page(
                'page1',
                name=''.join(e.get_formatted_text() for e in text.get()),
                master_page=u'Logo_20_Content',
                presentation_page_layout=u'AL3T1')
            self.page.append(
                odf_create_text_frame(
                    self.wrap_spans(text.get()),
                    presentation_style=u'pr4',
                    size = (u'20cm', u'3cm'),
                    position = (u'2cm', u'1cm'),
                    presentation_class = u'title'))
        else:
            raise RuntimeError('Unsupported heading level: %d' % level)

        self.page_content = ODFPartialTree([])
        return self.page_content

    def block_quote(self, text):
        para = odf_create_paragraph(style=u'ParagraphQuoteStyle')
        span = odf_create_element('text:span')
        span.set_text(u'“')
        para.append(span)

        span = odf_create_element('text:span')
        for elem in text.get():
            span.append(elem)
        para.append(span)

        span = odf_create_element('text:span')
        span.set_text(u'”')
        para.append(span)

        para.set_span(u'TextQuoteStyle', regex=u'“')
        para.set_span(u'TextQuoteStyle', regex=u'”')
        self.page_content = ODFPartialTree([para])
        return self.page_content

    def list_item(self, text):
        item = odf_create_list_item()
        for elem in self.wrap_spans(text.get()):
            item.append(elem)
        self.page_content = ODFPartialTree([item])
        return self.page_content

    def list(self, body, ordered=True):
        lst = odf_create_list(style=u'L6' if ordered else u'L1')
        for elem in body.get():
            lst.append(elem)
        self.page_content = ODFPartialTree([lst])
        return self.page_content

    def paragraph(self, text):
        # yes, this seem broadly illogical. but most 'paragraphs'
        # actually end up being parts of tables, quotes, list items
        # etc, which might not always permit text:p
        span = odf_create_element('text:span')
        for elem in text.get():
            span.append(elem)
        self.page_content = ODFPartialTree([span])
        return self.page_content

    def table(self, header, body):
        pass

    def table_row(self, content):
        pass

    def table_cell(self, content, **flags):
        pass

    def autolink(self, link, is_email=False):
        text = link
        if is_email:
            link = 'mailto:%s' % link
        lnk = odf_create_link(link, text=unicode(text))
        self.page_content = ODFPartialTree([lnk])
        return self.page_content

    def link(self, link, title, content):
        lnk = odf_create_link(link, text=unicode(content), title=unicode(title))
        self.page_content = ODFPartialTree([lnk])
        return self.page_content

    def codespan(self, text):
        span = odf_create_element('text:span')
        span.set_style('TextCodeStyle')
        if isinstance(text, str):
            span.set_text(unicode(text))
        else:
            for elem in text.get():
                span.append(elem)
        self.page_content = ODFPartialTree([span])
        return self.page_content

    def double_emphasis(self, text):
        span = odf_create_element('text:span')
        span.set_style('TextDoubleEmphasisStyle')
        for elem in text.get():
            span.append(elem)
        self.page_content = ODFPartialTree([span])
        return self.page_content

    def emphasis(self, text):
        span = odf_create_element('text:span')
        span.set_style('TextEmphasisStyle')
        for elem in text.get():
            span.append(elem)
        self.page_content = ODFPartialTree([span])
        return self.page_content

    def image(self, src, title, alt_text):
        pass

    def linebreak(self):
        self.page_content = ODFPartialTree([odf_create_line_break()])
        return self.page_content

    def tag(self, html):
        pass

    def strikethrough(self, text):
        pass

mkdwn_in = sys.argv[1]
odf_in = sys.argv[2]
odf_out = sys.argv[3]
presentation = odf_get_document(odf_in)

odf_renderer = ODFRenderer(presentation)
mkdown = mistune.Markdown(renderer=odf_renderer,
                          output_init=ODFPartialTree([]))

markdown = open(mkdwn_in, 'r')

mkdown.render(markdown.read())
odf_renderer.finalize()

presentation.save(target=odf_out, pretty=True)
