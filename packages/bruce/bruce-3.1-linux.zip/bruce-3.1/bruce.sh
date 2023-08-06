#! /usr/bin/env python

import sys
# force module loading from my zip file first
sys.path.insert(0, 'bruce-library.zip')

from bruce import run
run.main()
