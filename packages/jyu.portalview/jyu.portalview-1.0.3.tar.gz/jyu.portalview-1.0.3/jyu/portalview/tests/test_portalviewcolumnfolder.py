import unittest
from jyu.portalview.tests import base

from jyu.portalview.content.portalviewcolumnfolder import PortalViewColumnFolder

class TestContentType(base.ContentTypeTestCase):
    
    name = 'Portal View Column Folder'
    schema = PortalViewColumnFolder.schema

    def test_exists(self):
        self.failUnless('Portal View Column Folder' in self.types.objectIds())

    def test_factory(self):
        self.failUnless('Portal View Column Folder' in self.factory.getFactoryTypes().keys())

    def test_properties(self):
        self.assertProperty('title',                 'Portal View Column Folder')
        self.assertProperty('description',           'A folder, whose contents is displayed as a column in its parent portal view')
        self.assertProperty('i18n_domain',           'jyu.portalview')
        self.assertProperty('content_icon',          '++resource++jyu.portalview.images/column_icon.png')
        self.assertProperty('content_meta_type',     'PortalViewColumnFolder')
        self.assertProperty('product',               'jyu.portalview')
        self.assertProperty('factory',               'addPortalViewColumnFolder')
        self.assertProperty('immediate_view',        'base_edit')
        self.assertProperty('global_allow',          False)
        self.assertProperty('filter_content_types',  True)
        self.assertProperty('allowed_content_types', ('File', 'Image', 'Topic', 'Document', 'Portal View Column Folder'))
        self.assertProperty('allow_discussion',      False)
        self.assertProperty('default_view',          'view')
        self.assertProperty('view_methods',          ('view',))
        self.assertProperty('default_view_fallback', False)

    def test_method_aliases(self):
        self.assertMethodAlias('(Default)', 'folder_listing')
        self.assertMethodAlias('edit', 'atct_edit')
        self.assertMethodAlias('sharing', '@@sharing')
        self.assertMethodAlias('view', 'folder_listing')
    
    def test_actions(self):
        self.assertAction('view', {
            'title':    'View',
            'category': 'object',
            'condition_expr': '',
            'url_expr': 'string:${object_url}/view',
            'visible':  True,
            'permission': ()
        })
        self.assertAction('edit', {
            'title':          'Edit',
            'category':       'object',
            'condition_expr': 'not:object/@@plone_lock_info/is_locked_for_current_user|python:True',
            'url_expr':       'string:${object_url}/edit',
            'visible':        True,
            'permission':     ('Modify portal content',)
        })

    def test_fields(self):
        self.failUnless('width' in self.fieldnames)

    def test_width_field(self):
        field = self.schema.get('width')
        self.assertEquals('Products.Archetypes.Field.StringField', field.getType())
        self.assertEquals(True, field.required)
        self.assertEquals('SelectionWidget', field.getWidgetName())

    def test_width_widget(self):
        field = self.schema.get('width')
        self.assertEquals('select', field.widget.format)
        self.assertEquals((('20', '20 %'), 
                           ('25', '25 %'), 
                           ('30', '30 %'), 
                           ('40', '40 %'), 
                           ('50', '50 %'), 
                           ('60', '60 %'), 
                           ('70', '70 %'), 
                           ('80', '80 %'), 
                           ('100', '100 %')), field.vocabulary)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestContentType))
    return suite
