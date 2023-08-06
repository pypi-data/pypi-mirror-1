#
# Copyright 2008-2009, Blue Dynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later

__author__ = """Jens Klein <jens@bluedynamics.com>"""
__docformat__ = 'plaintext'

from zope import interface

class ILocaleFactory(interface.Interface):
    """callable that returns the locale that shall be used for date parsing.
    it must be one if the locales defined in bda.indellidatetime.converter.
    """
    