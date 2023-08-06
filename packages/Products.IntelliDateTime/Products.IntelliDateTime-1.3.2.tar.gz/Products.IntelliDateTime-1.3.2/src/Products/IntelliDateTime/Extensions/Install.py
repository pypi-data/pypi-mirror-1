#
# Copyright 2008-2009, Blue Dynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from StringIO import StringIO
from Products.Archetypes.Extensions.utils import install_subskin
from Products.IntelliDateTime.config import PROJECTNAME, GLOBALS
from Products.CMFPlone.utils import getToolByName

def install(self):
    out = StringIO()
    install_subskin(self, out, GLOBALS)

    js = (
        {'id': 'intellidatetime.js'},
    )
    registerJavascripts(self, out, js)

    out.write("Successfully installed %s." % PROJECTNAME)
    return out.getvalue()

def registerJavascripts(self, out, javascripts):
    jstool = getToolByName(self, 'portal_javascripts')
    existing = jstool.getResourceIds()
    updates = []
    for js in javascripts:
        if not js.get('id') in existing:
            jstool.registerScript(**js)
        else:
            updates.append(js)
    if updates:
        updateResources(jstool, updates)
    print >> out, "installed the IntelliDateTime additional javascripts."

def updateResources(tool, updates):
    resources = list(tool.resources)
    for update in updates:
        resource = tool.getResource(update['id'])
        for key in [k for k in update.keys() if k != 'id']:
            # keep a trace of our customization for further reversion
            if not resource._data.has_key('original_'+key):
                resource._data['original_'+key] = resource._data[key]
            resource._data[key] = update[key]
        tool.cookResources()
