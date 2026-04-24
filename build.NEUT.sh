#!/bin/sh

mkdir /software/neut-merge-test/
cd /software/neut-merge-test/
cmake ../neut-generic-interface/ -DNEUT_INCLCXX_ENABLED=TRUE -DNEUT_NUHEPMC_ENABLED=FALSE
make -j12
make install
cd ../
