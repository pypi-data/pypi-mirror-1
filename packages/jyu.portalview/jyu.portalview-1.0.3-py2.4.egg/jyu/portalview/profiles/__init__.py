## This is needed only for i18ndude to detect some implicit messageids
from zope.i18nmessageid import Message as _ # allows explicit domain

schemata_labels = [_(u"label_schema_menubar", domain="plone")]

error_messages = [_(u"Couldn't extract any menu bar items. Please, check that your input is valid HTML.", domain="plone"),
                  _(u"Syntax error. Input contains broken or open HTML tags.", domain="plone")]

##
