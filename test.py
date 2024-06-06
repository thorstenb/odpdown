#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2014, Thorsten Behrens
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

import odpdown
import mistune
import codecs
from odfdo.const import ODF_MANIFEST
from odfdo.document import Document
from odfdo.draw_page import DrawPage
from nose.tools import with_setup, raises

testdoc = None
odf_renderer = None
mkdown = None


def setup():
    global testdoc, odf_renderer, mkdown
    testdoc = Document('presentation')
    odf_renderer = odpdown.ODFRenderer(testdoc,'Nimbus Mono L')
    mkdown = mistune.Markdown(renderer=odf_renderer)


@with_setup(setup)
def test_heading1():
    markdown = '# Heading 1'
    odf = mkdown.render(markdown)
    assert len(odf.get()) == 1
    assert isinstance(odf.get()[0], DrawPage)
    assert len(odf.get()[0].get_elements('descendant::draw:frame')) == 1
    assert odf.get()[0].get_elements(
        'descendant::text:span')[0].text == 'Heading 1'


@with_setup(setup)
def test_heading2():
    markdown = '## Heading 2'
    odf = mkdown.render(markdown)
    assert len(odf.get()) == 1
    assert isinstance(odf.get()[0], DrawPage)
    assert len(odf.get()[0].get_elements('descendant::draw:frame')) == 1
    assert odf.get()[0].get_elements(
        'descendant::text:span')[0].text == 'Heading 2'


@raises(RuntimeError)
@with_setup(setup)
def test_heading3():
    # headings of level 3 or higher not supported currently
    markdown = '### Heading 3'
    odf = mkdown.render(markdown)


@with_setup(setup)
def test_simple_page():
    markdown = '''
## Heading

This is a sample paragraph.
'''.strip()
    odf = mkdown.render(markdown)
    assert len(odf.get()) == 1
    assert len(odf.get()[0].get_elements('descendant::draw:frame')) == 2
    assert (odf.get()[0].get_elements('descendant::text:span')[0].text ==
            'Heading')
    assert (odf.get()[0].get_elements('descendant::text:span')[2].text ==
            'This is a sample paragraph.')


@with_setup(setup)
def test_items_page():
    markdown = '''
## Heading

* this is item one
* this is item two
  * and a subitem
'''.strip()
    odf = mkdown.render(markdown)
    assert len(odf.get()) == 1
    assert len(odf.get()[0].get_elements('descendant::draw:frame')) == 2
    assert (odf.get()[0].get_elements('descendant::text:span')[0].text ==
            'Heading')
    items = odf.get()[0].get_elements('descendant::text:list-item')
    assert len(items) == 3
    assert items[0].get_elements(
        'descendant::text:span')[0].text == 'this is item one'
    assert items[1].get_elements(
        'descendant::text:span')[0].text == 'this is item two'
    subitems = items[1].get_elements('descendant::text:list-item')
    assert len(subitems) == 1
    assert subitems[0].get_elements(
        'descendant::text:span')[0].text == 'and a subitem'


@with_setup(setup)
def test_empty_list_items_page():
    markdown = '''
## Heading

* a
* 
* c
'''.strip()
    odf = mkdown.render(markdown)
    assert len(odf.get()) == 1
    assert len(odf.get()[0].get_elements('descendant::draw:frame')) == 2
    items = odf.get()[0].get_elements('descendant::text:list-item')
    assert len(items) == 3
    assert items[0].get_elements(
        'descendant::text:span')[0].text == 'a'
    assert len(items[1].get_elements(
        'descendant::text:span')) == 0
    assert items[2].get_elements(
        'descendant::text:span')[0].text == 'c'


@with_setup(setup)
def test_xml_entity_escaping():
    markdown = '''
## Heading

There "is" <some> & 'the' other to escape
'''.strip()
    odf = mkdown.render(markdown)
    assert len(odf.get()) == 1
    assert len(odf.get()[0].get_elements('descendant::draw:frame')) == 2
    # mistune splits text at '<', so we get two spans here
    assert (odf.get()[0].get_elements('descendant::text:span')[2].text ==
            'There "is" ')
    assert (odf.get()[0].get_elements('descendant::text:span')[3].text ==
            '<some>')
    assert (odf.get()[0].get_elements('descendant::text:span')[4].text ==
            ' & \'the\' other to escape')


@with_setup(setup)
def test_nested_emphasis():
    markdown = '''
## Heading

***triple emphasis***
'''.strip()
    odf = mkdown.render(markdown)
    assert len(odf.get()) == 1
    assert len(odf.get()[0].get_elements('descendant::draw:frame')) == 2
    assert (odf.get()[0].get_elements('descendant::text:span')[2].get_attribute(
        'style') == 'md2odp-TextDoubleEmphasisStyle')
    assert (odf.get()[0].get_elements('descendant::text:span')[3].get_attribute(
        'style') == 'md2odp-TextEmphasisStyle')
    assert (odf.get()[0].get_elements('descendant::text:span')[4].text ==
            'triple emphasis')


@with_setup(setup)
def test_code_block():
    markdown = '''
## Heading

~~~ c++
void main()
{
    return -1;
}
~~~
'''.strip()
    odf = mkdown.render(markdown)
    assert len(odf.get()) == 1
    assert len(odf.get()[0].get_elements('descendant::draw:frame')) == 2
    assert (odf.get()[0].get_elements('descendant::text:span')[0].text ==
            'Heading')
    spaces = odf.get()[0].get_elements('descendant::text:s')
    assert len(spaces) == 1
    assert spaces[0].get_attribute('text:c') == '4'


@with_setup(setup)
def test_complex():
    # read more complex doc from disk. simply don't crash...
    markdown = codecs.open('cramtest/test.md', 'r', encoding='utf-8').read()
    odf = mkdown.render(markdown)
    pass


@with_setup(setup)
def test_svg1():
    markdown = '''
## Heading

![This is alt text](cramtest/test.svg)

'''.strip()
    odf = mkdown.render(markdown)
    assert len(odf.get()) == 1
    assert len(odf.get()[0].get_elements('descendant::draw:frame')) == 2
    print(odf.get()[0].get_elements('descendant::draw:frame')[1].serialize())
    assert odf.get()[0].get_elements('descendant::draw:frame')[1].get_attribute(
        'svg:width') == '22cm'
    assert odf.get()[0].get_elements('descendant::draw:frame')[1].get_attribute(
        'svg:height') == '9cm'
    assert len(odf.get()[0].get_elements('descendant::draw:image')) == 1


@with_setup(setup)
def test_weird_uris():
    markdown = '''
## Heading

![This is alt text](cramtest/test.svg;_-^!$%&=+#test)

'''.strip()
    mkdown.render(markdown)
    assert '.svg' in [x[-4:] for x in testdoc.get_part(
        ODF_MANIFEST).get_paths()]


@with_setup(setup)
def test_single_space_bug():
    markdown = '''
## Heading

~~~ bash
if [ $? -eq 0 ]; then
fi
~~~
'''.strip()
    odf = mkdown.render(markdown)
    assert odf.get()[0].get_elements('descendant::text:span')[8].text == '-eq'


@with_setup(setup)
def test_multiline_bold():
    markdown = '''
## Heading

**bold text
next line bold**
'''.strip()
    odf = mkdown.render(markdown)
    assert len(odf.get()) == 1
    assert len(odf.get()[0].get_elements('descendant::draw:frame')) == 2
    assert (odf.get()[0].get_elements('descendant::text:span')[2].get_attribute(
        'style') == 'md2odp-TextDoubleEmphasisStyle')
    assert (odf.get()[0].get_elements('descendant::text:span')[3].text ==
            'bold text\nnext line bold')
