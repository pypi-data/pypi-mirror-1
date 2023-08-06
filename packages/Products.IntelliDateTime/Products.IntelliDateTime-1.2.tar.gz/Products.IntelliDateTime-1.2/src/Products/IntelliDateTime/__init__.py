#
# Copyright 2008-2009, Blue Dynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

import logging
logger = logging.getLogger('IntelliDateTime')
logger.info('Installing Product')

from widget import IntelliDateTimeWidget
from field import IntelliDateTimeField

from Products.CMFCore.DirectoryView import registerDirectory
from config import GLOBALS
registerDirectory('skins', GLOBALS)