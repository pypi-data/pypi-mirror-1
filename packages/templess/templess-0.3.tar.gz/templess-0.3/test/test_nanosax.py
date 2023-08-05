import py
here = py.magic.autopath().dirpath()
py.std.sys.path.append(here.dirpath().strpath)

import nanosax

class TestNanoSax(object):
    def test_parse(self):
        class tp(nanosax.nsparser):
            def __init__(self, handler, chunks):
                self.chunks = chunks
                super(tp, self).__init__(handler)
            def _parse_into_chunks(self, xml):
                return self.chunks
            def _handle_pis(self, xml):
                return xml

        handler = nanosax.echohandler()
        parser = tp(handler, [
            (tp.TYPE_START, 1, 'foo bar="baz"'),
            (tp.TYPE_COMMENT, 1, 'here is the content of tag foo'),
            (tp.TYPE_TEXT, 1, 'content of tag foo'),
            (tp.TYPE_END, 1, 'foo'),
        ])
        parser.parse('')
        assert handler.xml == ('<foo bar="baz">'
                                '<!--here is the content of tag foo-->'
                                'content of tag foo'
                                '</foo>')

        handler = nanosax.echohandler()
        parser = tp(handler, [
            (tp.TYPE_START, 1, 'document'),
            (tp.TYPE_TEXT, 1, '\n  '),
            (tp.TYPE_START, 2, 'node attr="value"'),
            (tp.TYPE_TEXT, 2, '\n    '),
            (tp.TYPE_CDATA, 3, '\n      some CDATA\n    '),
            (tp.TYPE_TEXT, 5, '\n  '),
            (tp.TYPE_END, 6, 'node'),
            (tp.TYPE_TEXT, 7, '\n'),
            (tp.TYPE_END, 8, 'document'),
        ])
        parser.parse('')
        assert handler.xml == ('<document>\n'
                                '  <node attr="value">\n'
                                '    <![CDATA[\n'
                                '      some CDATA\n'
                                '    ]]>\n'
                                '  </node>\n'
                                '</document>')

    def test_parse_into_chunks(self):
        handler = nanosax.nshandler()
        parser = nanosax.nsparser(handler)
        assert list(parser._parse_into_chunks(
            '<foo bar="baz">'
            '<!--here is the content of tag foo-->'
            'content of tag foo'
            '</foo>'
        )) == [
            (parser.TYPE_START, 1, 'foo bar="baz"'),
            (parser.TYPE_COMMENT, 1, 'here is the content of tag foo'),
            (parser.TYPE_TEXT, 1, 'content of tag foo'),
            (parser.TYPE_END, 1, 'foo'),
        ]

        handler = nanosax.nshandler()
        parser = nanosax.nsparser(handler)
        chunks = list(parser._parse_into_chunks(
            '<document>\n'
            '  <node attr="value">\n'
            '    <![CDATA[\n'
            '      some CDATA\n'
            '    ]]>\n'
            '  </node>\n'
            '</document>'
        ))
        expected = [
            (parser.TYPE_START, 1, 'document'),
            (parser.TYPE_TEXT, 1, '\n  '),
            (parser.TYPE_START, 2, 'node attr="value"'),
            (parser.TYPE_TEXT, 2, '\n    '),
            (parser.TYPE_CDATA, 3, '\n      some CDATA\n    '),
            (parser.TYPE_TEXT, 5, '\n  '),
            (parser.TYPE_END, 6, 'node'),
            (parser.TYPE_TEXT, 6, '\n'),
            (parser.TYPE_END, 7, 'document'),
        ]
        assert chunks == expected

        handler = nanosax.echohandler()
        parser = nanosax.nsparser(handler)
        py.test.raises(nanosax.XMLError,
            'list(parser._parse_into_chunks("<foo>"))')
        py.test.raises(nanosax.XMLError,
            r'list(parser._parse_into_chunks("<foo></bar>"))')
        py.test.raises(nanosax.XMLError,
            r'list(parser._parse_into_chunks("<foo />bar"))')
        py.test.raises(nanosax.XMLError,
            r'list(parser._parse_into_chunks("<foo<bar/>"))')

    def test_handle_pis(self):
        handler = nanosax.nshandler()
        parser = nanosax.nsparser(handler)
        xml = ('<?xml version="1.0" encoding="UTF-8" ?><?PI bar="baz" ?>'
                '<!DOCTYPE document [<!ELEMENT document (#PCDATA)>]>'
                '<document><!-- some comment --><![CDATA[ some cdata ]]>'
                '</document><?PI some more pi?>')
        result = parser._handle_pis(xml)
        assert result == (
            '<document><!-- some comment --><![CDATA[ some cdata ]]>'
            '</document>'
        )

    def test_parse_start(self):
        handler = nanosax.nshandler()
        parser = nanosax.nsparser(handler)

        assert parser._parse_start(1, 'foo bar="baz"') == \
                ('foo', {'bar': 'baz'})
        assert parser._parse_start(1, 'foo bar="baz" xmlns="foo:"') == \
                ('foo', {'bar': 'baz', 'xmlns': 'foo:'})
        assert parser._parse_start(1, 'foo:bar bar:baz="qux"') == \
                ('foo:bar', {'bar:baz': 'qux'})
        assert parser._parse_start(1, 'foo\n\t\tbar="baz\t\n"\t\t')
        py.test.raises(nanosax.XMLError,
            "parser._parse_start(1, 'foo$bar')")
        py.test.raises(nanosax.XMLError,
            "parser._parse_start(1, 'foo bar#baz=\"qux\"')")
        py.test.raises(nanosax.XMLError,
            "parser._parse_start(1, 'foo baz=\"qux\"\"')")
        py.test.raises(nanosax.XMLError,
            "parser._parse_start(1, 'foo bar')")

    def test_regs(self):
        p = nanosax.nsparser
        assert p._reg_name.match('foo')
        assert p._reg_name.match('foo:bar')
        assert p._reg_name.match('foo-bar:baz-qux')
        assert p._reg_name.match('foo123bar:baz123qux')
        assert p._reg_name.match('foo_bar')
        assert not p._reg_name.match('foo bar')
        assert not p._reg_name.match('foo$bar')

        assert p._reg_start.match('foo bar="baz"')
        assert p._reg_start.match('foo:bar xmlns="bar:" xmlns:foo="foo:"')
        assert p._reg_start.match('foo\n\t\tbar="baz\n\t\t\t\tqux"')
        assert not p._reg_start.match('foo bar')
        assert not p._reg_start.match('foo bar=""baz"')
        assert not p._reg_start.match('foo <bar="baz"')
        
        assert p._reg_attr.match('foo="bar"')
        assert p._reg_attr.match('foo="bar" xmlns:foo="foo:"')
        assert p._reg_attr.match('foo=""')
        assert p._reg_attr.match("foo='bar'")
        assert p._reg_attr.match("foo='bar' bar=\"baz\"")
        match = p._reg_attr.match(
            ('select="//customer[count(purchase[@type = \'ProductA\''
                'and @quantity &gt; 10]) = 1]"'))
        assert match.group(4) == (
            '//customer[count(purchase[@type = \'ProductA\''
            'and @quantity &gt; 10]) = 1]'
        )
        assert not p._reg_attr.match("foo='bar\"")
        assert not p._reg_attr.match('foo')
        assert not p._reg_attr.match('foo="bar>"')

        assert p._reg_xml_decl.match(
            '<?xml version="1.0" encoding="UTF-8" language="en" ?>')
        assert p._reg_xml_decl.match('<?xml ?>')
        assert not p._reg_xml_decl.match('<?processing-instruction ?>')
        assert not p._reg_xml_decl.match('<foo>')

        assert p._reg_encoding.match('encoding="UTF-8"')
        assert p._reg_encoding.match('encoding="latin-1"').group(1) == \
                'latin-1'
        assert not p._reg_encoding.match('encoding=""')
        assert not p._reg_encoding.match('hyperencoding="UTF-8"')
        
        assert p._reg_pi.match('<?processing-instruction foo bar="baz" ?>')
        assert p._reg_pi.match('<?foo ?>')
        assert not p._reg_pi.match('<foo ?>')

        assert p._reg_dtd_1.match('<!DOCTYPE foo [some content]>')
        dtd = ('<!DOCTYPE foo ['
                '<!ELEMENT bar (#PCDATA)>'
                '<!ELEMENT baz (#PCDATA)>]>')
        assert p._reg_dtd_1.match(dtd).group(0) == dtd
        assert not p._reg_dtd_1.match('<!ELEMENT foo ()>')
        assert not p._reg_dtd_1.match('<![CDATA[ jsklajdsa ]>')
        
        assert p._reg_dtd_2.match('<!DOCTYPE foo SYSTEM "bar">')
        assert p._reg_dtd_2.match("<!DOCTYPE foo SYSTEM 'bar'>")
        assert p._reg_dtd_2.match("<!DOCTYPE note\n         SYSTEM 'note.dtd'>")

class TestNanoSaxFunctional(object):
    def test_working(self):
        for file in here.join('data/nsxml').listdir('working_*.xml'):
            xml = file.read()
            handler = nanosax.echohandler()
            parser = nanosax.nsparser(handler)
            parser.parse(xml)
            xmlin = self.normalize(xml)
            xmlout = self.normalize(handler.xml)
            assert xmlin == xmlout, file.strpath

    def test_failing(self):
        for file in here.join('data/nsxml').listdir('failing_*.xml'):
            xml = file.read()
            handler = nanosax.nshandler()
            parser = nanosax.nsparser(handler)
            py.test.raises(nanosax.XMLError, 'parser.parse(xml)')

    def normalize(self, xml):
        from xml.dom import minidom
        xml = self.remove_cruft(xml)
        return minidom.parseString(xml).toxml()

    def remove_cruft(self, xml):
        p = nanosax.nsparser
        for reg in [p._reg_xml_decl, p._reg_pi, p._reg_dtd_1, p._reg_dtd_2]:
            while 1:
                match = reg.search(xml)
                if not match:
                    break
                xml = xml.replace(match.group(0), '')
        return xml
