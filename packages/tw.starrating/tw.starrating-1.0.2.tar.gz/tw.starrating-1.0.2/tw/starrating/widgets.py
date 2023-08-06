# -*- coding: utf-8 -*-

from tw.api import Widget, JSLink, CSSLink

from formencode import NoDefault
from formencode import validators
from formencode.api import Invalid
from tw.api import JSLink, CSSLink, js_function, js_callback
from tw import jquery
from tw.forms import FormField

__all__ = ["StarRatingField"]


rating_css = CSSLink(
    modname=__name__,
    filename='static/jquery.rating.css',)

rating_js = JSLink(
    modname=__name__,
    filename='static/jquery.rating.js',
    css=[rating_css],
    javascript=[jquery.jquery_js_compressed],)


class StarRatingField(FormField):
    """
    ToscaWidgets form field for jQuery Star Rating Plugin
    http://www.fyneworks.com/jquery/star-rating/

    Inspired by, and even taken some code from tw.rating
    (See http://code.google.com/p/twtools/).
    """

    params = ["min", "max", "read_only", "if_missing"]
    min = 1
    max = 5
    if_missing = NoDefault
    read_only = False
    template = """\
<%namespace name="tw" module="tw.core.mako_util"/>
<div ${ tw.attrs([('class', css_class)]) }>
% for val in range(min, max+1):
<input ${ tw.attrs(
    [('type', "radio"),
     ('name', name),
     ('value', str(val)),
     ('class', 'star'),
     ('checked', [None, "checked"][str(val)==str(checked_value)])],
    attrs=attrs
)} />
% endfor
</div>
"""
    javascript = [rating_js]
    include_dynamic_js_calls = True
    validator = None

    def __init__(self, *args, **kw):
        super(StarRatingField, self).__init__(*args, **kw)
        self.validator = self.validator or validators.Int(
            min=self.min, max=self.max, if_missing=self.if_missing)
    
    def update_params(self, d):
        super(StarRatingField, self).update_params(d)
        if d['read_only']:
            self.add_call(js_function("$")(js_callback(
                js_function("$")('input[name=%s]' % d.name).rating('readOnly', True)
                )))
        else:
            self.add_call(js_function("$")(js_callback(
                js_function("$")('input[name=%s]' % d.name).rating()
                )))

        try:
            checked_value = self.validator.to_python(d.value)
        except Invalid:
            checked_value = None
        d["checked_value"] = checked_value
