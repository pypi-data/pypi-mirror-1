#!/bin/bash -x

# start with ./use18ndude.sh 

PRODUCT="collective.calendarwidget"

# if you want to add new language, replace language code, 
# uncomment and run these two commands: 
# mkdir -p locales/de/LC_MESSAGES/
# touch locales/de/LC_MESSAGES/$PRODUCT.po 

i18ndude rebuild-pot --pot locales/$PRODUCT.pot --create $PRODUCT ./
i18ndude sync --pot locales/$PRODUCT.pot locales/*/LC_MESSAGES/$PRODUCT.po 

