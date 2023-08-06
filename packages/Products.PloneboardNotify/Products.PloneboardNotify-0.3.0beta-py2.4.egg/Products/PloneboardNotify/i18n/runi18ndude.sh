#!/bin/sh
TEMPLATES="find .. -name '*.*pt'"

i18ndude rebuild-pot --pot Products.PloneboardNotify.pot --create Products.PloneboardNotify $TEMPLATES 
i18ndude sync --pot Products.PloneboardNotify.pot Products.PloneboardNotify-it.po

