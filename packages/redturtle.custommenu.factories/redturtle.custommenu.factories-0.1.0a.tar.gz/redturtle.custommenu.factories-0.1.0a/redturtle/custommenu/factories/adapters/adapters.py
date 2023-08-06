# -*- coding: utf-8 -*-

from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from redturtle.custommenu.factories.interfaces import ICustomFactoryMenuProvider
from redturtle.custommenu.factories import custommenuMessageFactory as _

from Products.PageTemplates import Expressions
from zope.tales.tales import CompilerError

from zope.component import getMultiAdapter

class MenuCoreAdapter(object):

    def __init__(self, context):
        self.context = context

    def _formatNewEntry(self, customization, url, icon):
        """Return a menu-like structure with the new additional element"""
        return {'title'       : _(customization['element-name']),
                'description' : _(customization['element-descr']),
                'action'      : url,
                'selected'    : False,
                'icon'        : icon,
                'submenu'     : None,
                'extra'       : {'separator': None, 'id': customization['element-id'], 'class': ''},
                }

    def getMenuCustomization(self, data, results):
        raise NotImplementedError("You must provide the getMenuCustomization method")

class PloneSiteFactoryMenuAdapter(MenuCoreAdapter):
    implements(ICustomFactoryMenuProvider)

    def getMenuCustomization(self, data, results):
        """Get saved menu customization for a context that is the Plone site root
        @data: a dict object used for evaluate TALES expressions
        @results: a menu-like structure, normally obtained calling PloneFactoriesMenu.getMenuItems
        @return: the new menu-like structure, with additional customizations
        """
        context = self.context
        talEngine = Expressions.getEngine()
        view = getMultiAdapter((context, context.REQUEST), name=u'customize-factoriesmenu')

        newResults = []
        newIds = []
        extras, saved_customizations = view.getSavedCustomizations()
        for c in saved_customizations:
            condition = c['condition-tales']
            if condition:
                compiledCondition = talEngine.compile(condition)
                try:
                    result = compiledCondition(talEngine.getContext(data))
                except KeyError, inst:
                    print inst
                    continue
                if not result:
                    continue

            # URL
            url = talEngine.compile(c['element-tales'])
            try:
                compiledURL = url(talEngine.getContext(data))
            except KeyError, inst:
                print inst
                continue
            # ICON
            icon = talEngine.compile(c['icon-tales'])
            try:
                compiledIcon = icon(talEngine.getContext(data))
            except KeyError, inst:
                print inst
                compiledIcon = None
            
            if compiledURL:
                newElement = self._formatNewEntry(c, compiledURL, compiledIcon)
                if newElement['extra']['id']:
                    newIds.append(newElement['extra']['id'])
                newResults.append(newElement)

        # Spit off overriden elements, using id
        results = [x for x in results if x['extra']['id'] not in newIds]
        results.extend(newResults)
        return results

class FolderFactoryMenuAdapter(PloneSiteFactoryMenuAdapter):
    implements(ICustomFactoryMenuProvider)

    def getMenuCustomization(self, data, results):
        """Get saved menu customization from folderish content. Is also possible to inherit
        customization from the site root (if both inherit checks are True).
        @data: a dict object used for evaluate TALES expressions
        @results: a menu-like structure, normally obtained calling PloneFactoriesMenu.getMenuItems
        @return: the new menu-like structure, with additional customizations
        """
        context = self.context
        portal = getToolByName(context, 'portal_url').getPortalObject()
        viewOnPortal = getMultiAdapter((portal, context.REQUEST), name=u'customize-factoriesmenu')
        view = getMultiAdapter((context, context.REQUEST), name=u'customize-factoriesmenu')
        if viewOnPortal.inherit and view.inherit:
            siteResults = ICustomFactoryMenuProvider(portal).getMenuCustomization(data, results)
            results = PloneSiteFactoryMenuAdapter.getMenuCustomization(self, data, siteResults)
        else:
            results = PloneSiteFactoryMenuAdapter.getMenuCustomization(self, data, results)
        return results
