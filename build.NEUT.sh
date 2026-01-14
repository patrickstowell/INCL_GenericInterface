#!/bin/sh

mkdir /software/neut-build/
cd /software/neut-build/
cmake ../neut-generic-interface/ -DNEUT_INCLCXX_ENABLED=TRUE -DNEUT_NUHEPMC_ENABLED=FALSE
make
make install
cd ../
