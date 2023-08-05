# Copyright (c) 2005-2007
# Authors: KissBooth contributors (See CREDITS.txt)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#

from kss.core import KSSView, force_unicode, kssaction
from kss.core.parsers import HtmlParser

#from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.PythonScripts.standard import url_quote_plus

from cgi import escape

class LiveSearchView(KSSView):
    
    results = ()
    showMore = False
    emptyResult = True

    @kssaction
    def __call__(self, q, limit=10):
        limit = int(limit)
        self.update(q, limit=limit)
        if not self.results and not self.emptyResult:
            # if we do not want an empty result set at all...
            return self.render()
        html = self.renderHtml()
         ## if we have the next line, force_unicode is included
        # XXX now, the cgi.escape is inserting &quot; that we need to get rid of
        # so this is the main reason for using the parser now.
        html0 = html
        html = HtmlParser(html)()
        html = html.encode('ascii', 'xmlcharrefreplace')
        self.getCommandSet('core').continueEvent('insert', html=html)

    def update(self, q, limit=10):
        context = self.context
        
        # XXX this is only necessary because the brokenness of translation
        # via CMFPlone.i18nl10n's utranslate method. By setting the response 
        # headers we force translation services to return utf, which then we 
        # convert to unicode.
        # (btw, the translation should return unicode already, thus its brokenness.)
        #self.request.response.setHeader('Content-Type', 'text/xml;charset=%s' % context.plone_utils.getSiteEncoding())
        self.request.response.setHeader('Content-Type', 'text/xml;charset=utf-8')

        ploneUtils = getToolByName(context, 'plone_utils')

        # generate a result set for the query
        catalog = context.portal_catalog

        friendly_types = ploneUtils.getUserFriendlyTypes()

        def quotestring(s):
            return '"%s"' % s

        def quote_bad_chars(s):
            bad_chars = ["(", ")"]
            for char in bad_chars:
                s = s.replace(char, quotestring(char))
            return s

        # for now we just do a full search to prove a point, this is not the
        # way to do this in the future, we'd use a in-memory probability based
        # result set.
        # convert queries to zctextindex

        # XXX really if it contains + * ? or -
        # it will not be right since the catalog ignores all non-word
        # characters equally like
        # so we don't even attept to make that right.
        # But we strip these and these so that the catalog does
        # not interpret them as metachars
        ##q = re.compile(r'[\*\?\-\+]+').sub(' ', q)
        for char in '?-+*':
            q = q.replace(char, ' ')
        r=q.split()
        r = " AND ".join(r)
        r = quote_bad_chars(r)+'*'
        self.searchterms = url_quote_plus(r)

        results = catalog(SearchableText=r, portal_type=friendly_types)
        self.results = results[:limit]
        self.showMore = len(results) >= limit

    def renderHtml(self):
        context = self.context

        ploneUtils = getToolByName(context, 'plone_utils')
        pretty_title_or_id = ploneUtils.pretty_title_or_id

        portalProperties = getToolByName(context, 'portal_properties')
        siteProperties = getattr(portalProperties, 'site_properties', None)
        useViewAction = []
        if siteProperties is not None:
            useViewAction = siteProperties.getProperty('typesUseViewActionInListings', [])

        # SIMPLE CONFIGURATION
        ##USE_ICON = True
        ##USE_RANKING = False
        MAX_TITLE = 29
        MAX_DESCRIPTION = 93


        # replace named entities with their numbered counterparts, in the xml the named ones are not correct
        #   &darr;      --> &#8595;
        #   &hellip;    --> &#8230;
        legend_livesearch = _('legend_livesearch', default='LiveSearch &#8595;')
        label_no_results_found = _('label_no_results_found', default='No matching results found.')
        label_advanced_search = _('label_advanced_search', default='Advanced Search&#8230;')
        label_show_all = _('label_show_all', default='Show all&#8230;')

        ts = getToolByName(context, 'translation_service')

        b = []
        def b_append(txt):
            b.append(force_unicode(txt, 'utf'))

        b_append('<div id="LSResult" class="LSResult">')
        b_append('<div id="LSShadow" class="LSShadow">')

        if not self.results:
            b_append( '''<fieldset class="livesearchContainer">''')
            b_append( '''<legend id="livesearchLegend">%s</legend>''' % ts.translate(legend_livesearch))
            b_append( '''<div class="LSIEFix">''')
            b_append( '''<div id="LSNothingFound">%s</div>''' % ts.translate(label_no_results_found))
            b_append( '''<div class="LSRow">''')
            b_append( '<a href="search_form" style="font-weight:normal">%s</a>' % ts.translate(label_advanced_search))
            b_append( '''</div>''')
            b_append( '''</div>''')
            b_append( '''</fieldset>''')

        else:
            b_append( '''<fieldset class="livesearchContainer">''')
            b_append( '''<legend id="livesearchLegend">%s</legend>''' % ts.translate(legend_livesearch))
            b_append( '''<div class="LSIEFix">''')
            b_append( '''<ul class="LSTable">''')
            for result in self.results:

                itemUrl = result.getURL()
                if result.portal_type in useViewAction:
                    itemUrl += '/view'

                b_append( '''<li class="LSRow">''',)
                b_append( '''<img src="%s"/>''' % result.getIcon,)
                full_title = pretty_title_or_id(result)
                if len(full_title) >= MAX_TITLE:
                    display_title = ''.join((full_title[:MAX_TITLE],'...'))
                else:
                    display_title = full_title
                b_append( '''<a href="%s" title="%s">%s</a>''' % (itemUrl,
                        escape(full_title, True), escape(display_title, True)))
                b_append( '''<span class="discreet">[%s%%]</span>''' % result.data_record_normalized_score_)
                display_description = result.Description
                if len(display_description) >= MAX_DESCRIPTION:
                    display_description = ''.join((display_description[:MAX_DESCRIPTION],'...'))
                b_append( '''<div class="discreet" style="margin-left: 2.5em;">%s</div>''' % (display_description))
                b_append( '''</li>''')
                full_title, display_title, display_description = None, None, None

            b_append( '''<li class="LSRow">''')
            b_append( '<a href="search_form" style="font-weight:normal">%s</a>' % ts.translate(label_advanced_search))
            b_append( '''</li>''')

            if self.showMore:
                # add a more... row
                b_append( '''<li class="LSRow">''')
                b_append( '<a href="%s" style="font-weight:normal">%s</a>' % ('search?SearchableText=' + self.searchterms, ts.translate(label_show_all)))
                b_append( '''</li>''')
            b_append( '''</ul>''')
            b_append( '''</div>''')
            b_append( '''</fieldset>''')

        b_append('</div>')
        b_append('</div>')

        html = u''.join(b)
        return html 
