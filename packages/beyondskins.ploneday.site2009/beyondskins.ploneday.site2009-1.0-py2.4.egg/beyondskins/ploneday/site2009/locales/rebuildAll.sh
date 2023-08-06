#!/bin/bash
# kudos to Products.Ploneboard for the base for this file
# ensure that when something is wrong, nothing is broken more than it should...
set -e

# first, create some pot containing anything
i18ndude rebuild-pot --pot beyondskins.ploneday.site2009.pot --create beyondskins.ploneday.site2009 --merge manual.pot ../*

# finally, update the po files
i18ndude sync --pot beyondskins.ploneday.site2009.pot  `find . -iregex '.*\.po$'|grep -v plone`

