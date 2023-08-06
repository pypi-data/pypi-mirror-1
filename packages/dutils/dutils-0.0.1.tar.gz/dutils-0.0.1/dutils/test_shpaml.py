from unittest import TestCase
from textwrap import dedent

from convert import convert_text, convert_line


class TestPublish(TestCase):
    def assertConverts(self, source, expected_output):
        source = dedent(source)
        expected_output = dedent(expected_output).strip()
        actual_output = convert_text(source).strip()
        if expected_output != actual_output:
            print repr(expected_output)
            print repr(actual_output)
            raise Exception('values not equal')

    def test_raw_html(self):
        self.assertConverts(
            '''
            <p>
                <b>hello</b>
                <br />
            </p>
            ''',
            '''
            <p>
                <b>hello</b>
                <br />
            </p>
            ''')

    def test_dwim_paragraphs(self):
        self.assertConverts(
            '''
            p
                foo
            ''',
            '''
            <p>
                foo
            </p>
            ''')

    def test_indentation_indicates_tag_hierarchy(self):
        self.assertConverts(
            '''
            p
                | foo
            ''',
            '''
            <p>
                foo
            </p>
            ''')

    def test_blank_lines(self):
        self.assertConverts(
                '''
                p
                    bar
                        baz

                    yo

                x
                    foo
                ''',

                '''
                <p>
                    <bar>
                        baz
                    </bar>

                    yo
                </p>

                <x>
                    foo
                </x>
                '''
                )

    def test_jquery_syntax(self):
        self.assertConverts(
                '''
                p.foo 
                    | bar
                ''',
                '''
                <p class="foo">
                    bar
                </p>
                '''
                )
        self.assertConverts(
                '''
                .foo.bar#div1
                    | bar
                ''',
                '''
                <div class="foo bar" id="div1">
                    bar
                </div>
                '''
                )

    def test_surrounding_with_tags(self):
        self.assertConverts('b | foo', '<b>foo</b>')

    def test_surrounding_tags_with_tags(self):
        self.assertConverts('i | <b>foo</b>', '<i><b>foo</b></i>')

    def test_repeated_surrounding_with_tags(self):
        self.assertConverts('i > b | foo', '<i><b>foo</b></i>')


class TestConvertLine(TestCase):
    def verify_convert_line(self, source, expected_output):
        actual_output = convert_line(source).strip()
        if expected_output != actual_output:
            print
            print repr(expected_output)
            print repr(actual_output)
            raise Exception('values not equal')

    def test_stuff(self):
        self.verify_convert_line('', '')
        self.verify_convert_line('| {{ foo }}', '{{ foo }}')
        self.verify_convert_line('b | foo', '<b>foo</b>')
        self.verify_convert_line('p.foo | bar', '<p class="foo">bar</p>')
        self.verify_convert_line(
                'span class="foo" > b | foo', 
                '<span class="foo"><b>foo</b></span>')
        self.verify_convert_line('> input', '<input />')
        self.verify_convert_line('> br', '<br />')
        self.verify_convert_line('> br', '<br />')

    def test_jquery_syntax(self):
        self.verify_convert_line(
                '.foo | stuff',
                '<div class="foo">stuff</div>'
                )
        self.verify_convert_line(
                'p#foo | stuff',
                '<p id="foo">stuff</p>'
                )
        self.verify_convert_line(
                '#foo | stuff',
                '<div id="foo">stuff</div>'
                )
        self.verify_convert_line(
                'b > #foo | stuff',
                '<b><div id="foo">stuff</div></b>'
                )
        self.verify_convert_line(
                'b > #foo > i | stuff',
                '<b><div id="foo"><i>stuff</i></div></b>'
                )


if __name__ == '__main__':
    import unittest
    unittest.main()

