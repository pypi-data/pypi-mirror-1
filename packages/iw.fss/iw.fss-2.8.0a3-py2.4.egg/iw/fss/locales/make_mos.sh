#!/bin/sh
# $Id: make_mos.sh 66391 2008-06-09 17:38:35Z glenfant $
# Compile po files
for lang in $(find . -mindepth 1 -maxdepth 1 -type d); do
    if test -d $lang/LC_MESSAGES; then
        msgfmt -o $lang/LC_MESSAGES/iw.fss.mo $lang/LC_MESSAGES/iw.fss.po
    fi
done
