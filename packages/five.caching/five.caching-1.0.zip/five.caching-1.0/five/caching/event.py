from zope.interface import Interface
from zope.component import adapter
from plone.postpublicationhook.interfaces import IAfterPublicationEvent
from Products.CMFCore.utils import getToolByName
from z3c.caching.registry import lookup
import logging
import types

logger = logging.getLogger("LogRequest")

@adapter(Interface, IAfterPublicationEvent)
def CacheHandler(object, event):
    if isinstance(object, types.MethodType) and object.im_self is not None:
        object=object.im_self

    rule=lookup(object)
    if rule is None:
        return
    event.request.response.setHeader("X-Cache-Rule", rule)

    ct=getToolByName(object, "portal_cache_settings", None)
    if ct is None or not ct.getEnabled():
        return

    pm=getToolByName(object, "portal_membership")
    if pm is None:
        return

    rule=getattr(ct.getRules(), rule, None)
    if rule is None:
        return
    
    view = None
    # CacheFu wants to get None and not a special user object
    if pm.isAnonymousUser():
        member = None
    else:
        member = pm.getAuthenticatedMember()
    header_set = rule._getHeaderSet(event.request, object, view, member)
    if header_set is None:
        return
    expr_context=rule._getExpressionContext(event.request, object, view, member, {})
    (add,remove)=header_set.getHeaders(expr_context)

    response=event.request.response

    for h in remove:
        if response.headers.has_key(h.lower()):
            del response.headers[h.lower()]
        elif response.headers.has_key(h):
            del response.headers[h]
    for key, value in add:
        if key == 'ETag':
            response.setHeader(key, value, literal=True)
        else:
            response.setHeader(key, value)

