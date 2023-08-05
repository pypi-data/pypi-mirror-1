#!/bin/sh

i18ndude rebuild-pot --pot rating.pot --create rating --merge extra.pot ..
i18ndude sync --pot rating.pot de/LC_MESSAGES/rating.po

for lang in $(find ../locales -mindepth 1 -maxdepth 1 -type d); do
    if test -d $lang/LC_MESSAGES; then
        msgfmt -o $lang/LC_MESSAGES/rating.mo $lang/LC_MESSAGES/rating.po
    fi
done