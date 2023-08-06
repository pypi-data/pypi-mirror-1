# -*- coding: utf-8 -*-

from Acquisition import aq_inner, aq_parent
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements
from zope.component import getMultiAdapter

from plone.app.contentmenu.menu import FactoriesMenu as PloneFactoriesMenu
from plone.app.contentmenu.interfaces import IFactoriesMenu
from Products.CMFCore.utils import getToolByName

from OFS.interfaces import IFolder

from redturtle.custommenu.factories import custommenuMessageFactory as _
from redturtle.custommenu.factories.config import ANN_CUSTOMMENU_KEY
from redturtle.custommenu.factories.interfaces import ICustomFactoryMenuProvider

class FactoriesMenu(PloneFactoriesMenu):
    implements(IFactoriesMenu)

    # Stolen from ploneview
    def isFolderOrFolderDefaultPage(self, context, request):
        context_state = getMultiAdapter((aq_inner(context), request), name=u'plone_context_state')
        return context_state.is_structural_folder() or context_state.is_default_page()

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        results = PloneFactoriesMenu.getMenuItems(self, context, request)
        portal_url = getToolByName(context, 'portal_url')

        # First of all, get the real context on the menu
        if IFolder.providedBy(context):
            folder = context
        elif self.isFolderOrFolderDefaultPage(context, request):
            folder = aq_parent(aq_inner(context))
        else:
            # don't know how to handle this
            folder = context

        data = {'context': context, 'portal_url': portal_url, 'container': folder}

        try:
            m_provider = ICustomFactoryMenuProvider(folder)
        except TypeError:
            # For any adaptation problem
            return results
        
        results = m_provider.getMenuCustomization(data, results)

        # Re-sort
        results.sort(lambda x, y: cmp(x['title'],y['title']))

        mtool = getToolByName(context, 'portal_membership')
        if not mtool.isAnonymousUser() and mtool.getAuthenticatedMember().has_permission('Customize menu: factories', folder):
            context_url = folder.absolute_url()
            results.append({'title'       : _(u'custommenu_manage_title', default=_(u'Customize menu\u2026')),
                            'description' : _(u'custommenu_manage_description', default=_(u'Manage custom elements of this menu')),
                            'action'      : context_url+'/@@customize-factoriesmenu',
                            'selected'    : False,
                            'icon'        : None,
                            'submenu'     : None,
                            'extra'       : {'separator': 'actionSeparator', 'id': 'customize-factoriesmenu', 'class': 'customize-menu'},
                            })
        return results

