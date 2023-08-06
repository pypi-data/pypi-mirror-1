# -*- coding: utf-8 -*-

from zope.interface import Interface

class ICustomMenuEnabled(Interface):
    """Marker interface for content that use custom menu"""

class ICustomFactoryMenuProvider(Interface):
    """Interface for adapters that provide customization for factory menu"""