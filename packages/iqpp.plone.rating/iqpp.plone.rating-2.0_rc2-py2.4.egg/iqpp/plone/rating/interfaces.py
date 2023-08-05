# zope imports
from zope import schema
from zope.interface import Interface
from zope.i18nmessageid import MessageFactory
from zope.viewlet.interfaces import IViewletManager
_ = MessageFactory('iqpp.plone.rating')

# iqpp.rating imports
from iqpp.rating.interfaces import IRatingOptions

class IRatingPortletViewletManager(IViewletManager):
    """
    """