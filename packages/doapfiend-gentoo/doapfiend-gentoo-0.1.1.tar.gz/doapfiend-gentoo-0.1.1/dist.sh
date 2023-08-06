#!/bin/bash

sudo python setup.py develop --uninstall && sudo python setup.py sdist bdist_egg && scp dist/* cakebread@doapspace.org:webapps/static/doapfiend-gentoo/dist/
