from Products.CMFPlone.utils import getToolByName

def importFinalSteps(context):


    if context.readDataFile('collective.threecolorstheme_various.txt') is None:
        return
    site = context.getSite()
    setupTypesInfos(site)
    
        

def setupTypesInfos(context):
    """
    Disallow skins contents
    after portal_types & structure install
    """
    ttool = getToolByName(context, 'portal_types')
    types = ['ThreeColorsThemeSkin', 'PhantasySkinsRepository']
    for type in types :
        fti = getattr(ttool, type, None)
        if fti :
            fti._setPropValue('global_allow', 0)
    
