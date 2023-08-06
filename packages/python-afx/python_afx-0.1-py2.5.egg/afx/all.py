# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:et:sw=4:ts=4

import __init__
for pkg in __init__.__all__:
    exec 'from ' + pkg + ' import *'
