#!/usr/bin/python
#coding: UTF-8
import py
import time
try:
    from templess import templess
except ImportError:
    import templess

here = py.magic.autopath().dirpath()

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

def main():
    t = (py.magic.autopath().dirpath() /
                'templates/testtemplate.html').open()
    template = templess.template(t)
    rendered = template.unicode(context)

if __name__ == '__main__':
    import sys
    num = 100
    if len(sys.argv) > 1:
        num = int(sys.argv[1])
    start = time.clock()
    for i in range(num):
        main()
    print time.clock() - start
