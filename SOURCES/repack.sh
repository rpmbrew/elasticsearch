#!/bin/sh
NAME=$1
FNAME=$NAME.tar.gz

if [ -e $NAME ]  ; then
 echo  "$NAME exists. Remove it in orderto continue"
 exit -1
fi
tar -xf $FNAME
pushd $NAME
rm -rf .git
pushd bin
rm elasticsearch elasticsearch.bat elasticsearch-service-mgr.exe elasticsearch-service-x64.exe elasticsearch-service-x86.exe plugin plugin.bat service.bat
popd;
rm -rf lib
popd;
tar -cJf $NAME-fedora.tar.xz $NAME
rm -rf $NAME 
