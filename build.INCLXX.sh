#!/bin/sh

mkdir /software/incl-build/
cd /software/incl-build/
cmake ../incl-generic-interface/ -DINCL_SHARED_LIBS=TRUE
make
cd ../
