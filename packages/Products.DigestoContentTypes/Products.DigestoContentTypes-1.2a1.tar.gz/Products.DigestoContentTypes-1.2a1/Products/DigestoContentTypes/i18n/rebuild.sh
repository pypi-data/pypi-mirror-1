#!/bin/bash

I18NDUDE=i18ndude

cd `dirname $0`

PRODUCT_DIR=`dirname $PWD`
PRODUCT=`basename $PRODUCT_DIR`
I18NDOMAIN=DigestoContentTypes
POT=$I18NDOMAIN.pot
LOG=rebuild.log

echo -n "Rebuilding to $POT, this can take a while..."

cp generated.pot temp.pot
i18ndude merge --pot temp.pot --merge manual.pot

# Using --merge the resulting file is kept sorted by msgid
$I18NDUDE rebuild-pot \
  --pot $POT \
  --create $I18NDOMAIN \
  --merge temp.pot \
  $PRODUCT_DIR/skins/ $PRODUCT_DIR/portlets/ $PRODUCT_DIR/browser/ $PRODUCT_DIR/validators/ >$LOG 2>&1


# Using --merge the resulting file is kept sorted by msgid
$I18NDUDE rebuild-pot \
  --pot $I18NDOMAIN-plone.pot \
  --create $I18NDOMAIN-plone \
  --merge manual-plone.pot \
  $PRODUCT_DIR/browser/templates/ >$LOG 2>&1


rm -f temp.pot

# Made paths relative to the Product directory
sed -ri "s,$PRODUCT_DIR,\.,g" $POT

echo " done. Full report at $LOG."

exit 0
