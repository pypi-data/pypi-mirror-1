#!/bin/sh
PRODUCTNAME='collective.portlet.localcumulus'
I18NDOMAIN=$PRODUCTNAME
i18ndude=$(which i18ndude)
echo using $i18ndude
cd $(dirname $0)
# Synchronise the .pot with the templates.
$i18ndude rebuild-pot --pot locales/${PRODUCTNAME}.pot --merge locales/${PRODUCTNAME}-manual.pot --create ${I18NDOMAIN} .
# Synchronise the resulting .pot with the .po files
$i18ndude sync --pot locales/${PRODUCTNAME}.pot locales/fr/LC_MESSAGES/${PRODUCTNAME}.po


