################################################################
# collective.calendarwidget
# (C) 2009, ZOPYX Ltd. & Co. KG 
################################################################

from Globals import InitializeClass
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import demjson

class CalendarWidgetView(BrowserView):
    """ CalendarWidget supplementary methods """ 

    def language(self):
        language = self.context.REQUEST.LANGUAGE
        if '-' in language:
            # strip combined language code
            language = language.split('-')[0]
        return language
        
    def getJS(self):
        """ return request specific JS as JSON """

        language = self.language()
        formats = self.formats(language)
        params = dict(python_fmt=formats['python_fmt'],
                      jquery_fmt=formats['jquery_fmt'],
                      language=language,
                      )

        return demjson.encode(params)


    def formats(self, language=None):
        """ Return date formats based on the request language """

        if not language:
            language = self.language()

        european_fmt = dict(python_fmt='%d.%m.%Y',
        jquery_fmt='dd.mm.yy')

        us_fmt = dict(python_fmt='%Y/%m/%d',
                      jquery_fmt='yy/mm/dd')

        language_mapping = {
            'de' : european_fmt,
            'at' : european_fmt,
            'ch' : european_fmt,
            'cs' : european_fmt,
            'en' : us_fmt,
        }

        return language_mapping.get(language, us_fmt)

    def hours_minutes(self, date):
        """ return hour-date string from a given DateTime instance """

        if date:
            return date.hour(), date.minute()
        else:
            return '', ''

    def datestr(self, date, with_time=0, ignore_unset_time=0):
        """ return formated date string """

        format = self.formats()['python_fmt']

        try:
            if with_time and not (ignore_unset_time and date.TimeMinutes() == '00:00'):
                format += ' %H:%Mh' 
            return date.strftime(format)
        except:
            return ''

InitializeClass(CalendarWidgetView)
