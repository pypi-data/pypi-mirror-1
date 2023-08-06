from zope.interface import implements
from zope.component import getMultiAdapter

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import PloneMessageFactory as _

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Acquisition import aq_inner, aq_base, aq_parent
from Products.CMFPlone.interfaces import INonStructuralFolder, IBrowserDefault

import random
from DateTime import DateTime
import math 


#from zope.schema.vocabulary import SimpleVocabulary
from Products.Archetypes.public import DisplayList

class IAdsPortlet(IPortletDataProvider):
    """A portlet which can render a Ads
    """
        
    name = schema.TextLine(
           title=_(u"label_title", default=u"Title"),
           description=_(u"help_title",
                         default=u"The title"),
           default=u"",
           required=False)    
    
    count = schema.Int(title=_(u'Number of items to display'),
           description=_(u'How many items to list.'),
           required=True,
           default=5)
    
    state = schema.Tuple(title=_(u"Workflow state"),
           description=_(u"Items in which workflow state to show."),
           default=('published', ),
           required=True,
           value_type=schema.Choice(
                                    vocabulary="plone.app.vocabularies.WorkflowStates")
           )

        
from Products.CMFPlone.utils import log
    
class Assignment(base.Assignment):
    implements(IAdsPortlet)
    def __init__(self,name=u"", count=5, state=('published', )):
        self.count = count
        self.state = state
        self.name= name

    title = _(u'Ads', default=u'Ads')


class Renderer(base.Renderer):

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
       
    def title(self):
        return self.data.name or ''      
        
    def update(self):
        pass

    #memoize @
    def getFilteredBanners(self):
   
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        
        state = self.data.state
        count = self.data.count
        
        banners = catalog( portal_type='Banner',
                                  effectiveRange=DateTime(),
                                  review_state=state
                                )
        bannerPool = []

        for banner in banners:
            percentage = banner.getPercent
          
            #XXX make better check here /100 is not good.
            # check if not 0
            if percentage!=0:
                percentage = int(math.ceil(percentage/100));
                # dont show banner if all clicks were used or the banner is outdated
                if banner.getClicksUsed < banner.getClicks:
                    for i in range(percentage):
                        bannerPool.append(banner)
        
        # get count and randomize
        if (len(bannerPool)>count):
            bannerPool = random.sample(bannerPool,count);
        
        return bannerPool;


    render = ViewPageTemplateFile('templates/adsportlet.pt')

#class AddForm(base.NullAddForm):
class AddForm(base.AddForm):
    form_fields = form.Fields(IAdsPortlet)
    label = _(u"Add Ads Portlet")
    description = _(u"Displays banners in this plone site ")
    
    def create(self, data):
        return Assignment(name=data.get('name',''),count=data.get('count', 5), state=data.get('state', ('published',)))
    
class EditForm(base.EditForm):
    
    form_fields = form.Fields(IAdsPortlet)
    label = _(u"Edit Ads Portlet")
    description = _(u"Displays banners in this Plone sit")
    
    