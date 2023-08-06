#!/bin/sh
TEMPLATES=`find .. -name '*.*pt'`

i18ndude rebuild-pot --pot signupsheet.pot --create signupsheet --merge manual.pot $TEMPLATES
i18ndude sync --pot signupsheet.pot signupsheet-??.po
