# -*- coding: utf-8 -*-
"""Generate OpenDocument Presentation (odp) files from markdown"""

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
import mistune
import argparse
import urlparse
import codecs
import sys
import re

from urllib import urlopen
from mimetypes import guess_type

from lpod import ODF_MANIFEST, ODF_STYLES
from lpod.document import odf_get_document
from lpod.frame import odf_create_text_frame, odf_create_image_frame, odf_frame
from lpod.draw_page import odf_create_draw_page, odf_draw_page
from lpod.list import odf_create_list_item, odf_create_list
from lpod.style import odf_create_style
from lpod.paragraph import odf_create_paragraph, odf_span
from lpod.paragraph import odf_create_line_break, odf_create_spaces
from lpod.paragraph import odf_create_tabulation
from lpod.element import odf_create_element
from lpod.link import odf_create_link, odf_link

from pygments.lexers import get_lexer_by_name
from pygments.formatter import Formatter

__version__ = '0.4.0'
__author__ = 'Thorsten Behrens <tbehrens@acm.org>'
__all__ = [
    'ODFRenderer', 'ODFRenderer',
    'ODFFormatter', 'ODFFormatter',
    'ODFPartialTree', 'ODFPartialTree',
]

_master_page_spew = '''
Available master page names in template:
----------------------------------------

    For  visual  inspection,  select  View->Master->Slide  Master  in
    Impress. The names listed below are the slide names of the master
    pages you  see in the  slide preview  pane. Hover over  the slide
    thumbnails to  have them  displayed, right-click and  pick Rename
    Master to choose more speaking names.

'''.strip()


# helper for ODFFormatter and ODFRenderer
def add_style(document, style_family, style_name,
              properties, parent=None):
    """Insert global style into given document"""
    style = odf_create_style(style_family, style_name,
                             style_name, parent)
    for elem in properties:
        # pylint: disable=maybe-no-member
        style.set_properties(properties=elem[1], area=elem[0])
    document.insert_style(style, automatic=True)


def wrap_spans(odf_elements):
    """For any homogeneous toplevel range of text:span elements, wrap them
       into a paragraph"""
    res = []
    para = None
    for elem in odf_elements:
        if isinstance(elem, odf_span) or isinstance(elem, odf_link):
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

# buffer regex for tab/space splitting for block code
_whitespace_re = re.compile(u'( {2,}|\t)', re.UNICODE)


def handle_whitespace(text):
    """Add ODF whitespace processing and ODF linebreak elements into
       multi-line text. Returns list with mixed unicode and odf
       elements."""
    result = []
    lines = text.split('\n')
    for index, line in enumerate(lines):
        # for every line
        for part in _whitespace_re.split(line):
            # split off tabulators and whitespace
            if part[:1] == ' ':
                # multiple spaces in ODF need markup
                result.append(
                    odf_create_spaces(len(part)))
            elif part[:1] == '\t':
                # insert an actual tab
                result.append(
                    odf_create_tabulation())
            else:
                result.append(
                    unicode(part))

        # for all but the last line: add linebreak
        if index < len(lines)-1:
            result.append(odf_create_line_break())

    return result


# really quite an ugly hack. but unfortunately, mistune at a few
# non-overridable places use '+' and '+=' to concatenate render method
# returns. Due to the nature of the parser, to preserve output
# ordering, we need to return odf partial trees in our own render
# methods (that will then need to be concatenated via +/+=).
class ODFPartialTree:
    """Output object for mistune, used to collect formatter fragments
       via +/+= operators"""
    def __init__(self, elements, outline_size, outline_position):
        self._elements = elements
        self.outline_size = outline_size
        self.outline_position = outline_position

    @classmethod
    def from_metrics_provider(cls, elements, metrics_provider):
        """Initialize ODFPartialTree from a metrics provider"""
        return cls(elements,
                   metrics_provider.outline_size,
                   metrics_provider.outline_position)

    def add_child_elems(self, elems):
        """Helper to add elems to self as children"""
        # TODO: kill this ugly typeswitching
        if (len(self._elements) and
            isinstance(
                self._elements[-1], odf_draw_page) and not
            isinstance(
                elems[0], odf_draw_page)):

            # stick additional frame content into last existing one
            for child in self._elements[-1].get_elements(
                    'descendant::draw:frame'):
                if child.get_presentation_class() == u'outline':
                    text_box = child.get_children()[0]
                    for elem in wrap_spans(elems):
                        text_box.append(elem)
                    return

            # special-case image frames - append to pages literally!
            if isinstance(elems[0], odf_frame):
                for child in elems:
                    self._elements[-1].append(child)
            else:
                # no outline frame found, create new one with elems content
                elems = wrap_spans(elems)
                self._elements[-1].append(
                    odf_create_text_frame(
                        elems,
                        presentation_style=u'md2odp-OutlineText',
                        size=(u'%s' % self.outline_size[0],
                              u'%s' % self.outline_size[1]),
                        position=(u'%s' % self.outline_position[0],
                                  u'%s' % self.outline_position[1]),
                        presentation_class=u'outline'))
        else:
            self._elements += elems

    def add_text(self, text):
        """Helper to ctext to self"""
        span = odf_create_element('text:span')
        span.set_text(unicode(text))
        self._elements.append(span)

    def __add__(self, other):
        """Override of +"""
        tmp = ODFPartialTree(list(self._elements),
                             self.outline_size,
                             self.outline_position)
        if isinstance(other, basestring):
            tmp.add_text(other)
        else:
            tmp.add_child_elems(other.get())
        return tmp

    def __iadd__(self, other):
        """Override of +="""
        if isinstance(other, basestring):
            self.add_text(other)
        else:
            self.add_child_elems(other.get())
        return self

    def __copy__(self):
        """Override for deep copy"""
        return ODFPartialTree(self._elements[:],
                              self.outline_size,
                              self.outline_position)

    def get(self):
        """Get list of odf_element elements"""
        return self._elements


# parts from http://pygments.org/docs/formatterdevelopment/, BSD
# license
class ODFFormatter(Formatter):
    """Format pygment token stream as ODF"""
    def __init__(self, **options):
        Formatter.__init__(self, **options)

        # buffer regex for tab/space splitting for block code
        self.whitespace_re = re.compile(u'( {2,}|\t)', re.UNICODE)

        # create a dict of (start, end) tuples that wrap the
        # value of a token so that we can use it in the format
        # method later
        self.styles = {}

        # we iterate over the `_styles` attribute of a style item
        # that contains the parsed style values.
        for token, style in self.style:
            root_elem = None
            curr_elem = None
            # a style item is a tuple in the following form:
            # colors are readily specified in hex: 'RRGGBB'
            if style['color']:
                root_elem = curr_elem = odf_create_element('text:span')
                # pylint: disable=maybe-no-member
                curr_elem.set_style('md2odp-TColor%s' % style['color'])

            if style['bold']:
                span = odf_create_element('text:span')
                # pylint: disable=maybe-no-member
                span.set_style('md2odp-TBold')
                if root_elem is None:
                    root_elem = curr_elem = span
                else:
                    curr_elem.append(span)
                    curr_elem = span

            if style['italic']:
                span = odf_create_element('text:span')
                # pylint: disable=maybe-no-member
                span.set_style('md2odp-TItalic')
                if root_elem is None:
                    root_elem = curr_elem = span
                else:
                    curr_elem.append(span)
                    curr_elem = span

            if style['underline']:
                span = odf_create_element('text:span')
                # pylint: disable=maybe-no-member
                span.set_style('md2odp-TUnderline')
                if root_elem is None:
                    root_elem = curr_elem = span
                else:
                    curr_elem.append(span)
                    curr_elem = span

            self.styles[token] = (root_elem, curr_elem)

    def add_style_defs(self, document):
        """Add needed odf autostyles to document"""
        # we iterate over the `_styles` attribute of a style item
        # that contains the parsed style values.
        for token, style in self.style:
            # a style item is a tuple in the following form:
            # colors are readily specified in hex: 'RRGGBB'
            if style['color']:
                add_style(document, 'text',
                          u'md2odp-TColor%s' % style['color'],
                          [('text', {'color': u'#'+style['color']})])
            if style['bold']:
                add_style(document, 'text', u'md2odp-TBold',
                          [('text', {'font_weight': u'bold'})])
            if style['italic']:
                add_style(document, 'text', u'md2odp-TItalic',
                          [('text', {'font_style': u'italic'})])
            if style['underline']:
                add_style(document, 'text', u'md2odp-TUnderline',
                          [('text', {'text_underline_style': u'solid',
                                     'text_underline_width': u'auto',
                                     'text_underline_color': u'font-color'})])

    def format(self, tokensource):
        result = []

        # lastval is a string we use for caching because it's possible
        # that an lexer yields a number of consecutive tokens with the
        # same token type.  to minimize the size of the generated
        # markup we try to join the values of same-type tokens here
        lastval = ''
        lasttype = None

        for ttype, value in tokensource:
            # if the token type doesn't exist in the stylemap
            # we try it with the parent of the token type
            # eg: parent of Token.Literal.String.Double is
            # Token.Literal.String
            while ttype not in self.styles:
                ttype = ttype.parent
            if ttype == lasttype:
                # the current token type is the same of the last
                # iteration. cache it
                lastval += value
            else:
                # not the same token as last iteration, but we
                # have some data in the buffer. wrap it with the
                # defined style and write it to the output file
                if lastval:
                    root_span, leaf_span = self.styles[lasttype]

                    # white space and linefeeds: special handling
                    # needed in ODF
                    for elem in handle_whitespace(lastval):
                        if isinstance(elem, basestring):
                            if root_span is None:
                                span = odf_create_element('text:span')
                                span.set_text(elem)
                                result.append(span)
                            else:
                                # this is nasty - set text in
                                # shared style instance, clone
                                # afterwards
                                leaf_span.set_text(elem)
                                result.append(root_span.clone())
                        else:
                            result.append(elem)

                # set lastval/lasttype to current values
                lastval = value
                lasttype = ttype

        # something left in lastval? flush it now
        if lastval:
            root_span, leaf_span = self.styles[lasttype]
            if root_span is None:
                span = odf_create_element('text:span')
                span.set_text(unicode(lastval))
                result.append(span)
            else:
                # this is nasty - set text in shared style instance,
                # clone afterwards
                leaf_span.set_text(unicode(lastval))
                result.append(root_span.clone())

        return result


class ODFRenderer(mistune.Renderer):
    """Render mistune event stream as ODF"""
    image_prefix = 'odpdown_image_'

    def __init__(self,
                 document,
                 break_master=None,
                 breakheader_size=None,
                 breakheader_position=None,
                 content_master=None,
                 header_size=None,
                 header_position=None,
                 outline_size=None,
                 outline_position=None,
                 highlight_style='colorful',
                 autofit_text=True):
        mistune.Renderer.__init__(self)
        self.formatter = ODFFormatter(style=highlight_style)
        self.document = document
        self.doc_manifest = document.get_part(ODF_MANIFEST)
        # make sure nested odpdown calls don't end up writing
        # similarly-named images
        self.image_entry_id = len([path for path in
                                   self.doc_manifest.get_paths()
                                   if path.startswith(
                                           ODFRenderer.image_prefix)])
        self.break_master = 'Default' if break_master is None else break_master
        self.breakheader_size = ((u'20cm', u'3cm') if breakheader_size is None
                                 else breakheader_size)
        self.breakheader_position = (
            (u'2cm', u'8cm') if breakheader_position is None
            else breakheader_position)
        self.content_master = ('Default' if content_master is None
                               else content_master)
        self.header_size = ((u'20cm', u'3cm') if header_size is None
                            else header_size)
        self.header_position = ((u'2cm', u'0.5cm') if header_position is None
                                else header_position)
        self.outline_size = ((u'22cm', u'12cm') if outline_size is None
                             else outline_size)
        self.outline_position = ((u'2cm', u'4cm') if outline_position is None
                                 else outline_position)

        # font/char styles
        self.document.insert_style(
            odf_create_style(
                'font-face',
                name=u'Nimbus Mono L',
                font_name=u'Nimbus Mono L',
                font_family=u'Nimbus Mono L',
                font_family_generic=u'modern',
                font_pitch=u'fixed'),
            automatic=True)
        add_style(document, 'text', u'md2odp-TextEmphasisStyle',
                  [('text', {'font_style': u'italic'})])
        add_style(document, 'text', u'md2odp-TextDoubleEmphasisStyle',
                  [('text', {'font_weight': u'bold'})])
        add_style(document, 'text', u'md2odp-TextQuoteStyle',
                  # TODO: font size increase does not work currently
                  # Bug in Impress:
                  # schema has his - for _all_ occurences
                  #  <attribute name="fo:font-size">
                  #    <choice>
                  #      <ref name="positiveLength"/>
                  #      <ref name="percent"/>
                  #    </choice>
                  #  </attribute>
                  [('text', {'size': u'200%',
                             'color': u'#ccf4c6'})])
        add_style(document, 'text', u'md2odp-TextCodeStyle',
                  [('text', {'style:font_name': u'Nimbus Mono L'})])

        # paragraph styles
        add_style(document, 'paragraph', u'md2odp-ParagraphQuoteStyle',
                  [('text', {'color': u'#18a303'}),
                   ('paragraph', {'margin_left': u'0.5cm',
                                  'margin_right': u'0.5cm',
                                  'margin_top': u'0.6cm',
                                  'margin_bottom': u'0.5cm',
                                  'text_indent': u'-0.6cm'})])
        add_style(document, 'paragraph', u'md2odp-ParagraphCodeStyle',
                  [('text', {'style:font_name': u'Nimbus Mono L'}),
                   ('paragraph', {'margin_left': u'0.5cm',
                                  'margin_right': u'0.5cm',
                                  'margin_top': u'0.6cm',
                                  'margin_bottom': u'0.6cm',
                                  'text_indent': u'0cm'})])
        # graphic styles
        add_style(document, 'graphic', u'md2odp-ImageStyle',
                  [('graphic', {'stroke': u'none',
                                'fille':  u'none',
                                'draw:textarea_horizontal_align': u'right',
                                'draw:textarea-vertical-align':   u'bottom'})])

        # presentation styles
        add_style(document, 'presentation', u'md2odp-OutlineText',
                  ([('graphic',
                     {'draw:fit_to_size': u'shrink-to-fit'})] if autofit_text
                   else [('graphic',
                          {'draw:auto_grow_height': u'true'})]),
                  self.content_master + '-outline1')
        add_style(document, 'presentation', u'md2odp-TitleText',
                  [('graphic', {'draw:auto_grow_height': u'true'})],
                  self.content_master + '-title')
        add_style(document, 'presentation', u'md2odp-BreakTitleText',
                  [('graphic', {'draw:auto_grow_height': u'true'})],
                  self.break_master + '-title')

        # clone list style out of content master page (an abomination
        # this is not referenceable out of the presentation style...)
        content_master_styles = [i for i in self.document.get_part(
            ODF_STYLES).get_elements(
                'descendant::style:style') if (
                    i.get_attribute('style:name') ==
                    self.content_master + '-outline1')]
        if len(content_master_styles):
            # now stick that under custom name into automatic style section
            list_style = content_master_styles[0].get_elements(
                'style:graphic-properties/text:list-style[1]')[0].clone()
            list_style.set_attribute('style:name', u'OutlineListStyle')
            document.insert_style(list_style, automatic=True)
        else:
            print 'WARNING: no outline list style found for ' \
                  'master page "%s"!' % self.content_master

        # delegate to pygments formatter for their styles
        self.formatter.add_style_defs(document)

    def placeholder(self):
        return ODFPartialTree.from_metrics_provider([], self)

    def block_code(self, code, language=None):
        para = odf_create_paragraph(style=u'md2odp-ParagraphCodeStyle')

        if language is not None:
            # explicit lang given, use syntax highlighting
            lexer = get_lexer_by_name(language)

            for span in self.formatter.format(lexer.get_tokens(code)):
                para.append(span)
        else:
            # no lang given, use plain monospace formatting
            for elem in handle_whitespace(code):
                if isinstance(elem, basestring):
                    span = odf_create_element('text:span')
                    span.set_text(elem)
                    para.append(span)
                else:
                    para.append(elem)

        return ODFPartialTree.from_metrics_provider([para], self)

    def header(self, text, level, raw=None):
        page = None
        if level == 1:
            page = odf_create_draw_page(
                'page1',
                name=''.join(e.get_formatted_text() for e in text.get()),
                master_page=self.break_master,
                presentation_page_layout=u'AL3T19')
            page.append(
                odf_create_text_frame(
                    wrap_spans(text.get()),
                    presentation_style=u'md2odp-BreakTitleText',
                    size=(u'%s' % self.breakheader_size[0],
                          u'%s' % self.breakheader_size[1]),
                    position=(u'%s' % self.breakheader_position[0],
                              u'%s' % self.breakheader_position[1]),
                    presentation_class=u'title'))
        elif level == 2:
            page = odf_create_draw_page(
                'page1',
                name=''.join(e.get_formatted_text() for e in text.get()),
                master_page=self.content_master,
                presentation_page_layout=u'AL3T1')
            page.append(
                odf_create_text_frame(
                    wrap_spans(text.get()),
                    presentation_style=u'md2odp-TitleText',
                    size=(u'%s' % self.header_size[0],
                          u'%s' % self.header_size[1]),
                    position=(u'%s' % self.header_position[0],
                              u'%s' % self.header_position[1]),
                    presentation_class=u'title'))
        else:
            raise RuntimeError('Unsupported heading level: %d' % level)

        return ODFPartialTree.from_metrics_provider([page], self)

    def block_quote(self, text):
        para = odf_create_paragraph(style=u'md2odp-ParagraphQuoteStyle')
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

        # pylint: disable=maybe-no-member
        para.set_span(u'md2odp-TextQuoteStyle', regex=u'“')
        para.set_span(u'md2odp-TextQuoteStyle', regex=u'”')
        return ODFPartialTree.from_metrics_provider([para], self)

    def list_item(self, text):
        item = odf_create_list_item()
        for elem in wrap_spans(text.get()):
            item.append(elem)
        return ODFPartialTree.from_metrics_provider([item], self)

    def list(self, body, ordered=True):
        # TODO: reverse-engineer magic to convert outline style to
        # numbering style
        lst = odf_create_list(style=u'L1' if ordered else u'OutlineListStyle')
        for elem in body.get():
            lst.append(elem)
        return ODFPartialTree.from_metrics_provider([lst], self)

    def paragraph(self, text):
        # images? insert as standalone frame, no inline img
        if isinstance(text.get()[0], odf_frame):
            return text
        else:
            # yes, this seem broadly illogical. but most 'paragraphs'
            # actually end up being parts of tables, quotes, list items
            # etc, which might not always permit text:p
            span = odf_create_element('text:span')
            for elem in text.get():
                span.append(elem)
            return ODFPartialTree.from_metrics_provider([span], self)

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
        return ODFPartialTree.from_metrics_provider([lnk], self)

    def link(self, link, title, content):
        lnk = odf_create_link(link,
                              text=content.get()[0].get_text(),
                              title=unicode(title))
        return ODFPartialTree.from_metrics_provider([lnk], self)

    def codespan(self, text):
        span = odf_create_element('text:span')
        # pylint: disable=maybe-no-member
        span.set_style('md2odp-TextCodeStyle')
        if isinstance(text, basestring):
            span.set_text(unicode(text))
        else:
            for elem in text.get():
                span.append(elem)
        return ODFPartialTree.from_metrics_provider([span], self)

    def double_emphasis(self, text):
        span = odf_create_element('text:span')
        # pylint: disable=maybe-no-member
        span.set_style('md2odp-TextDoubleEmphasisStyle')
        for elem in text.get():
            span.append(elem)
        return ODFPartialTree.from_metrics_provider([span], self)

    def emphasis(self, text):
        span = odf_create_element('text:span')
        # pylint: disable=maybe-no-member
        span.set_style('md2odp-TextEmphasisStyle')
        for elem in text.get():
            span.append(elem)
        return ODFPartialTree.from_metrics_provider([span], self)

    def image(self, src, title, alt_text):
        # embed picture - TODO: optionally just link it
        media_type = guess_type(src)
        fragment_ext = urlparse.urlparse(src)[2].split('.')[-1]
        fragment_name = 'Pictures/%s%d.%s' % (ODFRenderer.image_prefix,
                                              self.image_entry_id,
                                              fragment_ext)
        imagedata = urlopen(src).read()
        try:
            if not fragment_ext.endswith('svg'):
                # delay our PIL dependency until really needed
                from PIL import Image
                import cStringIO

                imagefile = cStringIO.StringIO(imagedata)

                # obtain image aspect ratio
                image_w, image_h = Image.open(imagefile).size
            else:
                # PIL does not really support svg, so let's try heuristics
                # & find the aspect ratio ourselves
                from BeautifulSoup import BeautifulSoup

                imagefile = BeautifulSoup(imagedata)
                image_w = float(imagefile.svg['width'])
                image_h = float(imagefile.svg['height'])
        except:
            # unable to extract aspect ratio
            image_w, image_h = (100, 100)

        image_ratio = image_w / float(image_h)

        frame_x, frame_y = (2, 4)
        frame_w, frame_h = (22, 12)
        frame_ratio = frame_w / float(frame_h)

        if image_ratio > frame_ratio:
            image_w = frame_w
            image_h = int(frame_w / image_ratio)
            frame_y += (frame_h - image_h) / 2
        else:
            image_w = int(frame_h * image_ratio)
            image_h = frame_h
            frame_x += (frame_w - image_w) / 2

        args = {'style': u'md2odp-ImageStyle',
                'size': (u'%dcm' % image_w, u'%dcm' % image_h),
                'position': (u'%dcm' % frame_x, u'%dcm' % frame_y),
                'presentation_class': u'graphic'}
        if title is not None:
            args['text'] = unicode(title)
        frame = odf_create_image_frame(fragment_name, **args)

        if alt_text is not None:
            frame.set_svg_description(unicode(alt_text))

        self.doc_manifest.add_full_path(fragment_name,
                                        media_type[0])
        self.document.set_part(fragment_name,
                               imagedata)
        self.image_entry_id += 1
        return ODFPartialTree.from_metrics_provider([frame], self)

    def linebreak(self):
        return ODFPartialTree.from_metrics_provider([odf_create_line_break()],
                                                    self)

    def tag(self, html):
        pass

    def strikethrough(self, text):
        pass

    def text(self, text):
        return text


def main():
    """Command-line conversion tool"""
    parser = argparse.ArgumentParser(
        description='Convert markdown text into OpenDocument presentations')
    parser.add_argument('input_md',
                        help='Input markdown file')
    parser.add_argument('template_odp',
                        type=argparse.FileType('r'),
                        help='Input ODP template file')
    parser.add_argument('output_odp',
                        type=argparse.FileType('w'),
                        help='Output ODP file')
    parser.add_argument('-p', '--page', default=-1, type=int,
                        help='Append markdown after given page. Negative '
                        'numbers count from the end of the slide stack. '
                        '[Defaults to -1]')
    parser.add_argument('-n', '--no-autofit',
                        default=True,
                        action='store_false',
                        help='Use to disable auto-shrinking '
                        'font in text boxes, to fit available space.')
    parser.add_argument('-s', '--highlight-style', default='colorful',
                        help='Set pygments color style for syntax-'
                        'highlighting of code snippets. Available styles in '
                        'stock pygments are: "default", "emacs", "friendly",'
                        ' and "colorful". [Defaults to colorful]')
    parser.add_argument('--break-master', nargs='?', const='', default=None,
                        help='Use this master page for the 1st level'
                        ' headlines. List available ones if called with empty'
                        ' or unknown name')
    parser.add_argument('--content-master', nargs='?', const='', default=None,
                        help='Use this master page for the 2nd level headlines'
                        ' and content. List available ones if called with'
                        ' empty or unknown name')
    args = parser.parse_args()

    markdown = (codecs.getreader("utf-8")(sys.stdin) if args.input_md == '-'
                else codecs.open(args.input_md, 'r', encoding='utf-8'))
    odf_in = args.template_odp
    odf_out = args.output_odp
    presentation = odf_get_document(odf_in)

    master_pages = presentation.get_part(ODF_STYLES).get_elements(
        'descendant::style:master-page')
    master_names = [i.get_attribute('style:name') for i in master_pages]
    if ((args.break_master is not None and
         args.break_master not in master_names) or
        (args.content_master is not None and
         args.content_master not in master_names)):

        print _master_page_spew + '\n'
        for i in master_names:
            print ' - ' + i
        return

    breakheader_size = None
    breakheader_position = None
    header_size = None
    header_position = None
    outline_size = None
    outline_position = None

    # extract position and size of master page placeholders
    for page in master_pages:
        master_name = page.get_attribute('style:name')
        if master_name == args.break_master:
            frames = page.get_elements('descendant::draw:frame')
            for frame in frames:
                attr = frame.get_attribute('presentation:class')
                if attr is not None and attr == 'title':
                    breakheader_size = (frame.get_attribute('svg:width'),
                                        frame.get_attribute('svg:height'))
                    breakheader_position = (frame.get_attribute('svg:x'),
                                            frame.get_attribute('svg:y'))
        elif master_name == args.content_master:
            frames = page.get_elements('descendant::draw:frame')
            for frame in frames:
                attr = frame.get_attribute('presentation:class')
                if attr is not None and attr == 'title':
                    header_size = (frame.get_attribute('svg:width'),
                                   frame.get_attribute('svg:height'))
                    header_position = (frame.get_attribute('svg:x'),
                                       frame.get_attribute('svg:y'))
                elif attr is not None and attr == 'outline':
                    outline_size = (frame.get_attribute('svg:width'),
                                    frame.get_attribute('svg:height'))
                    outline_position = (frame.get_attribute('svg:x'),
                                        frame.get_attribute('svg:y'))

    odf_renderer = ODFRenderer(presentation,
                               break_master=args.break_master,
                               breakheader_size=breakheader_size,
                               breakheader_position=breakheader_position,
                               content_master=args.content_master,
                               header_size=header_size,
                               header_position=header_position,
                               outline_size=outline_size,
                               outline_position=outline_position,
                               autofit_text=args.no_autofit,
                               highlight_style=args.highlight_style)
    mkdown = mistune.Markdown(renderer=odf_renderer)

    doc_elems = presentation.get_body()
    if args.page < 0:
        args.page = len(doc_elems.get_children()) + args.page

    pages = mkdown.render(markdown.read())
    if isinstance(pages, ODFPartialTree):
        # pylint: disable=maybe-no-member
        for index, page in enumerate(pages.get()):
            doc_elems.insert(page, position=args.page + index)

        presentation.save(target=odf_out, pretty=False)

if __name__ == "__main__":
    main()
