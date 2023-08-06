import unittest
from jyu.portalview.tests import base

from jyu.portalview.content.portalview import PortalView

class TestContentType(base.ContentTypeTestCase):
    
    name = 'Portal View'
    schema = PortalView.schema

    def test_exists(self):
        self.failUnless(self.name in self.types.objectIds())

    def test_factory(self):
        self.failUnless(self.name in self.factory.getFactoryTypes().keys())

    def test_properties(self):
        self.assertProperty('title',                 'Portal View')
        self.assertProperty('description',           'A content type, which displays content in a portal like aggregating view')
        self.assertProperty('i18n_domain',           'jyu.portalview')
        self.assertProperty('content_icon',          '++resource++jyu.portalview.images/portalview_icon.png')
        self.assertProperty('content_meta_type',     'PortalView')
        self.assertProperty('product',               'jyu.portalview')
        self.assertProperty('factory',               'addPortalView')
        self.assertProperty('immediate_view',        'base_edit')
        self.assertProperty('global_allow',          True)
        self.assertProperty('filter_content_types',  True)
        self.assertProperty('allowed_content_types', ('Portal View Column Folder',))
        self.assertProperty('allow_discussion',      False)
        self.assertProperty('default_view',          'view')
        self.assertProperty('view_methods',          ('view',))
        self.assertProperty('default_view_fallback', False)

    def test_method_aliases(self):
        self.assertMethodAlias('(Default)', '(dynamic view)')
        self.assertMethodAlias('edit', 'atct_edit')
        self.assertMethodAlias('sharing', '@@sharing')
        self.assertMethodAlias('view', '(selected layout)')

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
        self.failUnless('css' in self.fieldnames)

    def test_css_field(self):
        field = self.schema.get('css')
        self.assertEquals('Products.Archetypes.Field.TextField', field.getType())
        self.assertEquals(False, field.required)
        self.assertEquals('TextAreaWidget', field.getWidgetName())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestContentType))
    return suite
