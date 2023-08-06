from zope.interface import Interface
from zope.schema import *
from zope.schema import vocabulary as schemavocab
from Products.CMFCore.utils import getToolByName 

from Products.CMFPlone import PloneMessageFactory as _

from collective.validator.base.interfaces.interfaces import IWebValidator
# Interfaces go here ...

class IW3cTransitional(IWebValidator):
    """Marker interface for the portal_transforms tool."""
