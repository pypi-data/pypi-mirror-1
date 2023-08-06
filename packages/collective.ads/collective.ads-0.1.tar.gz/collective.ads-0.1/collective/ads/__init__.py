from Products.CMFCore import DirectoryView

import logging
logger = logging.getLogger('Ads')
logger.debug('Installing Product Ads')

try:
    import CustomizationPolicy
except ImportError:
    CustomizationPolicy = None

from Globals import package_home
from Products.CMFCore import utils as cmfutils
try: # New CMF  
  from Products.CMFCore import permissions as CMFCorePermissions 
except: # Old CMF  
  from Products.CMFCore import CMFCorePermissions
from Products.CMFCore import DirectoryView

from Products.CMFPlone.utils import ToolInit

from Products.Archetypes.public import *
from Products.Archetypes import listTypes
from Products.Archetypes.utils import capitalize

import os, os.path

from collective.ads.config import *

DirectoryView.registerDirectory('skins', product_globals)
logger.debug('Register Skin')

PROJECTNAME = "collective.ads"

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    ##code-section custom-init-top #fill in your manual code here
    ##/code-section custom-init-top

    # imports packages and types for registration
    import content
    import admin

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
        
    tools = [admin.AdsAdmin.AdsAdmin]
    ToolInit("%s Tool" % PROJECTNAME,
                    tools=tools,
                    icon="browser/images/adminicon.gif",
                   ).initialize(context)
    # Apply customization-policy, if theres any
    if CustomizationPolicy and hasattr(CustomizationPolicy, 'register'):
        CustomizationPolicy.register(context)
        print 'Customization policy for Ads installed'
    ##code-section custom-init-bottom #fill in your manual code here
    ##/code-section custom-init-bottom
