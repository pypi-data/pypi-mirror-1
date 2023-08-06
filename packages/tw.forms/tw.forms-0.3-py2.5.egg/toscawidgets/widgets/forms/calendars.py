import os
from datetime import datetime
import logging

from pkg_resources import resource_filename

import toscawidgets
from toscawidgets.api import CSSLink, JSLink, js_function
from toscawidgets.widgets.forms import FormField, validators


__all__ = ["CalendarDatePicker", "CalendarDateTimePicker"]

setup_calendar = js_function("Calendar.setup")

log = logging.getLogger(__name__)

calendar_css = CSSLink(
    modname=__name__, filename='static/calendar/calendar-system.css')
calendar_js = JSLink(
    modname=__name__, filename='static/calendar/calendar.js')
calendar_setup = JSLink(
    modname=__name__, filename='static/calendar/calendar-setup.js')

#XXX: The calendar is  pretty broken now as most of the params to
#     CalendarDatePicker will have no effect when passed to display. This should
#     be fixed.

class CalendarDatePicker(FormField):
    css = [calendar_css]
    javascript = [calendar_js, calendar_setup]
    template = "toscawidgets.widgets.forms.templates.calendar"
    params = [
        "calendar_lang", "not_empty", "button_text", "date_format", 
        "picker_shows_time",
        ]
    calendar_lang = 'en'
    not_empty = True
    button_text = "Choose"
    date_format = "%m/%d/%Y"
    picker_shows_time = False
    validator = None
    include_dynamic_js_calls = True

    _default = None

    def __init__(self, *args, **kw):
        """
        Use a javascript calendar system to allow picking of calendar dates.
        The date_format is in mm/dd/yyyy unless otherwise specified
        """
        super(CalendarDatePicker, self).__init__(*args, **kw)
        if self.default is None and self.not_empty:
            self.default = lambda: datetime.now()
        self.validator = self.validator or validators.DateTimeConverter(
            format=self.date_format, not_empty=self.not_empty)

        lang_file_link = self.get_calendar_lang_file_link(self.calendar_lang)
        self.javascript.append(lang_file_link)

    def get_calendar_lang_file_link(self, calendar_lang):
        """
        Returns a CalendarLangFileLink containing a list of name
        patterns to try in turn to find the correct calendar locale
        file to use.
        """
        patterns = []
        
        # The preferred method is to use the explicitly specified
        # language.
        if calendar_lang is not None:
            patterns += ["lang/calendar-%s.js" % calendar_lang]

        # The next best method is to determine the language to use
        # from the HTTP header settings.
        patterns += ["lang/calendar-%(lang)s-%(charset)s.js",
                     "lang/calendar-%(lang)s.js"]

        # Fallback on English if neither of the above gave a result.
        patterns += ["lang/calendar-en.js"]
        
        return CalendarLangFileLink(name_patterns=patterns)

    def update_params(self, d):
        super(CalendarDatePicker, self).update_params(d)
        log.debug("Value received by Calendar: %r", d.value)
        try:
            d.strdate = d.value.strftime(d.date_format)
        except AttributeError:
            d.strdate = d.value
        options = dict(
            inputField = self.id,
            ifFormat = d.date_format,
            button = self.id + '_trigger',
            showsTime = d.picker_shows_time,
            )
        self.add_call(setup_calendar(options))


class CalendarDateTimePicker(CalendarDatePicker):
    date_format = "%Y/%m/%d %H:%M"
    picker_shows_time = True

def lang_in_gettext_date_format(lang):
    if len(lang) > 2:
        country = lang[3:].upper()
        lang = lang[:2] + "_" + country
    return lang

class CalendarLangFileLink(JSLink):
    """Links to proper calendar.js language file depending on HTTP info."""
    params = ["accept_language", "accept_charset", "name_patterns"]
    accept_language = ['en']
    accept_charset = ['utf-8']
    name_patterns = []

    def __init__(self, *args, **kw):
        super(CalendarLangFileLink, self).__init__(*args, **kw)
        self.webdir = calendar_js.webdir
        self.dirname = calendar_js.dirname
        self.modname = calendar_js.modname
        # filename is not really needed as it's dynamic. But we need to set
        # a dummy one for comparisons to work
        self.link = None

    def update_params(self, d):
        super(CalendarLangFileLink, self).update_params(d)
        base_dir = self.webdir
        def find_name():
            for name_pattern in d['name_patterns']:
                for lang in d['accept_language']:
                    for charset in d['accept_charset']:
                        params = dict()
                        params["lang"] = lang
                        params["charset"] = charset
                        params["gettext_lang"] = lang_in_gettext_date_format(lang)
                        params["gettext_charset"] = charset.upper()
                        params["custom_lang"] = self.custom_lang(lang)
                        params["custom_charset"] = self.custom_charset(charset)
                        name = name_pattern % params
                        if os.path.exists(os.path.join(self.dirname,name)):
                            return name
            return ''
        name = find_name()
        d["link"] = '/'.join(calendar_js.link.split('/')[:-1] + [name])

    def custom_lang(self, lang):
        return None

    def custom_charset(self, charset):
        return None
