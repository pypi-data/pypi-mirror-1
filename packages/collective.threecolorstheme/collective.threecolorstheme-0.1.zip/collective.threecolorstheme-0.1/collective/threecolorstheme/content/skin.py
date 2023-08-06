# -*- coding: utf-8 -*-

# Zope imports
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

# CMF imports
from Products.CMFCore import permissions as CCP
from Products.CMFPlone.utils import getToolByName

from Products.Archetypes.public import *

from collective.threecolorstheme.interfaces import IThreeColorsThemeSkin
from schema import ThreeColorsThemeSkinSchema
from collective.threecolorstheme.config import PROJECTNAME

from collective.phantasy.atphantasy.content.skin import PhantasySkin
 

class ThreeColorsThemeSkin(PhantasySkin):
    """ThreeColorsTheme Skin"""

    portal_type = meta_type = 'ThreeColorsThemeSkin'
    archetype_name = 'Dynamic Skin'
    global_allow = True
    schema = ThreeColorsThemeSkinSchema
    implements(IThreeColorsThemeSkin)


    security = ClassSecurityInfo()
    
    # mutators methods to set all plone colors with 3 colors
    
    security.declareProtected(CCP.ModifyPortalContent, 'setLeadingColor')
    def setLeadingColor(self, value, **kwargs):        
        fields = []
        fields.append(self.getField('contentViewBorderColor'))
        fields.append(self.getField('linkColor'))
        fields.append(self.getField('contentViewFontColor'))
        fields.append(self.getField('notifyBorderColor'))
        fields.append(self.getField('discreetColor'))
        fields.append(self.getField('leadingColor'))
        for field in fields :
            field.set(self, value, **kwargs)
            
    security.declareProtected(CCP.ModifyPortalContent, 'setLightColor2')
    def setLightColor2(self, value, **kwargs):        
        fields = []
        fields.append(self.getField('contentViewBackgroundColor'))
        fields.append(self.getField('evenRowBackgroundColor'))
        fields.append(self.getField('globalBackgroundColor'))
        fields.append(self.getField('globalBorderColor'))
        fields.append(self.getField('globalFontColor'))
        fields.append(self.getField('lightColor2'))
        for field in fields :
            field.set(self, value, **kwargs)    
            
    security.declareProtected(CCP.ModifyPortalContent, 'setLightColor1')
    def setLightColor1(self, value, **kwargs):        
        fields = []
        fields.append(self.getField('notifyBackgroundColor'))
        fields.append(self.getField('lightColor1'))
        for field in fields :
            field.set(self, value, **kwargs)                                
    

registerType(ThreeColorsThemeSkin, PROJECTNAME)
