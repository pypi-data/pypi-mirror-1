# -*- coding:utf-8 -*-
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.app import zapi
import urllib2

from DateTime import DateTime
import Missing
import re

CSS_COMMENTS_REGEXP = re.compile("(/\*[^\*]*\*/)") # Matches comments
CSS_SELECTORS_REGEXP = re.compile("([a-zA-Z0-9\.#-_:@]+[^{]*)*{[^}]*}") # Matches selectors
CSS_RULES_REGEXP = re.compile("([a-zA-Z0-9\.#-_:@]+[^{]*{[^}]*})") # Matches complete rules

class PortalView(BrowserView):
    """ Adds support for Portal View template """

    template = ViewPageTemplateFile('portalview.pt')
    
    def __init__(self, context, request):
        """ Sets up a few convenience object attributes """
        self.context = context
        self.request = request
        self.template.id = 'portalview'

    def __call__(self):
        return self.template()

    @property
    def boxToolsEnabled(self):
        """ Whether to show tools for boxes or not """
        mtool = getToolByName(self.context, "portal_membership")
        return mtool.checkPermission("Modify portal content", self.context)

    @property
    def menuBarEnabled(self):
        """ Whether to show the menu bar or not """
        return self.context.getMenuBarEnabled()

    @property
    def breadCrumbsHidden(self):
        """ Whether to gude the breadcrumbs or not """
        return self.context.getBreadCrumbsHidden()
        
    @property
    def prefixedStyles(self):
        """ Returns injectable CSS with #portalview prefix """
        css = CSS_COMMENTS_REGEXP.sub("", self.context.getCSS())

        for selector in CSS_SELECTORS_REGEXP.findall(css):
            parts = [part.strip() for part in selector.split(",")]
            css = css.replace(selector, ",\n#portalview ".join(parts) + " " )

        return "\n".join(["#portalview %(style)s" % vars() for style in
                          CSS_RULES_REGEXP.findall(css)])

    @property
    def columns(self):
        """ Returns columns with all visible boxes """
        return self._getColumns(anonymous=False)

    def _getColumns(self, anonymous=False):
        """ Returns columns with boxes (all visible or limited by anonymous) """
        root = "/".join(self.context.getPhysicalPath())

        results = self.__queryContents(anonymous)
        column_results, results_by_path = self.__extractResults(results)

        columns = []
        for column in column_results:
            path = column.getPath()
            parent = self.__getParentPath(path)
            if parent == root and results_by_path.has_key(path):
                columns.append(self.__column(column.getObject(), results_by_path))

        return columns

    def __column(self, column, results_by_path={}, id_prefix=''):
        """ Builds a column dict from column object and list of boxes """
        column_path = "/".join(column.getPhysicalPath())
        column_id = id_prefix + column.id
        column_width = column.get('width')
        boxes = [self.__box(column_id, box.getObject(), box.review_state, box.ExpirationDate, results_by_path) \
                 for box in results_by_path[column_path]]
        return {'wrapper': {'id': "portalview-column-wrapper-%(column_id)s" % vars(),
                            'class': " ".join(["portalViewColumnWrapper",
                                               "portalViewColumnWrapper-%(column_width)s" % vars()])},
                'id': "portalview-column-%(column_id)s" % vars(),
                'class': "portalViewColumn",
                'boxes': boxes}

    def __box(self, column_id, box, review_state, expires, results_by_path={}):
        """ Builds a box dict from box object """
        if box.portal_type == "Portal View Column Folder" \
           and results_by_path.has_key("/".join(box.getPhysicalPath())):
            return self.__column(box, results_by_path, "%(column_id)s-" % vars())
        else:
            box_id = box.id
            expired_state = expires and expires != 'None' and DateTime(expires) < DateTime() and " state-expired" or ""
            return {'wrapper': {'id': "portalview-box-wrapper-%(column_id)s-%(box_id)s" % vars(),
                                'class': " ".join(["portletWrapper",
                                                   "portalViewBoxWrapper",
                                                   "state-%(review_state)s%(expired_state)s" % vars()])},
                    'id': "portalview-box-%(column_id)s-%(box_id)s" % vars(),
                    'class': " ".join(["portlet",
                                       "portalViewBox",
                                       "portalViewBox-%(box_id)s" % vars()]),
                    'object': box}

    def __getParentPath(self, path):
        """ Returns path to parent from path """
        last_slash = path.rfind('/')
        if last_slash > -1:
            return path[:last_slash]
        else:
            return path

    # Handler for README.txt doctest
    def testQueryContents(self, anonymous=False):
        return self.__queryContents(anonymous)

    def __queryContents(self, anonymous=False):
        """ Returns query results for Portal View's contents """
        pc = getToolByName(self.context, 'portal_catalog')

        query = {
            'path'      : '/'.join(self.context.getPhysicalPath()),
            'sort_on'   : 'getObjPositionInParent',
            'sort_order': 'ascending'
            }

        portal_state = getMultiAdapter((self.context, self.request), name=u"plone_portal_state")

        results = []
        if portal_state.anonymous() or not anonymous:
            results.extend(pc.queryCatalog(query))
        else: # Anonymous like view for logged in members
            now = DateTime()
            query.update({
                'effectiveRange' : now,
                })
            results.extend([r for r in pc.queryCatalog(query) if r.review_state in \
                            ['published', 'public', 'visible', Missing.Value()]])
        return results

    # Handler for README.txt doctest
    def testExtractResults(self, results):
        return self.__extractResults(results)

    def __extractResults(self, results):
        """ Splits query results into columns and other content """
        column_results = []
        results_by_path = {}

        for brain in results:
            if brain.portal_type == 'Portal View Column Folder':
                column_results.append(brain)
            path = brain.getPath()
            parent = self.__getParentPath(path)
            if not results_by_path.has_key(parent):
                results_by_path[parent] = []
            results_by_path[parent].append(brain)

        return column_results, results_by_path

class AnonymousPortalView(PortalView):
    """ Adds support for Portal View template """

    def __call__(self):
        return self.template()
#        mtool = getToolByName(self.context, 'portal_membership')
#        if (self.context.getCacheable() is False or mtool.isAnonymousUser()):
#            return self.template()
#        else:
#            url = zapi.absoluteURL(self.context, self.request)
#            response = urllib2.urlopen(url)
#            return response.read()
    
    @property
    def boxToolsEnabled(self):
        """ Whether to show tools for boxes or not """
        return False

    @property
    def columns(self):
        """ Returns only columns with published boxes """
        return self._getColumns(anonymous=True)
