#!/bin/sh
TEMPLATES="find .. -name '*.*pt'"

i18ndude rebuild-pot --pot redturtle.smartlink.pot --create redturtle.smartlink $TEMPLATES 
i18ndude sync --pot redturtle.smartlink.pot redturtle.smartlink-it.po

