#!/bin/bash

#export PYTHONPATH=../..
for f in test*py
do
    python2.4 $f
done
