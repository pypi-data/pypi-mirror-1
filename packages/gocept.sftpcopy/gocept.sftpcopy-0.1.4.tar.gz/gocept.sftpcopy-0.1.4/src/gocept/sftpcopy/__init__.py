# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: __init__.py 5377 2007-11-13 07:53:32Z zagy $

import zope.deferredimport

zope.deferredimport.define(
    SFTPCopy = 'gocept.sftpcopy.sftpcopy:SFTPCopy'
    )
