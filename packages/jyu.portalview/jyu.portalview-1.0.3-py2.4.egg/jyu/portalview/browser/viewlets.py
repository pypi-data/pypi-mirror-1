from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

from elementtree.ElementTree import fromstring

import re

HTML_UL_REGEXP = re.compile("(<ul[^>]*>.*</ul>)", re.DOTALL)

class MenuBarViewlet(ViewletBase):
    render = ViewPageTemplateFile('menubar.pt')

    @staticmethod
    def parse(ul, deeper=True):
        """ Parses menubar link structure from the ElementTree UL-element
            recursively down to the second level. E.g.::

                <ul>
                  <li><a href="" title="" accesskey="" target=""></a>
                    <ul>
                      <li><a href="" title="" accesskey="" target=""></a></li>
                      <li><a href="" title="" accesskey="" target=""></a></li>
                    </ul>
                  </li>
                  <li><a href="" title="" accesskey="" target=""></a>
                    <ul>
                      <li><a href="" title="" accesskey="" target=""></a></li>
                      <li><a href="" title="" accesskey="" target=""></a></li>
                    </ul>
                  </li>
                <ul>
        """
        items = []
        for li in (ul and ul.findall('li') or []):
            link = li.find('a')
            if link is not None:
                items.append({
                    'text': link.text or None,
                    'href': link.get('href', None),
                    'title': link.get('title', None),
                    'target': link.get('target', None),
                    'accesskey': link.get('accesskey', None),
                    'subitems': deeper and MenuBarViewlet.parse(li.find('ul'), False) or None,
                    })
            else:
                items.append({
                    'text': None,
                    'href': None,
                    'title': None,
                    'target': None,
                    'accesskey': None,
                    'subitems': None,
                    })
        return items

    def update(self):
        """ Sets when the menubar should be rendered and, if it will be rendered,
            updates its contents.

            Menu bar will be rendered if:
            - the portal_type of the context is Portal View
            - and menubar is enabled on the Portal View
            - and the current view is either *view* or *organize*
            - and proper menubar contents is found
        """
        if self.context.portal_type == "Portal View" \
            and self.request.getURL().split('/')[-1] in ['view', 'organize', '', self.context.id]:
            enabled = self.context.getMenuBarEnabled()

            # The data is parsed by grepping the outmost <ul></ul>s and
            # parsing the menu bar structure from them. That should be
            # safer than just trust the data and flush as its given. This
            # should be also more Zopeish, since the final menu bar list
            # is rendered by using TAL.
            data = HTML_UL_REGEXP.findall(self.context.getMenuBarContents())
            if enabled and len(data):
                items = []
                for ul in data:
                    try:
                        div = fromstring("<div>%(ul)s</div>" % vars())
                    except:
                        # Couldn't parse contents. Let's try to next <ul></ul> pair.
                        continue
                    for results in [MenuBarViewlet.parse(el) for el in div.findall('ul')]:
                        items.extend(results)
                if items:
                    self.menuitems = items
                    self.enabled = True
                else:
                    self.enabled = False
            else:
                self.enabled = False
        else:
            self.enabled = False
