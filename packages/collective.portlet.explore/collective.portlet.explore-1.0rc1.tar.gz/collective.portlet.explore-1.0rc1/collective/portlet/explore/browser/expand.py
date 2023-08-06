from zope.interface import implements
from Acquisition import aq_inner
from kss.core import kssaction
from plone.portlets.utils import unhashPortletInfo
from plone.app.kss.plonekssview import PloneKSSView 
from plone.app.portlets.utils import assignment_from_key 
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.navtree import buildFolderTree


class DecorateStrategy:
    implements(INavtreeStrategy)

    def __init__(self, root, strategy):
        self.strategy=strategy
        self.root = "/".join(root.getPhysicalPath())
        self.showAllParents = True
        self.rootPath = "/".join(root.getParentNode().getPhysicalPath())

    def nodeFilter(self, node):
        if not self.strategy.nodeFilter(node):
            return False
        return node["item"].getPath().startswith(self.root+"/") or \
                 node["item"].getPath()==self.root

    def showChildrenOf(self, rootObject):
        return self.strategy.showChildrenOf(rootObject)

    def decoratorFactory(self, newNode):
        return self.strategy.decoratorFactory(newNode)

    def subtreeFilter(self, newNode):
        return self.strategy.subtreeFilter(newNode)


class ExpandMenu(PloneKSSView):
    recurse = ViewPageTemplateFile('../recurse.pt')

    @kssaction
    def expandNode(self, portlethash, uid):
        """Expand the navtree at a given UID for a given portlet.
        """

        rt=getToolByName(self.context, "reference_catalog")
        root=rt.lookupObject(uid)

        info=unhashPortletInfo(portlethash)
        assignment=assignment_from_key(self.context,
                info["manager"], info["category"], info["key"], info["name"])

        queryBuilder = getMultiAdapter((root, assignment),
                                       INavigationQueryBuilder)
        strategy = getMultiAdapter((aq_inner(self.context), assignment),
                                   INavtreeStrategy)
        strategy = DecorateStrategy(root, strategy)

        query=queryBuilder()

        data=buildFolderTree(root, query=query, strategy=strategy)
        html=self.recurse(children=data.get('children', []), level=1, bottomLevel=assignment.bottomLevel)

        core=self.getCommandSet("core")
        selector="div#portletwrapper-%s li.node-%s " % (portlethash, uid)

        core.replaceHTML(selector, html)

        selector="div#portletwrapper-%s span.kssattr-uid-%s" % (portlethash,uid)
        core.removeClass(selector, "toggleNode")
        core.removeClass(selector, "expandedNode")
        if len(data.get('children')) > 0 and len(data.get('children')[0].get('children')) > 0:
            core.addClass(selector, "expandedNode")
        else:
            core.addClass(selector, "noChildren")

