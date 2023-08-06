#!/bin/sh

cd `dirname $0`
cd ..

find . -type f -name .svnignore | while read a; do
    ( cd `dirname $a` && svn propset -R svn:ignore -F .svnignore . )
done

