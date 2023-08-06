# -*- coding: utf-8 -*-
from zope.component import getMultiAdapter
from cStringIO import StringIO

from Acquisition import aq_inner
from AccessControl import getSecurityManager

from plone.app.layout.viewlets import common
from plone.app.layout.navigation.navtree import buildFolderTree

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.browser.navtree import SitemapQueryBuilder

from plone.memoize import ram
from plone.memoize.compress import xhtml_compress

def _render_sections_cachekey(fun, self):
    key = StringIO()
    
    print >> key, self.__class__
    print >> key, getToolByName(aq_inner(self.context), 'portal_url')()
    print >> key, self.request.get('LANGUAGE', 'de')

    catalog = getToolByName(self.context, 'portal_catalog')
    counter = catalog.getCounter()
    print >> key, counter
    print >> key, aq_inner(self.context).getPhysicalPath()
    
    user = getSecurityManager().getUser()
    roles = user.getRolesInContext(aq_inner(self.context))
    print >> key, roles

    return key.getvalue()
    
class SuperFishQueryBuilder(SitemapQueryBuilder):
    """Build a folder tree query suitable for a dropdownmenu
    """
    
    def __init__(self, context):
        super(SuperFishQueryBuilder, self).__init__(context)
        
        portal_state = getMultiAdapter(
            (context, context.REQUEST), name=u'plone_portal_state')
        
        self.query['path']['query'] = portal_state.navigation_root_path()
        
class SuperFishViewlet(common.ViewletBase):

    index = ViewPageTemplateFile('sections.pt')
    portal_tabs = []
    
    # monkey patch this if you want to use collective.superfish together with 
    # global_sections, need another start level or menu depth.
    menu_id = 'portal-globalnav'
    menu_depth = 2
    
    # this template is used to generate a single menu item.
    _menu_item = u"""
    <li id="%(menu_id)s-item-%(id)s"%(classnames)s><span%(selected)s
        ><a href="%(url)s" title="%(description)s">
            %(title)s
        </a></span>%(submenu)s </li>"""
    
    # this template is used to generate a menu container
    _submenu_item = u"""\n<ul%(id)s class="%(classname)s">%(menuitems)s</ul>"""
    
    def __init__(self, *args):
        super(SuperFishViewlet, self).__init__(*args)
        
        context_state = getMultiAdapter(
            (self.context, self.request), name=u'plone_context_state')
        portal_state = getMultiAdapter(
            (self.context, self.request), name=u'plone_portal_state')
        
        self.current_url = context_state.current_page_url()
        self.site_url = portal_state.portal_url()
        self.navigation_root_path = portal_state.navigation_root_path()
    
    def _build_navtree(self):
        # we generate our navigation out of the sitemap. so we can use the 
        # highspeed navtree generation, and use it's caching features too.
        query = SuperFishQueryBuilder(self.context)()
        query['path']['depth'] = self.menu_depth
        
        # no special strategy needed, so i kicked the INavtreeStrategy lookup.
        return buildFolderTree(self.context, obj=self.context, query=query)
    
    def update(self):
        self.data = self._build_navtree()
    
    def portal_tabs(self):
        """We do not want to use the template-code any more. 
           Python code should speedup rendering."""
        
        def submenu(items, menu_id=None, menu_level=0, menu_classnames=''):
            # unsure this is needed any more...
            #if self.menu_depth>0 and menu_level>self.menu_depth:
            #    # finish if we reach the maximum level
            #    return 
            
            i = 0
            s = []
            
            # exclude nav items
            items = [item for item in items 
                        if not item['item'].exclude_from_nav]
            
            if not items:
                return ''
            
            for item in items:
                first = i==0
                i += 1
                last  = i==len(items)
                
                s.append(menuitem(item, first, last, menu_level))
            
            return self._submenu_item % dict(
                menuitems=u"".join(s),
                id=menu_id and u" id=\"%s\"" % (menu_id) or u"",
                classname=u"navTreeLevel%d %s" % (menu_level, menu_classnames))
        
        def menuitem(item, first=False, last=False, menu_level=0):
            classes = []
            
            if first: classes.append('firstItem')
            if last: classes.append('lastItem')
            if self.current_url.startswith(item['item'].getURL()):
                classes.append('navTreeItemInPath')
            
            return self._menu_item % dict(
                menu_id=self.menu_id,
                id=item['item'].id,
                title=safe_unicode(item['item'].Title),
                description=safe_unicode(item['item'].Description),
                url=item['item'].getURL(),
                classnames=len(classes) and 
                    u' class="%s"' % (" ".join(classes)) or u"",
                selected=item['currentItem'] and u' class="selected"' or u"",
                submenu=submenu(item['children'], 
                                menu_level = menu_level + 1) or u"")
        
        if self.data:
            return submenu(self.data['children'], 
                           menu_id=u"portal-globalnav",
                           menu_classnames=u"sf-menu")
    
    @ram.cache(_render_sections_cachekey)
    def render(self):
        return xhtml_compress(self.index())
