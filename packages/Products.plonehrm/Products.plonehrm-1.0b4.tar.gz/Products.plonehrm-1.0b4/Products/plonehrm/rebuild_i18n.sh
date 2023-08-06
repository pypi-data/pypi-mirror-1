#!/bin/sh
PRODUCTNAME=plonehrm
I18NDOMAIN=$PRODUCTNAME

# Synchronise the .pot with the templates.
i18ndude rebuild-pot --pot locales/${PRODUCTNAME}.pot --create ${I18NDOMAIN} .

# Synchronise the resulting .pot with the .po files
i18ndude sync --pot locales/${PRODUCTNAME}.pot locales/nl/LC_MESSAGES/${PRODUCTNAME}.po
i18ndude sync --pot i18n/plone.pot i18n/plone-*.po

msgfmt -o locales/nl/LC_MESSAGES/${PRODUCTNAME}.mo locales/nl/LC_MESSAGES/${PRODUCTNAME}.po
