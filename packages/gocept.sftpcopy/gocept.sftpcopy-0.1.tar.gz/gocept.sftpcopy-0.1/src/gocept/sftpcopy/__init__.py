# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: __init__.py 5353 2007-10-26 07:57:18Z zagy $

import zope.deferredimport

zope.deferredimport.define(
    SFTPCopy = 'gocept.sftpcopy.sftpcopy:SFTPCopy'
    )
