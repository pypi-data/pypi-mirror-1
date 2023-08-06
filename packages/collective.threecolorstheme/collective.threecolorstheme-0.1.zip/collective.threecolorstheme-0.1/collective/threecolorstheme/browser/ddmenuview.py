# -*- coding: utf-8 -*-
## Copyright (C) 2006 Ingeniweb - all rights reserved
## No publication or distribution without authorization.

from DateTime import DateTime
from zope.component import getMultiAdapter
from zope.app.component.hooks import getSite
from Acquisition import aq_inner
from AccessControl import getSecurityManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView


from plone.memoize.ram import global_cache

# CMF imports
from Products.CMFCore.utils import getToolByName

# Product import
from collective.threecolorstheme import config

   

class GlobalSectionsView(BrowserView):
            
    
    
    def _typesToList(self):
        """
        return types to list in navtree
        """                
        context = aq_inner(self.context)
        ntp = getToolByName(context, 'portal_properties').navtree_properties
        ttool = getToolByName(context, 'portal_types')
        bl = ntp.getProperty('metaTypesNotToList', ())
        bl_dict = {}
        for t in bl:
            bl_dict[t] = 1
        all_types = ttool.listContentTypes()
        wl = [t for t in all_types if not bl_dict.has_key(t)]
        return wl


    def _getSubTabs(self, subpath, level=0):
        """
         getSubContents tabs from a path (or canonical path)
         resursively for an infinite drop down menu
         according to navtree properties, site properties 
         and linguaface presence or not
        """
        if level :
            level +=1  
        # print '%s : %s' %(level, subpath)
        context = aq_inner(self.context)
        cat = getToolByName(context, "portal_catalog") 
        ntp = getToolByName(context, 'portal_properties').navtree_properties
        stp = getToolByName(context, 'portal_properties').site_properties
        lf_tool = getToolByName(context, 'linguaface_tool', None)
        view_action_types = stp.getProperty('typesUseViewActionInListings', ())
        parentTypesNQ = ntp.getProperty('parentMetaTypesNotToQuery', ())
        ids_not_to_list = ntp.getProperty('idsNotToList', ())
        excluded_ids = {}
        for exc_id in ids_not_to_list:
            excluded_ids[exc_id] = 1
        crit = {}
        path = {}
        path['query'] = subpath
        path['depth'] = 1
        if lf_tool is not None :
            crit['getCanonicalPath'] = path
        else :
            crit['path'] = path    
        if ntp.getProperty('sortAttribute', False):
            crit['sort_on'] = ntp.sortAttribute
        if (ntp.getProperty('sortAttribute', False) and
            ntp.getProperty('sortOrder', False)):
            crit['sort_order'] = ntp.sortOrder
        if ntp.getProperty('enable_wf_state_filtering', False):
            crit['review_state'] = ntp.wf_states_to_show
        crit['is_default_page'] = False
        if config.TYPES_FOR_DD_MENUS :
            crit['portal_type'] = config.TYPES_FOR_DD_MENUS
        else :
            crit['portal_type'] = self._typesToList()
            
        results = cat.searchResults(**crit)
        tabs = []
        for r in results :
            tab={}
            tab_id = r.getId
            tab['id'] = tab_id
            tab['title'] = r.pretty_title_or_id()
            navUrl = r.getURL()
            navType = r.portal_type
            if navType in view_action_types :
                navUrl += '/view'
            tab['url'] = navUrl
            tab['description'] = r.Description
            tab['subtabs'] = []
            do_not_display = ( excluded_ids.has_key(tab_id) or
                               not not getattr(r, 'exclude_from_nav', True))            
            if r.is_folderish and navType not in parentTypesNQ and (level < config.LEVELS_FOR_DD_MENUS or not level) \
               and not do_not_display :
                if tab.has_key('canonical-path'):
                    tab['subtabs'] = self._getSubTabs('/'.join(tab['canonical-path']), level = level)
                else :
                    tab['subtabs'] = self._getSubTabs('%s/%s' %(subpath, tab_id), level = level)                      
            if not do_not_display :
                tabs.append(tab)
        return tabs               
        

    def _getGlobalSections(self):
                
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        actions = context_state.actions()
        
        portal_tabs_view = getMultiAdapter((self.context, self.request),
                                           name='portal_tabs_view')
        return portal_tabs_view.topLevelTabs(actions=actions)
        

    def portal_tabs(self):
        """
         return portal_tabs + subtabs 
        """                

        portal_tabs = self._getGlobalSections()
        
        portal = getSite()
        
        portalId = portal.getId()
        
        for tab in portal_tabs :          
            tab['subtabs'] = ''            
            if config.LEVELS_FOR_DD_MENUS > 1 or not config.LEVELS_FOR_DD_MENUS :  
                if tab.has_key('canonical-path') :
                    if tab['canonical-path'] :
                        tab['subtabs'] = self._getSubTabs('/'.join(tab['canonical-path']), level=1)  
                else :    
                    subpath = '/%s/%s' %(portalId, tab['id'])
                    tab['subtabs'] = self._getSubTabs(subpath, level=1)
                
        return portal_tabs      
        

    def _getLastModification(self):
        """
        Return last modification date + uid
        """
        context = aq_inner(self.context)
        ct = getToolByName(context, 'portal_catalog')
        lastPublishedResult = ct.searchResults(sort_on='modified',\
                                               sort_order='reverse',\
                                               sort_limit=1)[:1]
        
        lastModification = lastPublishedResult[0]
        return lastModification.modified, lastModification.UID
        
        
    def headers_define(self):
        """
        return True when menu can be cached
        """        
        context = aq_inner(self.context)
        request = self.request
        response = request.RESPONSE
        pm = getToolByName(context, 'portal_membership')
        ptp = getToolByName(context, 'portal_properties')
        stp = ptp.site_properties
        charset = stp.getProperty('default_charset', 'utf-8')
        currentDate = str((DateTime()).toZone('GMT').rfc822()).replace('+0000','GMT')
        refreshRequest = request.HTTP_PRAGMA
        requestedEtag = request.HTTP_IF_NONE_MATCH  
        requestedLang = request.HTTP_ACCEPT_LANGUAGE [:2]
        forceRefresh = 0
        requestFormKeys = request.form.keys()
        if '-C' in requestFormKeys :
            requestFormKeys.remove('-C')
        if request.REQUEST_METHOD.lower() == 'post' :
            forceRefresh = 1    
        elif len(requestFormKeys) :
            forceRefresh = 1
        max_age = 0
        cache_actions = 'must-revalidate,proxy-revalidate'

        if pm.isAnonymousUser() :
            user = 'anonymous'
            cache_type  = 'public'
        else :
            user = request['AUTHENTICATED_USER']
            cache_type  = 'private'                
        lastModification = self._getLastModification()
        lastModifiedDate = lastModification[0]
        lastUID = lastModification[1]
        
        lastModified = str(lastModifiedDate)
        lastModifiedHeader = str(lastModifiedDate.toZone('GMT').rfc822()).replace('+0000','GMT')
        
        lang = request.LANGUAGE
        etag = '%s-%s-%s-%s' %(user,lang,lastUID,lastModified)
        
        if etag == requestedEtag and not (refreshRequest or forceRefresh) :
            response.setHeader('Etag', etag)
            response.setHeader('Content-Language', lang)
            response.setHeader('Cache-control', 'max-age=%i,s-maxage=%i,%s,%s' %(max_age, max_age, cache_actions, cache_type) )
            response.setHeader('Last-Modified', lastModifiedHeader)
            response.setHeader('Connection', 'close')
            response.setStatus(304)
            return True                
        else :
            response.setHeader('Content-Type', 'text/html;;charset=%s' % charset)
            response.setHeader('Etag', etag)
            response.setHeader('Content-Language', lang)
            response.setHeader('Cache-control', 'max-age=%i,s-maxage=%i,%s,%s' %(max_age, max_age, cache_actions, cache_type) )    
            response.setHeader('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT')
            response.setHeader('Last-Modified', lastModifiedHeader)
            return False            

        

           

