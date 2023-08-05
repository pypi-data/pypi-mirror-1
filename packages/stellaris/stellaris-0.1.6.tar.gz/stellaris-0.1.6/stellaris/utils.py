# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import os

def contextPath(view, context):
    if len(context) > 0 and context[0] == '/':
        context = context[1:]

    return os.path.join(view, context)        
