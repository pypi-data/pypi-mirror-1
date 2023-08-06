from zope.interface import implements
from zope.formlib import form
from zope.i18nmessageid import MessageFactory
from plone.fieldsets.fieldsets import FormFieldsets

from plone.app.controlpanel.form import ControlPanelForm

from Products.Five.formlib import formbase
from Acquisition import aq_inner
from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import html_quote, newline_to_br

from collective.ads.admin.utility import IAdsAdminControlPanelForm,IAdsPortal


_ = MessageFactory('portal_adsadmin')

class AdsAdminControlPanelForm(ControlPanelForm):
    """Control Panel Form"""
    implements(IAdsAdminControlPanelForm)

    ads = FormFieldsets(IAdsAdminControlPanelForm)
    ads.id = 'ads'
    ads.label = _(u'ads', default=u'Macros')

    #ads_banner = FormFieldsets(IAdsPortal)
    #ads_banner.id = 'ads'
    #ads_banner.label = _(u'ads', default=u'Banners')

    form_fields = FormFieldsets(ads)

    label = _(u"AdsAdmin")
    description = _(u"AdsAdmin")
    form_name = _("AdsAdmin")

