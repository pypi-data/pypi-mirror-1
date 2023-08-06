# Licensed under GNU General Public License (GPL)
# http://www.opensource.org/licenses/gpl-license.php

from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = "collective.idashboard"

DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))

product_globals = globals()

