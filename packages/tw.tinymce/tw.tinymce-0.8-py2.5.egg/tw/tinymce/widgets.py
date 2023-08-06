"""
TinyMCE rich text editor ToscaWidget.

Bundles tinyMCE from http://tinymce.moxiecode.com/

Copyright 2007 Alberto Valverde Gonzalez

Licensed under the LGPL license due to bundled JS library's license.
"""
import os
import re
from warnings import warn

from pkg_resources import resource_filename

from tw.api import JSLink, js_function, adapt_value
from tw.forms import TextArea
from tw.forms.validators import UnicodeString

from genshi.core import Markup, stripentities

__all__ = ["TinyMCE", "MarkupConverter"]

class MarkupConverter(UnicodeString):
    """A validator for TinyMCE widget.

    Will make sure the text that reaches python will be unicode un-xml-escaped 
    HTML content.

    Will also remove any trailing <br />s tinymce sometimes leaves at the end
    of pasted text.
    """ 
    cleaner = re.compile(r'(\s*<br />\s*)+$').sub 
    if_missing=''
    def _to_python(self, value, state=None):
        value = super(MarkupConverter, self)._to_python(value, state)
        if value:
            value = Markup(stripentities(value)).unescape()
            return self.cleaner('', value)


def _get_available_languages():
    filename_re = re.compile(r'(\w+)\.js')
    locale_dir = resource_filename(__name__, "static/javascript/langs")
    langs = []
    for filename in os.listdir(locale_dir):
        match = filename_re.match(filename)
        if match:
            langs.append(match.groups(0)[0])
    return langs

tinyMCE = JSLink(
    modname = __name__, 
    filename = 'static/javascript/tiny_mce_src.js',
    init = js_function('tinyMCE.init'),
    )


class TinyMCE(TextArea):
    """TinyMCE WYSIWYG rich text editor. 
    
    You can pass options directly to tinyMCE JS object at consruction or 
    display via the ``mce_options`` dict parameter.
    
    Allows localization. To see available languages peek into the ``langs``
    attribute of the TinyMCE class. Language codes can be passed as the 
    ``locale`` parameter to display or provide a default at construction
    time. To dynamically switch languages based on HTTP headers a callable
    can be passed to return a language code by parsing/fetching headers 
    whereever the app/framework makes them available. Same technique can be
    used to use cookies, session data or whatever.

    If a custom validator is supplied, it is recommended that it inherits from
    ``toscawidgets.widgets.tinymce.MarkupConverter`` to deal with markup
    conversion and unicode issues.
    """
    javascript = [tinyMCE]
    langs = _get_available_languages()
    locale = 'en'
    params = ["mce_options", "locale"]
    cols = 79
    rows = 25
    mce_options = {}
    default_options = dict(
        mode = "exact",
        theme = "advanced",
        plugins = "advimage",
        theme_advanced_toolbar_location = "top",
        theme_advanced_toolbar_align = "center",
        theme_advanced_statusbar_location = "bottom",
        extended_valid_elements = "a[href|target|name]",
        theme_advanced_resizing = True,
        paste_use_dialog = False,
        paste_auto_cleanup_on_paste = True,
        paste_convert_headers_to_strong = False,
        paste_strip_class_attributes = "all",
    )
    validator = MarkupConverter
    include_dynamic_js_calls = True

    def update_params(self, d):
        super(TinyMCE, self).update_params(d)
        options = self.default_options.copy()
        options.update(d.mce_options)
        if d.locale in self.langs:
            options.setdefault('language', d.locale)
        else:
            warn("Language file for '%s' not available" % d.locale)
            d.locale = 'en'
        if options.setdefault('mode', 'exact') == 'exact':
            options['elements'] = d.id
        # Next line creates a javascript call which will be placed at bodybottom
        # to initialize tinyMCE with desired options.
        self.add_call(tinyMCE.init(options))
