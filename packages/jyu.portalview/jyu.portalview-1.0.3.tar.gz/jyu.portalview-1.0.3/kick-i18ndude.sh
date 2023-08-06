#!/bin/bash

# Portal View
i18ndude rebuild-pot --pot jyu/portalview/locales/jyu.portalview.pot --create jyu.portalview jyu/portalview
i18ndude sync --pot jyu/portalview/locales/jyu.portalview.pot jyu/portalview/locales/*/LC_MESSAGES/jyu.portalview.po

# Plone
i18ndude rebuild-pot --pot jyu/portalview/i18n/plone.pot --create plone jyu/portalview/profiles
i18ndude sync --pot jyu/portalview/i18n/plone.pot jyu/portalview/i18n/plone-*.po