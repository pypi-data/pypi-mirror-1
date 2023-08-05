#!/usr/bin/python
# -*- coding: UTF-8 -*-
import py
here = py.magic.autopath().dirpath()
py.std.sys.path.append(here.dirpath().strpath)

try:
    from templess import templess
except ImportError:
    import templess
from StringIO import StringIO
import re

from xml.dom.minidom import parseString

includeel = templess.xmlstring(u'<div>foo</div>')
includeel2 = templess.template(
    here.join('templates/testtemplate_include.html').open()
).render(
    {'data': unicode('föö', 'UTF-8')}
)
context = {
    'p1data': unicode('föö', 'UTF-8'),
    'p2data': ['bar', 'baz'],
    'rowdata': [
        {'celldata': ['cell 1', 'cell 2']},
        {'celldata': ['cell 3', 'cell 4']},
    ],
    'styledata': 'color: red',
    'divclass': 'foo',
    'div2data': [
        {'data': 'foo'},
        {'data': 'bar'},
    ],
    'condition1': 'true',
    'condition2': '',
    'replacedata': 'foo',
    'replacedata2': [
        {'data': 'bar'},
    ],
    'includedata': includeel,
    'includedata2': includeel2,
}

def setup_module(mod):
    t = (py.magic.autopath().dirpath() /
                    'templates/testtemplate.html').open()
    template = templess.template(t)
    mod.rendered = rendered = template.unicode(context)

    print repr(rendered)
    mod.rdoc = parseString(rendered.encode('UTF-8'))

def gettext(node):
    ret = []
    for child in node.childNodes:
        if child.nodeType == 3:
            ret.append(child.nodeValue)
        elif child.nodeType == 1:
            ret += gettext(child)
    return ''.join(ret)

def test_string_content():
    p = rdoc.getElementsByTagName('p')[0]
    assert gettext(p) == unicode('föö', 'UTF-8')

def test_string_repeat():
    p1, p2 = rdoc.getElementsByTagName('p')[1:]
    assert gettext(p1) == 'bar'
    assert gettext(p2) == 'baz'

def test_dict_repeat():
    c1, c2, c3, c4 = rdoc.getElementsByTagName('td')
    assert gettext(c1) == 'cell 1'
    assert gettext(c3) == 'cell 3'

def test_attr():
    d = [d for d in rdoc.getElementsByTagName('div')
                if d.hasAttribute('style')][0]
    assert d.getAttribute('style') == 'color: red'
    assert d.getAttribute('class') == 'foo'

def test_cond():
    ds = [d for d in rdoc.getElementsByTagName('div')
                if d.getAttribute('class') == 'y']
    assert gettext(ds[0]) == 'foo'
    assert len(ds) == 1

def test_not():
    ds = [d for d in rdoc.getElementsByTagName('div')
                if d.getAttribute('class') == 'noty']
    print gettext(ds[0])
    assert gettext(ds[0]) == 'bar'
    assert len(ds) == 1

def test_replace():
    d = [d for d in rdoc.getElementsByTagName('div')
                if d.getAttribute('class') == 'z'][0]
    assert d.firstChild.nodeValue.strip() == 'foo'
    span = d.getElementsByTagName('*')[0]
    print span.nodeName
    assert span.nodeName == 'span'
    assert gettext(span) == 'bar'

def test_node_include():
    d = [d for d in rdoc.getElementsByTagName('div')
                if d.getAttribute('class') == 'node'][0]
    assert d.nodeName == 'div'
    assert gettext(d) == 'foo'

def test_templess_macro():
    d = [d for d in rdoc.getElementsByTagName('div')
                if d.getAttribute('class') == 'node'][1]
    assert d.nodeName == 'div'
    assert gettext(d) == unicode('föö', 'UTF-8')

def test_nested_element_repeat():
    # tests a specific problem where an element inside a repeat was not the
    # direct child of the repeat element
    ds = [d for d in rdoc.getElementsByTagName('div')
                if d.getAttribute('class') == 'x']
    assert gettext(ds[0]) == 'foo'
    assert gettext(ds[1]) == 'bar'

def test_nonascii():
    # we've already tested whether interpolation works (see first test)
    # and also interpolation with a macro, now let's test plain strings in
    # the template and also everything with latin-1 contents
    nonasciis = [d for d in rdoc.getElementsByTagName('div')
                    if d.getAttribute('class') == 'nonascii']
    assert gettext(nonasciis[0]).strip() == unicode('föö', 'UTF-8')

    # latin-1 tests
    context = {
        'p1data': unicode('föö', 'UTF-8').encode('latin-1'),
        'p2data': ['bar', 'baz'],
        'rowdata': [
            {'celldata': ['cell 1', 'cell 2']},
            {'celldata': ['cell 3', 'cell 4']},
        ],
        'styledata': 'color: red',
        'divclass': 'foo',
        'div2data': [
            {'data': 'foo'},
            {'data': 'bar'},
        ],
        'condition1': 'true',
        'condition2': '',
        'replacedata': 'foo',
        'replacedata2': [
            {'data': 'bar'},
        ],
        'includedata': 'foo',
        'includedata2': 'bar',
    }
    fp = (py.magic.autopath().dirpath() / 'templates/testtemplate.html').open()
    try:
        data = fp.read()
    finally:
        fp.close()
    data = unicode(data, 'UTF-8').encode('latin-1')
    template = templess.template(data, 'latin-1')
    html = template.unicode(context)
    # the interpolated föö is in a <p>
    assert html.find(unicode('<p>föö</p>', 'UTF-8')) > -1
    # the one inside the template is in a div with a class
    assert html.find(unicode('<div class="nonascii">föö</div>',
                                'UTF-8')) > -1

def test_snippet_repeat():
    xml = ('<foo xmlns:t="http://johnnydebris.net/xmlns/templess">'
            '<bar t:replace="bars">'
            '<baz t:content="baz" /><qux t:content="qux" />'
            '</bar></foo>')
    template = templess.template(xml)
    rendered = template.unicode(
        {'bars':[
            {'baz': 'baz1',
                'qux': 'qux1'},
            {'baz': 'baz2',
                'qux': 'qux2'},
            ]
        }
    )
    dom = parseString(rendered)
    doc = dom.documentElement
    assert len(doc.childNodes) == 4
    assert doc.childNodes[0].nodeName == 'baz'
    assert doc.childNodes[1].nodeName == 'qux'

def test_validate():
    try:
        from lxml import etree
    except:
        py.test.skip('requires lxml, not installed')
    edoc = etree.fromstring(rendered)
    xpe = etree.XPathEvaluator(edoc)
    xpe.registerNamespace('xhtml', 'http://www.w3.org/1999/xhtml')
        
    rngdoc = etree.parse(str(py.magic.autopath().dirpath() / 'templess.rng'))
    # if this fails, you might not have the xhtml (and modules) schema
    # available
    rng = etree.RelaxNG(rngdoc)
    t1 = open(str(py.magic.autopath().dirpath() /
                    'templates/testtemplate.html'))
    t1doc = etree.parse(t1)
    assert rng.validate(t1doc)
    rngdoc = etree.parse(str(py.magic.autopath().dirpath() / 'xhtml.rng'))
    rng = etree.RelaxNG(rngdoc)
    assert rng.validate(edoc)

