from inlinestyle import InlineStyler, remove_whitepace
import os.path
from nose.tools import eq_, ok_

class TestCase(object):
    def setup(self):
        test_path = os.path.dirname(__file__)
        test_html_file = os.path.join(test_path, 'test.html')
        f = open(test_html_file,'r')
        self.html = f.read()
        f.close()

    def test_strip_styles(self):
        styler = InlineStyler(self.html)
        css_list = styler._strip_styles()
        eq_(len(css_list), 4)

    '''
    def test_style_application(self):
        assert False, 'not yet implemented'

    def test_conversion(self):
        assert False, 'not yet implemented'
    '''

    def test_remove_whitepace(self):
        inpt = 'body{\r\ntest}\t '
        string2 = remove_whitepace(inpt)
        eq_(string2, 'body{test}')

    '''
    def test_css_load(self):
        styler = InlineStyler(self.html)
        css_list = styler._strip_styles()
        string = ''.join(css_list)
        assert False, 'not yet implemented'
    '''


class TestConversion(TestCase):
    def test_integration(self):
        styler = InlineStyler(self.html)
        new_html = styler.convert()
        eq_(new_html, """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
<title>untitled</title>


</head>

<body class="body" style="font-size: 10px;background: #000;color: #FFF">
    Body text
    <div class="div" style="font-weight: bold;font-family: 'Courier New';background: #fff;color: #000">
        div text
    </div>
<div style="font-weight: bold;font-family: 'Courier New'">
        empty div
    </div>

<p class="p" style="background: #fff;color: #000">
        p text
    </p>
</body>
</html>
""")

    def test_handles_documents_with_an_empty_style_tag(self):
        styler = InlineStyler('<style></style>')
        new_html = styler.convert()
        eq_(new_html, '')

    def test_id_as_second_selector_where_first_selector_doesnt_exist(self):
        html = """
            <style>
                .some-class #some-id {
                    font-weight: bold;
                }
            </style>
            <div><div id="some-id">foo</div></div>
        """
        styler = InlineStyler(html)
        result = styler.convert()
        ok_('<div id="some-id">foo</div>' in result)

    def test_handles_multiple_classes(self):
        html = """
            <style>
                div.class1.class2 {
                    color: red;
                }
            </style>
            <div class="class1 class2">stuff</div>
        """
        styler = InlineStyler(html)
        new_html = styler.convert()
        eq_(new_html.strip(), '<div class="class1 class2" style="color: red">stuff</div>')

    def test_handles_comma_separated_classes(self):
        html = u"""
            <style>
                .noise-class, .target {
                    background-color: #FF00FF
                }
            </style>
            <div class="target">
            </div>
        """
        expected_html = u"""

<div class="target" style="background-color: #F0F">
</div>
"""
        styler = InlineStyler(html)
        new_html = styler.convert()
        eq_(expected_html, new_html)

    def test_remove_class_attribute(self):
        styler = InlineStyler('<style></style><div class="test">test</div>')
        new_html = styler.convert(remove_class=True)
        eq_(new_html, '<div>test</div>')

    def test_remove_id_attribute(self):
        styler = InlineStyler('<style></style><div id="test">test</div>')
        new_html = styler.convert(remove_id=True)
        eq_(new_html, '<div>test</div>')


    def test_respects_preexisting_style_attrs(self):
        html = u"""<style>
                    div { color: red; }
                    .class1 { color: green; }
                </style>
                <div class="class1" style="color: blue">test</div>"""
        styler = InlineStyler(html)
        new_html = styler.convert()
        eq_(new_html.strip(), u'<div class="class1" style="color: red;color: green;color: blue">test</div>')

        html = u"""<style>
                    div { color: red; border: 1px solid #000; }
                    .class1 { color: green; border: 2px dashed #CCC; }
                </style>
                <div class="class1" style="color: blue; border: 3px dotted #AAA;">test</div>"""
        styler = InlineStyler(html)
        new_html = styler.convert()
        eq_(new_html.strip(), u'<div class="class1" style="color: red;border: 1px solid #000;color: green;border: 2px dashed #CCC;color: blue; border: 3px dotted #AAA">test</div>')

    def test_respects_id_over_class(self):
        html = u"""<style>
                #div1 { color: red; }
                .class1 { color: blue; }
            </style>
            <div id="div1" class="class1">some text</div>
        """
        styler = InlineStyler(html)
        result = styler.convert()
        eq_(result.strip(), u'<div class="class1" id="div1" style="color: blue;color: red">some text</div>')

    def test_respects_class_over_element(self):
        html = u"""<style>
                .class1 { color: red; }
                div { color: orange; }
            </style>
            <div class="class1">some text</div>
        """
        styler = InlineStyler(html)
        result = styler.convert()
        eq_(result.strip(), u'<div class="class1" style="color: orange;color: red">some text</div>')

    def test_respects_pseudo_class_over_element(self):
        html = u"""<style>
                [rel="hi"] { color: green; }
                div { color: yellow; }
            </style>
            <div rel="hi">some text</div>
        """
        styler = InlineStyler(html)
        result = styler.convert()
        eq_(result.strip(), u'<div rel="hi" style="color: yellow;color: green">some text</div>')

    def test_respects_id_over_element(self):
        html = u"""<style>
                #div1 { color: blue; }
                div { color: red; }
            </style>
            <div id="div1">some text</div>
        """
        styler = InlineStyler(html)
        result = styler.convert()
        eq_(result.strip(), u'<div id="div1" style="color: red;color: blue">some text</div>')

    def test_applies_duplicate_rules_in_correct_order(self):
        html = """
            <style>
                h1 {
                    font-size: 30px;
                    font-weight: normal;
                }

                h1 {
                    font-size: 100%;
                    font-weight: bold;
                }
            </style>
            <h1>Hey guys.</h1>
        """
        styler = InlineStyler(html)
        result = styler.convert()
        ok_(result.find('font-size: 30px') < result.find('font-size: 100%'))
        ok_(result.find('font-weight: normal') < result.find('font-weight: bold'))

    def test_leaves_media_queries_in_style_tags(self):
        html = """
            <style>
                @media only screen and (max-width: 480px) {
                    h1 {
                        font-size: 18px;
                    }
                }

                h1 {
                    font-size: 20px;
                }
            </style>

            <h1>hey</h1>
        """
        styler = InlineStyler(html)
        result = styler.convert()
        ok_('<style>' in result)
        ok_('@media only screen and (max-width: 480px)' in result)
        ok_('font-size: 18px' in result)
        ok_('<h1 style="font-size: 20px">' in result)
