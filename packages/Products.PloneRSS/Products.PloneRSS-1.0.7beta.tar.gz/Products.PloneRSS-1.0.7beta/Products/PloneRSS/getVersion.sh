#!/bin/bash
vstr=`cat version.txt`
version1=`echo ${vstr}|cut -d" " -f1`
version2=`echo ${vstr}|cut -d" " -f3`
echo "${version1}.${version2}"
