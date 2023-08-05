#!/bin/sh
TIMESTAMP=`date +%s`
BASE=files
find files/scanned/ -empty -delete
mkdir -p $BASE/scanning/scan-$TIMESTAMP
cd $BASE/scanning/scan-$TIMESTAMP
scanimage --batch --source "ADF Front" --resolution 300 --y-resolution 300
cd ../../..
mv $BASE/scanning/scan-$TIMESTAMP $BASE/scanned
