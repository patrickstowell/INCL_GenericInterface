#!/bin/sh

mkdir /software/neut-build/
cd /software/neut-build/
cmake ../neut-generic-interface/ -DNEUT_INCLCXX_ENABLED=TRUE
make
make install
cd ../
