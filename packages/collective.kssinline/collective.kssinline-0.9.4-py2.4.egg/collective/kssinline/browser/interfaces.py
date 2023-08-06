from zope.viewlet.interfaces import IViewletManager
from zope.interface import Interface

class IContentLinks(IViewletManager):
    """ 
    A viewlet manager for inserting extra navigation links 
    for an item.
    """

class ILinkableItem(Interface):
    """
    A class which understands the format of item and 
    provides information from it.
    """

    def obj(item):
        """
        Return object
        """

    def uid(item):
        """
        Return UID
        """

    def url(item):
        """
        Return absolute url
        """

class ILinkableItemView(Interface):
    """
    A class which understands the format of item and 
    provides information from it.
    Apply this as a marker interface to views.
    """

    def obj(item):
        """
        Return object
        """

    def uid(item):
        """
        Return UID
        """

    def url(item):
        """
        Return absolute url
        """
