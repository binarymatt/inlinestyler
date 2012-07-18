from bs4 import BeautifulSoup as Soup
from soupselect import select
import cssutils
import string


class InlineStyler(object):
    _style_attr_bookmark = '__||__'

    def __init__(self, html_string, parser="html.parser"):
        self._original_html = html_string
        self._soup = Soup(self._original_html, parser)

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

    def _pre_process_style_attrs(self):
        '''
            Adds a "bookmark" to keep track of which inline styles existed
            before InlineStyler got started. This way those styles will be
            respected and applied after anything originally included in a
            <style> tag.
        '''
        # find all elements with style tags
        for tag in self._soup.find_all(lambda tag: tag.has_key('style')):
            # "bookmark" where the already-inlined styles start
            tag['style'] = "%s%s" % (self._style_attr_bookmark, tag['style'])

    def _post_process_style_attrs(self):
        '''
            Removes the "bookmark" added by _pre_process_style_attrs() so that
            inline styles are applied in the correct order.
        '''
        for tag in self._soup.find_all(lambda tag: tag.has_key('style')):
            if tag['style'].startswith(self._style_attr_bookmark):
                tag['style'] = tag['style'].replace(self._style_attr_bookmark, "")
            else:
                tag['style'] = tag['style'].replace(self._style_attr_bookmark, ";")


    def _apply_rules(self):
        self._pre_process_style_attrs()

        for item in self._sheet.cssRules:
            if item.type == item.STYLE_RULE:
                selectors = item.selectorText
                for selector in selectors.split(','):
                    items = select(self._soup, selector)

                    for element in items:
                        styles = item.style.cssText.splitlines()
                        new_styles = [style.replace(';', u'').replace(
                                        '"', u"'") for style in styles]

                        all_styles = element.get('style', u'')
                        if self._style_attr_bookmark in all_styles:
                            current_styles, last_styles = all_styles.split(
                                    self._style_attr_bookmark)
                        else:
                            current_styles = all_styles
                            last_styles = None
                        current_styles = current_styles.split(';')

                        current_styles.extend(new_styles)
                        current_styles = filter(None, current_styles)
                        current_styles = u';'.join(current_styles)

                        if last_styles:
                            element['style'] = "%s%s%s" % (current_styles,
                                    self._style_attr_bookmark, last_styles)
                        else:
                            element['style'] = current_styles

        self._post_process_style_attrs()

        return self._soup

    def convert(self, remove_class=False, remove_id=False):
        css_list = self._strip_styles()
        self._load_sheet(css_list)
        html = self._apply_rules()

        if remove_class:
            for element in html.find_all(lambda tag: tag.has_key('class')):
                del element['class']

        if remove_id:
            for element in html.find_all(lambda tag: tag.has_key('id')):
                del element['id']

        return unicode(html)


def remove_whitepace(input_string):
    filtered_string = filter(lambda x: x not in string.whitespace,
            input_string)
    return filtered_string
