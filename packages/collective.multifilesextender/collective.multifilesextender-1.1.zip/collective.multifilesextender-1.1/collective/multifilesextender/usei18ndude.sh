#!/bin/bash
PRODUCT="collective.multifilesextender"

mkdir -p locales/cs/LC_MESSAGES/
mkdir -p locales/dk/LC_MESSAGES/
mkdir -p locales/en/LC_MESSAGES/
touch locales/manual.pot
touch locales/cs/LC_MESSAGES/$PRODUCT.po
touch locales/dk/LC_MESSAGES/$PRODUCT.po
touch locales/en/LC_MESSAGES/$PRODUCT.po

i18ndude rebuild-pot --pot locales/$PRODUCT.pot --create $PRODUCT --merge locales/manual.pot ../
i18ndude sync --pot locales/$PRODUCT.pot locales/cs/LC_MESSAGES/$PRODUCT.po
i18ndude sync --pot locales/$PRODUCT.pot locales/dk/LC_MESSAGES/$PRODUCT.po
i18ndude sync --pot locales/$PRODUCT.pot locales/en/LC_MESSAGES/$PRODUCT.po
