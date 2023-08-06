# Licensed under GNU General Public License (GPL)
# http://www.opensource.org/licenses/gpl-license.php

import logging

from Products.Archetypes import listTypes
from Products.Archetypes.atapi import *
from Products.CMFCore import utils as cmfutils

from config import *

log = logging.getLogger('collective.idashboard')
log.debug('Installing Product')

def initialize(context):
    """initialize product (called by zope)"""
    import browser

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

