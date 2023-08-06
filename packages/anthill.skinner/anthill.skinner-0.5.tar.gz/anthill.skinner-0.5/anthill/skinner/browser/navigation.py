
from zope.interface import implements
from Acquisition import aq_inner, aq_parent
from zope.component import queryMultiAdapter

from zope.contentprovider.interfaces import IContentProvider

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IFolderish

import plone.app.layout.viewlets.common
import plone.app.portlets.portlets.navigation

from anthill.tal.macrorenderer import MacroRenderer

from interfaces import INavigationBase, ICustomMenuParameters

class NavigationBase(BrowserView):
    """ @see: INavigationBase """

    implements(INavigationBase)

    def __init__(self, context, request):
        self.context = aq_inner(context)
        self.request = request

    def _render_viewlet(self, factory):
        # shamelessly copied from collective.skinny
        viewlet = factory(self.context, self.request, None, None).__of__(self.context)
        viewlet.update()
        return viewlet.render()

    def renderPathBar(self):
        return self._render_viewlet(plone.app.layout.viewlets.common.PathBarViewlet)

    def renderNavigation(self):
        return self._render_viewlet(plone.app.layout.viewlets.common.GlobalSectionsViewlet)

    def renderBackToCMSLink(self):
        return '<a href="%s/@@skinner/deactivatePreview" i18n:translate="">Back to Plone</a>' % self.context.absolute_url()

    def _folderishContextOf(self, ct):
        folder = aq_inner(ct)
        if not IFolderish.providedBy(folder):
            folder = aq_parent(folder)
        return folder

    def menuIsActive(self, topLevel, bottomLevel):
        # algorithm is as follows:
        # - get the plone root path
        # - get the context path (folderish)
        # - check if current level of path == topLevel - 1 and < bottomLevel 
        # - check if there are any items displayable

        purl = getToolByName(self.context, 'portal_url')
        portal = aq_inner(purl.getPortalObject())

        # shortcuts
        if topLevel <= 0:
            return True

        # submenu of portal should always be active
        _fd = self._folderishContextOf(self.context)
        if _fd is portal:
            return False

        portalpath = aq_inner(portal).getPhysicalPath()
        currentpath = _fd.getPhysicalPath()
        level = len(currentpath[len(portalpath):])

        levelok = (level >= (topLevel) and level <= bottomLevel)

        # it is a bit tricky to determine if there are items to be displayed
        # because we can't rely on a simple getFolderContents or such. Instead
        # we need to load the navtree engine and then check if there are any items
        # provided. This is a bit slow but there is no other way. We use the data
        # provided by PublicMenu here.
        cnav = queryMultiAdapter( (self.context, self.request, self), 
                                    name = u'anthill.skinner.PublicMenu')
        cnav.update()
        navok = len(cnav.data['children']) > 0

        return levelok and navok

class CustomNavigation(object):
    """ Custom navigation that relies on standard plone engine but simplifies life a bit
        by using templates diectly accessible by the user. """

    implements(ICustomMenuParameters, IContentProvider)

    enclosing_tag = None
    includeTop = True
    topLevel = 1
    bottomLevel = 65536

    def __init__(self, context, request, view):
        self.context = aq_inner(context)
        self.request = request
        self.__parent__ = view

    def update(self):
        # we use Renderer directly here (querying multi adapter would be too
        # complicated for a portlet) in order to mimic the navtree portlet
        # as much as possible

        data = plone.app.portlets.portlets.navigation.Assignment('publicmenu',
                    currentFolderOnly=False, includeTop=self.includeTop,
                    topLevel=self.topLevel, bottomLevel=self.bottomLevel)

        self.navrenderer = plone.app.portlets.portlets.navigation.Renderer(
                                            self.context, self.request,
                                            view=None, manager=None, 
                                            data=data)

        self.data = self.navrenderer.getNavTree()
        self.navroot = self.navrenderer.getNavRoot()

    def _computeMacroName(self, level, template):
        # we compute the macro name to be used. This is needed
        # because macro levels can be 'acquired'. If there is for
        # example no macro for level n we search for a def for n-1

        levels = range(level); levels.reverse();
        for n in levels:
            try:
                name = 'level_%s' % int(n)
                template.macros[name]
                return name
            except KeyError:
                continue

        raise Exception, 'You seem to have forgotten to define macro levels!'

    def _recurse(self, template, level, node):
        output = u''
        if level <= 0 or level <= self.bottomLevel:
            children = node.get('children', [])
            for child in children:
                data = {'item' : child,
                        'isGlobalCurrent' : child['currentItem']}

                renderer = MacroRenderer(template, self._computeMacroName(level, template))
                output += renderer(data=data)

                if len(child['children']) > 0 and child['show_children']:
                    output += self._recurse(template, level+1, child)

        return output

    def render(self):

        # load template (residing in portal_skins to ease customization)
        navtemplate = self.context.unrestrictedTraverse('publicmenu_levels')

        struct = {}
        for name in ['include_top', 'root_item_class', 'root_is_portal', 'navigation_root']:
            struct[name] = getattr(self.navrenderer, name)
       
        defout = u'%s'; output = u''
        if self.enclosing_tag != None:
            defout = '<%(tag)s>%%s<%(tag)s>' % {'tag' : self.enclosing_tag} 

        # render root item first and then children
        output += MacroRenderer(navtemplate, 'rootitem')(data=struct)
        output += self._recurse(navtemplate, level=1, node=self.data)

        return defout % output

