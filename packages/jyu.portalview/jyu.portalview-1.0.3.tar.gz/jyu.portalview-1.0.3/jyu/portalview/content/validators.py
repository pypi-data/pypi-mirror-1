from Products.validation.interfaces import ivalidator

from jyu.portalview import PortalViewMessageFactory as _

from jyu.portalview.browser.viewlets import HTML_UL_REGEXP, MenuBarViewlet

from elementtree.ElementTree import fromstring

class MenuBarValidator:
    __implements__ = (ivalidator,)

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        items = []
        for ul in HTML_UL_REGEXP.findall(value):
            try:
                div = fromstring("<div>%(ul)s</div>" % vars())
            except:
                return _(u"Syntax error. Input contains broken or open HTML tags.")

            for results in [MenuBarViewlet.parse(el) for el in div.findall('ul')]:
                items.extend(results)

        if value and not items:
            return _(u"Couldn't extract any menu bar items. Please, check that your input is valid HTML.")
