#!/bin/bash

I18NDUDE=i18ndude

cd `dirname $0`

for PO in DigestoContentTypes-??.po DigestoContentTypes-??-??.po ; do
    $I18NDUDE sync --pot DigestoContentTypes.pot $PO
done

for PO in DigestoContentTypes-plone*.po ; do
    $I18NDUDE sync --pot DigestoContentTypes-plone.pot $PO
done

for PO in DigestoContentTypes-*plone.po ; do
    $I18NDUDE sync --pot DigestoContentTypes-plone.pot $PO
done
