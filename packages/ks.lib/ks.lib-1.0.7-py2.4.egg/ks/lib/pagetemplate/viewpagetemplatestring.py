### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""String-based page for the Zope 3 based ks.pagetemplate package

$Id: viewpagetemplatestring.py 23861 2007-11-25 00:13:00Z xen $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 23861 $"
__date__ = "$Date: 2007-11-25 02:13:00 +0200 (Sun, 25 Nov 2007) $"

from zope.pagetemplate.pagetemplate import PageTemplate
from zope.app.pagetemplate.viewpagetemplatefile import ViewMapper, BoundPageTemplate
from zope.app import zapi
from zope.app.pagetemplate.engine import TrustedAppPT

class ViewPageTemplateString(TrustedAppPT, PageTemplate):
    """Page Templates used as methods of views defined as Python classes.
    """

    def __init__(self, source=None, content_type=None):
        super(ViewPageTemplateString, self).__init__()
        if content_type is not None:
            self.content_type = content_type
        if source is not None:
            assert isinstance(source, basestring)
            self.write(source)

    def pt_getContext(self, instance, context, request, **_kw):
        # instance is a View component
        namespace = super(ViewPageTemplateString, self).pt_getContext(**_kw)
        namespace['request'] = request
        namespace['view'] = instance
        namespace['context'] = context
        namespace['views'] = ViewMapper(context, request)
        return namespace

    def __call__(self, instance, context, request, *args, **keywords):
        namespace = self.pt_getContext(
            instance=instance,
            context=context,
            request=request,
            args=args, options=keywords)
        debug_flags = request.debug
        s = self.pt_render(
            namespace,
            showtal=getattr(debug_flags, 'showTAL', 0),
            sourceAnnotations=getattr(debug_flags, 'sourceAnnotations', 0),
            )
        return s

    def __get__(self, instance, type):
        return BoundPageTemplateString(self, instance)

class BoundPageTemplateString(BoundPageTemplate):
      def __repr__(self):
        return "<BoundPageTemplateString of %r>" % self.im_self

