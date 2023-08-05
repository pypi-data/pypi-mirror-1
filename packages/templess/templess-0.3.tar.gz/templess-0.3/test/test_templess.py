import py
here = py.magic.autopath().dirpath()
py.std.sys.path.append(str(here.dirpath()))

try:
    from templess.templess import *
except ImportError:
    from templess import *

def test_entitize():
    assert entitize('foo') == 'foo'
    assert entitize('>foo"bar&qux\'quux<') == \
            '&gt;foo&quot;bar&amp;qux&apos;quux&lt;'

def test_serialize_attrs():
    node = elnode('foo', {}, None)
    assert node._serialize_attrs({'foo': 'bar', 'baz': 'qux'}) == \
            ' baz="qux" foo="bar"'
    assert node._serialize_attrs({'foo:bar': 'baz"qux'}) == \
            ' foo:bar="baz&quot;qux"'

def test_str():
    doc = elnode('foo', {'bar': 'baz'}, None)
    c1 = elnode('bar', {}, doc)
    c2 = elnode('bar', {}, doc)
    c3 = textnode('some text', doc)
    c1c1 = textnode('some text here too', c1)

    xml = doc.unicode()
    print xml
    assert xml == \
        '<foo bar="baz"><bar>some text here too</bar><bar />some text</foo>'

def test_builder_handler():
    import nanosax
    handler = treebuilderhandler('UTF-8')
    parser = nanosax.nsparser(handler)
    
    xml = here.join('data/test1.xml').read()
    parser.parse(xml)
    assert xml.strip() == handler.root.unicode()

def test_start_node():
    node = elnode('foo', {'foo': 'bar'}, None)
    assert list(node._start_node(node.attrs, True)) == [
            '<foo foo="bar"', ' />']
    assert list(node._start_node(node.attrs, False)) == [
            '<foo foo="bar"', '>']

def test_handle_cond():
    node = templessnode('foo', {}, None, 't')
    assert node._handle_cond({}, {})

    node = templessnode('foo', {'t:cond': 'foo'}, None, 't')
    assert not node._handle_cond({'t:cond': 'foo'}, {'foo': False})
    
    node = templessnode('foo', {'t:cond': 'foo'}, None, 't')
    assert node._handle_cond({'t:cond': 'foo'}, {'foo': True})

    node = templessnode('foo', {'t:cond': 'foo'}, None, 't')
    py.test.raises(KeyError, 'node._handle_cond({"t:cond": "foo"}, {})')

    node = templessnode('foo', {'t:not': 'foo'}, None, 't')
    assert not node._handle_cond({'t:not': 'foo'}, {'foo': True})

    node = templessnode('foo', {'t:not': 'foo'}, None, 't')
    assert node._handle_cond({'t:not': 'foo'}, {'foo': False})
    
    node = templessnode('foo', {'t:cond': 'foo'}, None, 't')
    assert not node._handle_cond({'t:cond': 'foo'}, {'foo': []})

def test_get_content():
    node = templessnode('foo', {}, None, 't')
    assert not node._get_content({})
    
    node = templessnode('foo', {'t:content': 'foo'}, None, 't')
    assert node._get_content({'t:content': 'foo'}) == 'foo'

def test_get_replace():
    node = templessnode('foo', {}, None, 't')
    assert not node._get_replace({})
    
    node = templessnode('foo', {'t:replace': 'foo'}, None, 't')
    assert node._get_replace({'t:replace': 'foo'}) == 'foo'

def test_basic_rendering():
    node = templessnode('foo', {'t:content': 'bar'}, None, 't')
    node = node.convert({'bar': 'baz'})
    ret = node.unicode()
    assert ret == '<foo>baz</foo>'

def test_list_rendering():
    node = templessnode('foo', {'t:content': 'bar'}, None, 't')
    nodes = node.convert({'bar': ['1', '2']})
    ret1 = nodes[0].unicode()
    ret2 = nodes[1].unicode()
    assert ret1 == '<foo>1</foo>'
    assert ret2 == '<foo>2</foo>'

def test_entitizing():
    node = templessnode('foo', {'t:content': 'bar'}, None, 't')
    node = node.convert({'bar': 'x < 1'})
    ret = node.unicode()
    assert ret == '<foo>x &lt; 1</foo>'

def test_xmlstring():
    node = templessnode('foo', {'t:content': 'bar'}, None, 't')
    node = node.convert({'bar': xmlstring('<bar />')})
    ret = node.unicode()
    assert ret == '<foo><bar /></foo>'

def test_generator():
    def somegenerator():
        for x in [1, 2, 3]:
            yield x
    node = templessnode('foo', {'t:content': 'bar'}, None, 't')
    nodes = node.convert({'bar': somegenerator()})
    for i, n in enumerate(nodes):
        assert n.unicode() == '<foo>%s</foo>' % (i + 1,)

def test_list_of_dicts():
    node = templessnode('foo', {'t:content': 'fooc'}, None, 't')
    # add some ignorable whitespace and some children
    textnode('   ', node)
    templessnode('bar', {'t:content': 'barc'}, node, 't')
    templessnode('baz', {'t:content': 'bazc'}, node, 't')
    nodes = node.convert(
        {'fooc': [
            {'barc': 'r1', 'bazc': 'z1'},
            {'barc': 'r2', 'bazc': 'z2'},
        ]}
    )
    assert nodes[0].unicode() == u'<foo>   <bar>r1</bar><baz>z1</baz></foo>'
    assert nodes[1].unicode() == u'<foo>   <bar>r2</bar><baz>z2</baz></foo>'

def test_basic_attrs():
    node = templessnode('foo', {'t:attr': 'value bar'}, None, 't')
    node = node.convert({'bar': 'baz'})
    assert node.unicode() == '<foo value="baz" />'

def test_attr_basic():
    node = templessnode('foo', {'t:attr': 'bar baz'}, None, 't')
    node = node.convert({'baz': 'qux'})
    assert node.unicode() == u'<foo bar="qux" />'

def test_attr_false():
    node = templessnode('foo', {'t:attr': 'bar baz'}, None, 't')
    node = node.convert({'baz': False})
    assert node.unicode() == u'<foo />'

def test_attr_remove_xmlns():
    node = templessnode('foo', {'xmlns:t': 'foo'}, None, 't')
    node = node.convert({})
    assert node.unicode() == u'<foo />'

def test_attr_remove_xmlns_leave_other():
    node = templessnode('foo', {'xmlns:q': 'foo'}, None, 't')
    node = node.convert({})
    assert node.unicode() == u'<foo xmlns:q="foo" />'

def test_attr_false_empty_string():
    node = templessnode('foo', {'t:attr': 'bar baz'}, None, 't')
    node = node.convert({'baz': ''})
    assert node.unicode() == u'<foo bar="" />'

def test_attr_false_replacing():
    node = templessnode('foo', {'bar': 'baz', 't:attr': 'bar baz'}, None, 't')
    node = node.convert({'baz': False})
    assert node.unicode() == u'<foo />'

def test_list_with_attrs():
    # XXX not entirely sure about this behaviour yet...
    node = templessnode('foo', {'t:content': 'bar', 't:attr': 'value baz'},
                        None, 't')
    nodes = node.convert({'baz': 'top', 'bar': [{'baz': 1}, {'baz': 2}]})
    assert len(nodes) == 2
    assert nodes[0].unicode() == u'<foo value="top" />'
    assert nodes[1].unicode() == u'<foo value="top" />'

def test_cdata():
    node = cdatanode(' foo ', None)
    assert node.unicode() == u'<![CDATA[ foo ]]>'

def test_find():
    foo = elnode('foo', {}, None)
    bar1 = elnode('bar', {}, foo)
    baz = elnode('baz', {}, bar1)
    bar2 = elnode('bar', {}, baz)
    bar3 = elnode('bar', {}, foo)
    bar4 = elnode('bar', {}, bar2)

    assert list(foo.find('bar')) == [bar1, bar2, bar3, bar4]

class container(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def test_objectcontext_regular():
    c = container(foo=1)
    assert str(c.foo) == '1'
    py.test.raises(TypeError, "c['foo']")

    oc = objectcontext(c)
    assert str(oc['foo']) == '1'
    py.test.raises(KeyError, "oc['bar']")

def test_objectcontext_dict():
    oc = objectcontext({'foo': 1})
    assert str(oc['foo']) == '1'

def test_objectcontext_nested():
    ci = container(bar=1)
    c = container(foo=ci)
    oc = objectcontext(c)
    assert str(oc['foo']['bar']) == '1'

def test_objectcontext_callable():
    c = container(foo=lambda: 1)
    oc = objectcontext(c)
    assert str(oc['foo']) == '1'

def test_objectcontext_nested_list():
    c = container(foo=[container(bar=1), container(bar=2)])
    oc = objectcontext(c)
    for i, item in enumerate(oc['foo']):
        assert isinstance(item, objectcontext)
        assert str(item['bar']) == str(i+1)

def test_objectcontext_nested_iterable():
    c = container(foo=(container(bar=x) for x in [1, 2]))
    oc = objectcontext(c)
    for i, item in enumerate(oc['foo']):
        assert isinstance(item, objectcontext)
        assert str(item['bar']) == str(i+1)

def test_generate():
    t = template('<foo xmlns:t="http://johnnydebris.net/xmlns/templess" '
                 't:content="foo" />')
    ret = ''
    i = 0
    for chunk in t.generate({'foo': 'bar'}):
        i += 1
        ret += chunk
    assert i > 1
    assert ret == ('<foo>bar</foo>')

def test_elnode_repr():
    xml = elnode('bar', {}, None).unicode()
    assert xml == '<bar />'

def test_templessnode_repr():
    xml = templessnode('bar', {}, None, 't').convert({}).unicode()
    assert xml == '<bar />'

def test_unicode_noxmlns():
    t = template('<foo />')
    xml = t.unicode({})
    assert xml == '<foo />'

