#!/bin/sh
make build
(time (make split ) 1>&2 )
(time (make indexinput ) 1>&2 )
#time (make index)
