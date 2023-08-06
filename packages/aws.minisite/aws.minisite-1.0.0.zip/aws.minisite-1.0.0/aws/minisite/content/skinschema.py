from Products.Archetypes.public import *
from aws.minisite.config import I18N_DOMAIN
from Products.SmartColorWidget.Widget import SmartColorWidget

from collective.phantasy.atphantasy.content.skin import PhantasySkinSchema
from aws.minisite import minisiteMessageFactory as _

invisibleShematas = ['borders', 'plone-overloads']

invisibleFields = ['contentBackgroundImageName']      

visibleFields = []        


MiniSiteSkinFieldsSchema = Schema((        
                                                                      
    #new background image
    StringField(
        'headerBackgroundImageName',
        schemata ='images',
        widget=StringWidget(
            description = _(u'description_header_background_image_name', u"""Enter the header background image name, upload the image in this skin"""),
            label = _(u'label_header_background_image_name', u'Header Background Image Name'),
            ),
        ),
        
    BooleanField(
        'displayRoundedCorners',
        schemata ='images',
        default = False,
        widget=BooleanWidget(
            description = _(u'description_display_rounded_corners', 
                                u"""Do you want to display rounded corners around content ? (use it only for a portal width fixed to 996px, otherwise you may need to overload corner images and styles)"""),
            label = _(u'label_display_rounded_corners', u'Display Rounded Corners ?'),
            ), 
        ),          
        
    # new dimension
    StringField(
        'portalPadding',
        schemata ='dimensions', 
        widget=StringWidget(
            label=_(u'label_portal_padding', u'Portal Padding'),
            description = _(u'description_portal_padding', 
                            u"""Enter the portal padding, ex 10px or 1em ..."""),
            ),
        ),                           

    ), marshall=RFC822Marshaller())    


def finalizeMiniSiteSkinSchema():
    """Finalizes schema to alter some fields
    """
    schema = PhantasySkinSchema.copy()
    for fieldName in schema.keys() :
        if (fieldName not in visibleFields) and (schema[fieldName].schemata in invisibleShematas) :
            schema[fieldName].widget.visible = {'view':'invisible', 'edit':'invisible'}
        elif fieldName in invisibleFields :
            schema[fieldName].widget.visible = {'view':'invisible', 'edit':'invisible'}            
        elif fieldName == 'footerViewlet' :
            schema[fieldName].widget.fck_area_css_class = 'documentContent'
        elif fieldName == 'logoViewlet' : 
            schema[fieldName].widget.fck_area_css_id = 'portal-header'
    # Make a copy to reinitialize all layers
    new_schema = schema.copy() + MiniSiteSkinFieldsSchema
    return new_schema
    
    
MiniSiteSkinSchema = finalizeMiniSiteSkinSchema()

