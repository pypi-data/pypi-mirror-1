try:
    from Products.LinguaPlone.atapi import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.atapi import *

from Products.ATContentTypes.configuration import zconf
from jyu.portalview import PortalViewMessageFactory as _

from Products.validation import validation
from validators import MenuBarValidator

validation.register(MenuBarValidator('isValidMenuBarSyntax'))

PortalViewSchema = OrderedBaseFolderSchema.copy() + Schema((

    TextField('css',
        required = False,
        searchable = True,
        accessor = 'getCSS',
        mutator = 'setCSS',
        storage = AnnotationStorage(),
        default_content_type = 'text/plain',
        default_output_type = 'text/plain',
        widget = TextAreaWidget(
            label = _(u'Custom styles'),
            rows = 25,
        ),
    ),

    BooleanField('menuBarEnabled',
        schemata = 'menubar',
        required = False,
        default = False,
        storage = AnnotationStorage(),
        widget = BooleanWidget(
            label = _(u'Show dropdown menu bar'),
            description = _(u'When set a dropdown menu bar built from the contents below will be rendered on top of the portal.'),
        )
    ),

    TextField('menuBarContents',
        schemata = 'menubar',
        required = False,
        storage = AnnotationStorage(),
        default_content_type = 'text/x-html-safe',
        default_output_type = 'text/x-html-safe',
        validators = ('isTidyHtmlWithCleanup', 'isValidMenuBarSyntax', ),
        widget = TextAreaWidget(
            label = _(u"Dropdown menu bar contents"),
            description = _(u"Use a two-dimensional HTML list with links to define the contents of the dropdown menu bar."),
            rows = 25,
        ),
    ),

    BooleanField('breadCrumbsHidden',
        schemata = 'menubar',
        required = False,
        storage = AnnotationStorage(),
        widget = BooleanWidget(
            label = _(u'Hide breadcrumbs when menu bar is enabled'),
        )
    ),
))

PortalViewSchema['title'].storage = AnnotationStorage()
PortalViewSchema['description'].storage = AnnotationStorage()


PortalViewColumnFolderSchema = OrderedBaseFolderSchema.copy() + Schema((

    StringField('width',
        required = True,
        searchable = False,
        storage = AnnotationStorage(),
        vocabulary = (('20', '20 %'),
                      ('25', '25 %'),
                      ('30', '30 %'),
                      ('40', '40 %'),
                      ('50', '50 %'),
                      ('60', '60 %'),
                      ('70', '70 %'),
                      ('80', '80 %'),
                      ('100', '100 %')),
        widget = SelectionWidget(
            label = _(u'Width'),
            format = 'select',
        ),
    ),
))

PortalViewColumnFolderSchema['title'].storage = AnnotationStorage()
PortalViewColumnFolderSchema['description'].storage = AnnotationStorage()
