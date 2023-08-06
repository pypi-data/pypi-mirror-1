#!/bin/bash

##
## Compile all '.po' files (into '.mo' files).
##
## Syntax: ./compile.sh
##

for file in `find . -name *.po`
do
    output=`echo $file | sed s/\\.po/\\.mo/g`
    msgfmt -o $output -v $file
done