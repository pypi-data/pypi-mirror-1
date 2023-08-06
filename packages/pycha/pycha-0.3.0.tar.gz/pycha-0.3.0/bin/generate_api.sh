#!/bin/sh

HTDOCS=$1
REPO=$2

# get a checkout
cd ${HTDOCS}
svn co -q file://${REPO}/trunk/src pycha

# Generate the html files
pydoc -w pycha.bar
pydoc -w pycha.chart
pydoc -w pycha.color
pydoc -w pycha.line
pydoc -w pycha.pie

# clean the checkout
rm -rf pycha

# setup ownership
chown apache:apache *.html
