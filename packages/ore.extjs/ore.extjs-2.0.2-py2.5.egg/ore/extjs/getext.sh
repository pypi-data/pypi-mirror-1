#!/bin/bash
VERSION="2.0.2"
wget --continue http://extjs.com/deploy/ext-$VERSION.zip
unzip ext-$VERSION.zip
mv ext-$VERSION ext-2.0
