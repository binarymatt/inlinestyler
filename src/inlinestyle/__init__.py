from bs4 import BeautifulSoup as Soup
from soupselect import select
import cssutils
import re

class InlineStyler(object):
    def __init__(self, html_string):
        self._original_html = html_string
        self._soup = Soup(self._original_html)

    def _strip_styles(self):
        style_blocks = self._soup.find_all('style')
        css_list = []
        for style_block in style_blocks:
            if style_block.contents:
                css_list.append(style_block.contents[0])
            style_block.extract()
        return css_list

    def _load_sheet(self, css_list):
        parser = cssutils.CSSParser()
        self._sheet = parser.parseString(u''.join(css_list))
        return self._sheet

    def _apply_rules(self):
        for item in self._sheet.cssRules:
            if item.type == item.STYLE_RULE:
                selectors = item.selectorText
                for selector in selectors.split(','):
                    items = select(self._soup, selector)

                    for element in items:
                        styles = item.style.cssText.splitlines()
                        new_styles = [style.replace(';',u'').replace('"', u"'")
                                      for style in styles]

                        current_styles = element.get('style',u'').split(';')
                        current_styles.extend(new_styles)
                        current_styles = filter(None, current_styles)
                        element['style'] = u';'.join(current_styles)

        return self._soup

    def convert(self, remove_class=False, remove_id=False):
        css_list = self._strip_styles()
        self._load_sheet(css_list)
        html = self._apply_rules()

        def has_class_attr(tag):
            return tag.has_key('class')

        def has_id_attr(tag):
            return tag.has_key('id')

        if remove_class:
            for element in html.find_all(has_class_attr):
                del element['class']

        if remove_id:
            for element in html.find_all(has_id_attr):
                del element['id']

        return unicode(html)

def remove_whitepace(input_string):
    import string
    filtered_string = filter(lambda x: x not in string.whitespace, input_string)
    return filtered_string
