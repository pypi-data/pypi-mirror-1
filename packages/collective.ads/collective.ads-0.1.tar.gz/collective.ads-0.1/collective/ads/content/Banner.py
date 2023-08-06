from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from collective.ads.config import *
##code-section module-header #fill in your manual code here
##/code-section module-header

copied_fields = {}
copied_fields['effectiveDate'] = BaseSchema['effectiveDate'].copy()
copied_fields['effectiveDate'].schemata = "default"
copied_fields['effectiveDate'].widget.label_msgid = "Ads_label_effective"
copied_fields['expirationDate'] = BaseSchema['expirationDate'].copy()
copied_fields['expirationDate'].schemata = "default"
copied_fields['expirationDate'].widget.label_msgid = "Ads_label_expired"
schema = Schema((

    FileField(
        name='source',
        widget=FileWidget(
            description="Add Flash object",
            label='Source',
            label_msgid='Ads_label_source',
            description_msgid='Ads_help_source',
            i18n_domain='collective.ads',
        ),
        required=0,
        storage=AttributeStorage()
    ),
	
    ImageField(
        name='bannerimage',
        widget=ImageField._properties['widget'](
            description="Add images object like: jpg, gif or png",
            label='Image',
            label_msgid='Ads_label_image',
            description_msgid='Ads_help_image',
            i18n_domain='collective.ads',
        ),
        required=0,
        storage=AttributeStorage(),
        max_size=(150, 150),
        sizes={'small':(150,150)},
    ),

    IntegerField(
        name='clicks',
        widget=IntegerWidget(
            label='Maximum number of clicks',
            label_msgid='Ads_label_clicks',
            i18n_domain='collective.ads',
        ),
        required=1
    ),

    IntegerField(
        name='clicksUsed',
        default="0",
        widget=IntegerWidget(
            visible=-1,
            label='Clicksused',
            label_msgid='Ads_label_clicksUsed',
            i18n_domain='collective.ads',
        )
    ),

    IntegerField(
        name='percent',
        default="100",
		widget=IntegerWidget(
            label='Showing rate in %',
            label_msgid='Ads_label_percent',
            i18n_domain='collective.ads',
        ),
        required=1
    ),

    ReferenceField(
        name='linkIntern',
        widget=ReferenceBrowserWidget
        (
            allowed_types=('RichDocument', 'File', 'Image', 'Folder'),
            label='Internal link',
            label_msgid='Ads_label_linkIntern',
            i18n_domain='collective.ads',
        ),
        multiValued=0,
        relationship="banner_int_link"
    ),

    StringField(
        name='linkExtern',
        validators=('isURL',),
        widget=StringWidget(
            label='External Link',
            label_msgid='Ads_label_linkExtern',
            i18n_domain='collective.ads',
        ),
        
    ),
    copied_fields['effectiveDate'],
    copied_fields['expirationDate'],
),
)


##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Banner_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Banner(BaseContent, BrowserDefaultMixin):
    security = ClassSecurityInfo()
    implements(interfaces.IBanner)

    archetype_name = 'Banner'
    meta_type = 'Banner'

    _at_rename_after_creation = True
    schema = Banner_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

registerType(Banner,PROJECTNAME)
# end of class Banner

##code-section module-footer #fill in your manual code here
##/code-section module-footer



