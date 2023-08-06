from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
#import interfaces
import utility

from collective.ads.config import *

from Products.CMFCore.utils import UniqueObject
   
    
##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

AdsAdmin_schema = BaseFolderSchema.copy()
##code-section after-schema #fill in your manual code here
##/code-section after-schema

class AdsAdmin(UniqueObject,BaseFolder):
    security = ClassSecurityInfo()

    implements(utility.IAdsPortal)
    
    # This name appears in the 'add' box
    archetype_name = 'AdsAdmin'

    meta_type = 'AdsAdmin'
    schema = AdsAdmin_schema

    # Methods
    security.declarePublic('banner_click')
    def banner_click(self, UID=None):
        """
        gets the UID of the banner, saves the click and redirects to the URL
        """
        if not UID:
          return
          
        atool = self.archetype_tool
        cat = self.portal_catalog
        banner = atool.lookupObject(UID)
        intLink = banner.getLinkIntern()
        extLink = banner.getLinkExtern()
        link = (intLink and intLink.absolute_url()) or extLink
        
        # save click
        banner.setClicksUsed((banner.getClicksUsed() or 0) + 1)
        
        # update catalog entries (metadata getClicks and getClicksUsed)
        cat.reindexObject(banner)
        
        # redirect to the URL
        self.REQUEST.RESPONSE.redirect(link)

    
def modify_fti(fti):
    # Hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ['edit', 'sharing', 'metadata', 'folderlisting']:
            a['visible'] = 0
    return fti

registerType(AdsAdmin,PROJECTNAME)
# end of class AdsAdmin

##code-section module-footer #fill in your manual code here
##/code-section module-footer



