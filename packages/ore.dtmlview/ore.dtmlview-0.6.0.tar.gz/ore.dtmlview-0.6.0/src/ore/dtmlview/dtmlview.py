##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: dtmlview.py 2124 2007-11-26 21:56:25Z hazmat $
"""

import sys, os, mimetypes
from zope.component import getMultiAdapter
from zope.documenttemplate.dt_html import HTML

# source:
# from zope.app.pagetemplate.viewpagetemplatefile import ViewMapper

class ViewMapper(object):
    def __init__(self, ob, request):
        self.ob = ob
        self.request = request

    def __getitem__(self, name):
        return getMultiAdapter((self.ob, self.request), name=name)

# source:
# from zope.pagetemplate.pagetemplatefile import package_home
#
def package_home(gdict):
    filename = gdict["__file__"]
    return os.path.dirname(filename)


class DTMLViewFile( object ):

    dt_class = HTML

    _v_last_read = 0
    
    def __init__( self, filename, _prefix=None, content_type=None ):

        path = self.get_path_from_prefix(_prefix)
        self.filename = os.path.join(path, filename)
        if not os.path.isfile(self.filename):
            raise ValueError("No such file", self.filename)

        # try to guess mime based on file, else fallback to html
        if content_type is None: 
            content_type = mimetypes.guess_type( self.filename )[0]
            if content_type is None:
                content_type = 'text/html'
            
        self.content_type = content_type
        self._program = None
        self._text = u''
        self._read_file()
        
    def get_path_from_prefix(self, _prefix):
        if isinstance(_prefix, str):
            path = _prefix
        else:
            if _prefix is None:
                _prefix = sys._getframe(2).f_globals
            path = package_home(_prefix)
        return path

    def get_context( self, instance, request, *args, **kw ):
        namespace = dict(
            request = request,
            view = instance,
            context = instance.context,
            views=ViewMapper( instance.context, request ),            
            )
        kw.update( namespace )
        return kw
        
    def __getstate__(self):
        raise TypeError("non-picklable object")
    
    def _cook_check(self):
        if self._v_last_read and not __debug__:
            return
        __traceback_info__ = self.filename
        try:
            mtime = os.path.getmtime(self.filename)
        except OSError:
            mtime = 0
        if mtime == self._v_last_read:
            return
        self._read_file()
        if self._v_errors:
            logging.error('DocumentTemplateFile: Error in template %s: %s',
                    self.filename, '\n'.join(self._v_errors))
            return

    def _read_file( self ):
        """ read the file if not read, respect dev mode """
        self._program = self.dt_class( open( self.filename ).read() )
        self._v_last_read = os.path.getmtime( self.filename )
        
    def render( self, instance, *args, **kw ):
        """ render the template """
        self._cook_check()
        namespace = self.get_context( instance=instance, request=instance.request, *args, **kw )
        return self._program(instance.context, **namespace )

    __call__ = render
    
    def __get__( self, instance, type ):
        return BoundDocumentTemplate( self, instance )
    

class BoundDocumentTemplate( object ):
    def __init__(self, dt, ob):
        object.__setattr__( self, 'im_func', dt )
        object.__setattr__( self, 'im_self', ob )

    filename = property( lambda self: self.im_func.filename )

    def __call__( self, *args, **kw):
        if self.im_self is None:
            im_self, args = args[0], args[1:]
        else:
            im_self = self.im_self
        return self.im_func( im_self, *args, **kw)

    def __setattr__(self, name, v):
        raise AttributeError("Can't set attribute", name)

    def __repr__(self):
        return "<BoundDTMLFile of %r>" % self.im_self



    
