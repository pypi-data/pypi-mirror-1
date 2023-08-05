#!/usr/bin/env bash

cd "$( dirname "$0" )"
. common.bash

pkg=python-commons
. simple-setup.bash

install lib/python2.4/site-packages src/commons
