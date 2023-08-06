from Acquisition import aq_base
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.publisher.interfaces.browser import IBrowserView
from Products.Five.browser import BrowserView


class ILastModifiedView(IBrowserView):
    def __call__():
        """Return the last modification date for an object.""" 


class CatalogableDublinCoreLastModified(BrowserView):
    implements(ILastModifiedView)

    def __call__(self):
        return self.context.modified()


class DCTimesLastModified(BrowserView):
    implements(ILastModifiedView)

    def __call__(self):
        return self.context.modified


class BrowserViewLastModified(BrowserView):
    implements(ILastModifiedView)

    def __call__(self):
        if not hasattr(aq_base(self.context), "context"):
            return None

        context=aq_base(self.context.context)
        view=getMultiAdapter((context, self.request), name="lastmodified")
        if view is None:
            return None

        return view()


class FallbackLastModified(BrowserView):
    implements(ILastModifiedView)

    def __call__(self):
        m=getattr(self.context, "modified", None)
        if callable(m):
            return m()
        else:
            return m

