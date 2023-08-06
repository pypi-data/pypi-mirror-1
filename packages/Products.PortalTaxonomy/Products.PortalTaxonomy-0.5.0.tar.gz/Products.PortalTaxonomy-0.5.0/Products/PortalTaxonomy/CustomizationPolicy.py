'''
------------------------------------------------------------------------------
Name:         CustomizationPolicy.py
Purpose:      Sets up Plone with PortalTaxonomy.  You will need to uncomment
              the lines in __init__.py that install this policy if you want to
              use it.
Author:       Jeremy Stark <jeremy@deximer.com>
Copyright:    (c) 2005 by Deximer
Licence:      GNU General Public Licence (GPL) Version 2 or later
------------------------------------------------------------------------------
'''

from Products.CMFPlone.Portal import addPolicy
from Products.CMFPlone.interfaces.CustomizationPolicy import ICustomizationPolicy
from Products.CMFPlone.CustomizationPolicy import DefaultCustomizationPolicy
from Products.CMFCore.utils import getToolByName

class PTCustomizationPolicy(DefaultCustomizationPolicy):
    __implements__ = ICustomizationPolicy

    availableAtConstruction = True
    
    def customize(self, portal):
        DefaultCustomizationPolicy().customize(portal)
        portal.portal_quickinstaller.installProduct("PortalTaxonomy")

def register(context):
    addPolicy('PotalTaxonomy based site', PTCustomizationPolicy())

