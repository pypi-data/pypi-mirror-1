from Products.Archetypes.public import *
from collective.threecolorstheme.config import I18N_DOMAIN
from Products.SmartColorWidget.Widget import SmartColorWidget

from collective.phantasy.atphantasy.content.skin import PhantasySkinSchema

invisibleShematas = ['borders', 'plone-overloads', 'colors', 'dimensions']

invisibleFields = ['contentBackgroundImageName']      

visibleFields = ['columnOneWidth','columnTwoWidth']        


ThreeColorsThemeFieldsSchema = Schema((                                                                      
    # new dimension added
    StringField(
        'portalPadding',
        schemata ='dimensions', 
        widget=StringWidget(
            label='Portal Padding',
            description = "Choose the padding for the portal",
            label_msgid = "label_header_ portal_padding",
            description_msgid = "description_header_ portal_padding",
            i18n_domain = I18N_DOMAIN,
            ),
        ),        

    # new background image added
    StringField(
        'headerIllustrationName',
        schemata ='images', 
        widget=StringWidget(
            label='Header Illustration Name',
            description = "Choose the header illustration file name, upload the image in the skin to overload it",
            label_msgid = "label_header_ illustration_name",
            description_msgid = "description_header_ illustration_name",
            i18n_domain = I18N_DOMAIN,
            ),
        ),         
    # colors used to change standard plone colors
    # see mutators in skin.py         
    StringField(
        'leadingColor',
        required=1,
        schemata ='colors',
        widget=SmartColorWidget(
            label='leading Color',
            description = "Choose the portal background color",
            label_msgid = "label_portal_background_color",
            description_msgid = "description_portal_background_color",
            i18n_domain = I18N_DOMAIN,
            ),
        ), 
    StringField(
        'lightColor1',
        required=1,
        schemata ='colors',
        widget=SmartColorWidget(
            label='light Color',
            description = "Choose the light color (used in tabs menus)",
            label_msgid = "label_light_color1",
            description_msgid = "description_light_color1",
            i18n_domain = I18N_DOMAIN,
            ),
        ),  
    StringField(
        'lightColor2',
        required=1,
        schemata ='colors',
        widget=SmartColorWidget(
            label='very Light Color',
            description = "Choose the very light color (used in buttons, even rows ...)",
            label_msgid = "label_light_color2",
            description_msgid = "description_light_color2",
            i18n_domain = I18N_DOMAIN,
            ),
        ),              

    ), marshall=RFC822Marshaller())    


def finalizeThreeColorsThemeSchema():
    """Finalizes schema to alter some fields
    """
    schema = PhantasySkinSchema.copy()
    for fieldName in schema.keys() :
        if (fieldName not in visibleFields) and (schema[fieldName].schemata in invisibleShematas) :
            schema[fieldName].widget.visible = {'view':'invisible', 'edit':'invisible'}
        elif fieldName in invisibleFields :
            schema[fieldName].widget.visible = {'view':'invisible', 'edit':'invisible'}            
    # Make a copy to reinitialize all layers
    new_schema = schema.copy() + ThreeColorsThemeFieldsSchema
    return new_schema
    
    
ThreeColorsThemeSkinSchema = finalizeThreeColorsThemeSchema()

