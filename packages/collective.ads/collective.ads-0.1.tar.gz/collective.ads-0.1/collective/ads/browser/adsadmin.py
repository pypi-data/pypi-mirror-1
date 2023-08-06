##code-section module-header #fill in your manual code here
##/code-section module-header

from zope import interface
from zope import component
from Products.CMFPlone import utils
from Products.Five.browser import BrowserView
from zope.interface import implements
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Acquisition import aq_inner, aq_base, aq_parent
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from Products.CMFPlone import PloneMessageFactory as _


class AdsAdminView(BrowserView):
    """
        view class
    """
    
    def __call__(self):
        
        if self.request.form.get('form.submitted'):
            REQUEST = self.context.REQUEST
            self.save_all_banners(REQUEST)
            self.context.plone_utils.addPortalMessage(_(u'Saved'), 'info')
        return self.index()
        
    def getBanners(self):
        context = self.context
        
        context = aq_inner(context)
        
        query = {'portal_type' : ["Banner"]}
        currentPath = '/'.join(context.getPhysicalPath())
        query['path'] = {'query' : currentPath, 'depth' : 1}

        catalog = getToolByName(self, "portal_catalog")

        y = []
        brains = catalog(query)
        for brain in brains:
            y.append(brain)
            
        return y
    
    security = ClassSecurityInfo()
    security.declarePrivate('save_all_banners')
    def save_all_banners(self, REQUEST=None):
        """
        """
        if not REQUEST:
          REQUEST = self.REQUEST
        
        ids = REQUEST.get('banner-ids')
        context =aq_inner(self.context)
        
        for id in ids:
          editVals = {'clicks': REQUEST.get('clicks_%s' % id),
                      'percent':REQUEST.get('percent_%s' % id),
                     }
          
          banner = getattr(context,id)
          banner.edit(**editVals)
        return 'saved'
        #self.REQUEST.RESPONSE.redirect(link)
