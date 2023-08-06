#!/usr/bin/env bash

cd "$( dirname "$0" )"
. common.bash

pkg=afx
. simple-setup.bash

install lib/python2.5/site-packages/ src/afx
