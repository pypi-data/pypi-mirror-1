import os
from Globals import DTMLFile
from Acquisition import aq_inner
from Products.ResourceRegistries.tools.packer import CSSPacker
from collective.phantasy.browser.phantasy_properties import PhantasyThemeProperties

this_dir = os.path.dirname(os.path.abspath(__file__))

templates_dir = os.path.join(this_dir, 'stylesheets')


stylesheet_dtml = DTMLFile('threecolorstheme.css', templates_dir)


class ThreeColorsThemeProperties(PhantasyThemeProperties):    
    
    def __call__(self, *args, **kw):
        """Return a dtml file when calling the view (more easy thx to Gillux)"""

        # Wrap acquisition context to template
        context = aq_inner(self.context)
        template = stylesheet_dtml.__of__(context)
        # Push cache headers
        self.getHeader()
        phantasy_props = self.getPhantasyCssProperties()
        logo = getattr(context, phantasy_props['logoName'])
        csscontent = template(context,
                              phantasy_properties = phantasy_props,
                              css_url = self.getPhantasyThemeUrl(),
                              portal_url = self.getPortalUrl(),
                              logoWidth = logo.width,
                              logoHeight = logo.height  )
        
        return  CSSPacker('safe').pack(csscontent)                              