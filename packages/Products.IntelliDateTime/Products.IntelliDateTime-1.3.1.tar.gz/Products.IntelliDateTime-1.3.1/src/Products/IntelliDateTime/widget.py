# Copyright 2008-2009, BlueDynamics Alliance, Austria - http://bluedynamics.com
# GNU General Public Licence Version 2 or later

__author__ = """Robert Niederreiter <rnix@squarewave.at>
                Jens Klein <jens@bluedynamics.com>"""
__docformat__ = 'plaintext'

from zope.component import adapts, adapter
from zope.interface import Interface
from zope.interface import implementer
from zope.component import queryAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.i18n.locales import locales
from van.timeformat import ltimefmt

from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import CalendarWidget
from Products.CMFCore.utils import getToolByName
from bda.calendar.base.interfaces import ITimezoneFactory
from bda.intellidatetime import IIntelliDateTime
from bda.intellidatetime import DateTimeConversionError

from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.IntelliDateTime.interfaces import ILocaleFactory

class IntelliDateTimeWidget(CalendarWidget):
    """Widget for IntelliDateTime input.
    """
    _properties = CalendarWidget._properties.copy()
    _properties.update({
        'macro' : 'intellidatetime',
        'starting_year': 1900,
        'ending_year': 2100,
        'datetimeimplementation': 'zope', # zope, python or provide own adapter
        'format': 'dd/mm/y', # TODO: strformat compatibility for the js
        'defaulttime': '', # prefill time, but no date if value is None
    })
    del _properties['helper_js']

    security = ClassSecurityInfo()
    
    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        
        fieldname = field.getName()        
        
        # check if field is there!
        testvalue = form.get('%s_date' % fieldname, empty_marker)
        if testvalue is empty_marker:
            return empty_marker
        
        # if its there we can read
        value = self._readDateTimeFromForm(instance, form, fieldname)
        if value is None and empty_marker:
            value = empty_marker
        return value, {}
    
    def dateInputValue(self, instance, value, fieldname=None):
        value = self._readValue(instance, value, fieldname)
        if not value:
            return ''
        
        date = ''
        lastchar = None
        if isinstance(value, DateTime):
            # zope DateTime
            day = value.day()
            month = value.month()
            year = value.year()
        else:
            # python datetime
            day = value.day
            month = value.month
            year = value.year
        for char in self.format:
            if char == lastchar:
                continue
            if char == 'd':
                lastchar = char
                date += str(day) + '.'
                continue
            if char == 'm':
                lastchar = char
                date += str(month) + '.'
                continue
            if char == 'y':
                lastchar = char
                date += str(year) + '.'
                continue
        return date.strip('.')
    
    def timeInputValue(self, instance, value, fieldname=None):
        value = self._readValue(instance, value, fieldname)
        if value is None:
            return self.defaulttime
        
        if isinstance(value, DateTime):
            hour = value.hour()
            min = value.minute()
        else:
            hour = value.hour
            min = value.minute                    
        formatted = '%02d:%02d' % (hour, min)
        return formatted
    
    def _readValue(self, instance, value, fieldname):
        submitted = self.REQUEST.form.get('submitted')
        if fieldname is None:
            return value
        formvalue = self._readDateTimeFromForm(instance, self.REQUEST.form, 
                                               fieldname)
        if formvalue or (not formvalue and value and submitted):
            return formvalue
        return value
    
    def formatDateTime(self, instance, dt):
        site = self._site(instance)
        locale = ILocaleFactory(site)
        locale = locales.getLocale(locale, locale)
        if not self.show_hm:
            return ltimefmt(dt, locale, category="date", length="short")
        return ltimefmt(dt, locale, category="dateTime", length="short")
    
    def _readDateTimeFromForm(self, instance, form, fieldname):
        date = form.get('%s_date' % fieldname)
        time = form.get('%s_time' % fieldname)
        site = self._site(instance)
        
        # these default adapters read properties of your plone site.
        # tzinfo is one of pytz.all_timezones
        # locale is one of those in bda.intellidatetime.converter
        
        # register a adapter that meets your need for your site if you need 
        # other behaviour. the default is using the server's timezone (which 
        # will prevent you from clashes with non-timezone aware dates 
        # (archetypes default datetimefields)
        tzinfo = ITimezoneFactory(site)
        
        # locales define the format for dates (%Y-%m-%d in 'en'... see 
        # bda.indellidatetime.converter)
        # the default implementation fetches the portal's default_language
        # possible specialisations could return a locale for the logged in user
        locale = ILocaleFactory(site)
        
        try:
            value = IIntelliDateTime(self).convert(date, time=time, 
                                                   locale=locale, tzinfo=tzinfo)
        except DateTimeConversionError, e:
            return None
        # correct DST, dont add one hour!
        value = value.replace(tzinfo=tzinfo.normalize(value).tzinfo)
        value = queryAdapter(value, IDateTimeImplementation,
                             name=self.datetimeimplementation)   
        return value
    
    def _site(self, instance):
        site = queryUtility(IPloneSiteRoot)
        if site is None:
            site = getToolByName(instance, 'portal_url').getPortalObject()
        return site
    
class IDateTimeImplementation(Interface):
    """converts python datetime to some other implementation."""

@implementer(IDateTimeImplementation)
def ZopeDateTime(value):
    try:
        return DateTime(value.isoformat())
    except DateTime.DateTimeError:
        return None

@implementer(IDateTimeImplementation)
def PythonDateTime(value):
    return value

@implementer(ILocaleFactory)
@adapter(IPloneSiteRoot)
def getPortalDefaultDateTimeLocale(site):
    """returns the default_language of the portal
    this will trigger the way dates are parsed by bda.intellidatetime and
    define how dates are formatted for printing
    """
    return site.portal_properties.site_properties.default_language