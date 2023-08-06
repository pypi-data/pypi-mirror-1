# -*- coding: utf-8 -*-
# Copyright 2009 Martin Borho <martin@borho.net>
# GPL - see License.txt for details
from urllib import quote_plus
from baas.core.yqlapi import YQLApi
from baas.core.plugins import Plugin
from baas.core.helpers import strip_tags, xmlify, htmlentities_decode

class Yql (Plugin):

    def get_map(self):
        """
            returns the command map for the plugin
        """
        cmd_map = [('news',self.search_news), ('web', self.search_web), ('blip',self.search_blip)]
        return cmd_map

    def get_help(self):
        """
            returns the help text for the plugin
        """
        additional = '''Some commands (news,web) can be combined with lang-codes, like #de, #en, #es etc:
news:hamburg #de
web:xmpp #de'''

        return {
            'commands': ['news:word - searches for news','web:word - websearch','blip:song - search for songs on blip.fm'],
            'additional': [additional],
        }

    def _extract_hits(self, result):
        hits = result.get('result') if result else None
    
        # handle single result
        if type(hits) == dict:
            hits = [hits]
        return hits
         
    def search_web(self, term):
        '''
        searches web by yahoo
        '''
        term = term.strip()
        lang = None

        if term and term.find('#')+1:
            term, lang = term.split('#',1)
            term = term.strip()

        if term == '':
            return "Please specify your search term"

        query = 'select title,url,date '
        query += 'from search.web where query="%s" ' % term

        if lang:
            query += ' AND region="%s" AND lang="%s" ' % (lang, lang)

        yql_api = YQLApi()
        response = yql_api.request(query=query)
        hits = self._extract_hits(response)
        
        title = 'Searching the web for %s\n' % term
        return self.render(data=hits, title=title)

    def search_news(self, term):
        '''
        searches news
        '''
        term = term.strip()
        lang = None

        if term and term.find('#')+1:
            term, lang = term.split('#',1)
            term = term.strip()

        if term == '':
            return "Please specify your search term"

        query = 'select title,url,date '
        query += 'from search.news where query="%s" ' % term

        if lang:
            query += ' AND region="%s" AND lang="%s" ' % (lang, lang)

        query += '| sort(field="age")'

        yql_api = YQLApi()
        response = yql_api.request(query=query)        
        hits = self._extract_hits(response)
                
        title = 'Searching news for %s\n' % term
        return self.render(data=hits, title=title)
        

    def search_blip(self, term):
        '''
        searches for blips on blip.fm
        '''
        term = term.strip()

        if term == '':
            return "Please specify your search term"

        yterm = 'intitle:"%s" site:blip.fm inurl:profile -intitle:"Props given" -intitle:"Favourite DJs" \
                -intitle:"Blip.fm %s"' % (term, term)

        query = 'select title,url from search.web(0,15) '
        query += "WHERE query = '%s'" % yterm

        yql_api = YQLApi()
        response = yql_api.request(query=query)
        hits = self._extract_hits(response)
        
        return self.render(data=hits, title='Blips for %s' % term, extra_format='blip')
        
    def render_xmpp(self, hits, title):
        '''
        renders the result for xmpp responses
        '''
        result = title+"\n"
        if hits:
            for row in hits:
                result += "(%s) %s : %s\n" % (row['date'],row['title'],row['url'])
        else:
            result += 'No hits found!'
        return strip_tags(result)

    def render_wave(self, hits, title):
        '''
        renders the result for wave responses
        '''
        result = " <br/><br/><b>%s</b><br/>" % xmlify(title)
        if hits:
            for row in hits:
                title = xmlify(row['title'])
                result += '<a href="%s">%s</a><br/><br/>' % (xmlify(row['url']), title)
        else:
            result += 'No hits found!'
        return result

    def render_xmpp_blip(self, hits, title):
        '''
        renders blip search result for xmpp responses
        '''
        result = title+"\n"
        if hits:
            for row in hits:
                result += "%s : %s\n" % (row['title'].replace('Blip.fm | ',''),row['url'])
        else:
            result +='No blips found!'
        return strip_tags(result)

    def render_wave_blip(self, hits, title):
        '''
        renders blip search result for wave responses
        '''
        result = " <br/><br/><b>%s</b><br/>" % xmlify(title)
        if hits:
            for row in hits:
                title = xmlify(row['title'])
                result += '<a href="%s">%s</a><br/>' % (xmlify(row['url']), title)
        else:
            result +='No blips found!'
        return result