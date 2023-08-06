#!/bin/bash

cd ~/FLIES/code/mtrax
stdeb_run_setup --default-distribution feisty-ads
version=`cat version.txt`
cd deb_dist/mtrax-$version
echo "**********************************************************"
dpkg-buildpackage -rfakeroot -uc -us
cd ..
echo "**********************************************************"
dput private mtrax_$version-1*changes
