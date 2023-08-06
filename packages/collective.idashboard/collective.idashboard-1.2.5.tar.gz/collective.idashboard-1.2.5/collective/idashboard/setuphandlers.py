from StringIO import StringIO

from plone.browserlayer import utils

from collective.idashboard.interfaces import IIDashboardLayer

def removeBrowserLayer(portal, out):
    if IIDashboardLayer in utils.registered_layers():
        utils.unregister_layer(name='collective.idashboard')
        print >> out, "Remove the browser layer collective.idashboard"

def importVariousUninstall(context):
    if context.readDataFile('idashboard_uninstall_marker.txt') is None:
        return

    site = context.getSite()
    out = StringIO()

    removeBrowserLayer(site, out)
