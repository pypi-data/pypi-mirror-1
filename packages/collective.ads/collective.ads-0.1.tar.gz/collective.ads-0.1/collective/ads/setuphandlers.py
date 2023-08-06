# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2008 by []
# Generator: ArchGenXML Version 2.0-beta10 (svn)
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """info@fourdigits.nl"""
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger('Ads: setuphandlers')
from collective.ads.config import PROJECTNAME
from collective.ads.config import DEPENDENCIES
from Products.CMFCore.utils import getToolByName

from collective.ads.config import TOOL_TITLE
##code-section HEAD
##/code-section HEAD

def installGSDependencies(context):
    """Install dependend profiles."""

    # XXX Hacky, but works for now. has to be refactored as soon as generic
    # setup allows a more flexible way to handle dependencies.

    dependencies = []
    if not dependencies:
        return

    site = context.getSite()
    setup_tool = getToolByName(site, 'portal_setup')
    for dependency in dependencies:
        if dependency.find(':') == -1:
            dependency += ':default'
        old_context = setup_tool.getImportContextID()
        setup_tool.setImportContext('profile-%s' % dependency)
        importsteps = setup_tool.getImportStepRegistry().sortSteps()
        excludes = [
            u'Ads-QI-dependencies',
            u'Ads-GS-dependencies'
        ]
        importsteps = [s for s in importsteps if s not in excludes]
        for step in importsteps:
            setup_tool.runImportStep(step) # purging flag here?
        setup_tool.setImportContext(old_context)

    # re-run some steps to be sure the current profile applies as expected
    importsteps = setup_tool.getImportStepRegistry().sortSteps()
    filter = [
        u'typeinfo',
        u'workflow',
        u'membranetool',
        u'factorytool',
        u'content_type_registry',
        u'membrane-sitemanager'
    ]
    importsteps = [s for s in importsteps if s in filter]
    for step in importsteps:
        setup_tool.runImportStep(step) # purging flag here?

def installQIDependencies(context):
    """This is for old-style products using QuickInstaller"""
    site = context.getSite()
    qi = getToolByName(site, 'portal_quickinstaller')

    for dependency in DEPENDENCIES:
        if qi.isProductInstalled(dependency):
            logger.info("Re-Installing dependency %s:" % dependency)
            qi.reinstallProducts([dependency])
        else:
            logger.info("Installing dependency %s:" % dependency)
            qi.installProducts([dependency])



def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""

    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()

def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    site = context.getSite()

    #if self.readDataFile('atadsmanager.txt') is None:
    #    return


def importVarious(self):
    if self.readDataFile('atadsmanager.txt') is None:
        logger.info("Return")
        return
    site = self.getSite()
    
    vtool = getToolByName(site, 'portal_adsadmin')
    vtool.title = TOOL_TITLE
    logger.info("portal_adsadmin = %s:" % TOOL_TITLE)
    # remove from portal_catalog
    vtool.unindexObject()
    

##code-section FOOT
##/code-section FOOT
