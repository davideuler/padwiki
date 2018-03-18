#!/bin/sh
#usage: ./benchmark.index.sh 2> performance.log
rm -rf db
rm -rf db.lucene
(time (make index) 1>&2)
