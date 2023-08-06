# -*- coding: utf-8 -*-
#
# File: wikipediamashup.py
#
# Copyright (c) Matias Bordese
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

__author__ = 'Matias Bordese <mbordese@gmail.com>'
__docformat__ = 'plaintext'

import urllib2
from BeautifulSoup import BeautifulSoup, Tag

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from kupu.mashups.config import WIKIPEDIA_URL

class WikipediaView(BrowserView):
    """View for wikipedia excerpts"""

    template = ViewPageTemplateFile('templates/wikiarticle.pt')

    def __call__(self, title=None):
        context = self.context
        self.article_content = ''
        if title:
            try:
                article = self._getWikiArticle(title)
                self.article_title = self._extractTitle(article)
                self.article_content = self._extractExcerpt(article)
            except:
                self.article_title = ''
                self.article_content = ''
        return self.template()

    def getFullArticleUrl(self):
        """Return the url to the current article"""
        url = self._getArticleUrl(self.article_title)
        return url

    def _getArticleUrl(self, title):
        """Return the url to the article given the title"""
        title = title.replace(' ', '_')
        url = WIKIPEDIA_URL + "/w/index.php?title=%s" % title
        return url

    def _getWikiArticle(self, title):
        """Return the BeautifulSoup of the article with the given title"""
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        url = self._getArticleUrl(title)
        infile = opener.open(url)
        page = infile.read()
        return BeautifulSoup(page)

    def _extractTitle(self, bsoup):
        """Return the title of the current article"""
        content = bsoup.find('div', id='content')
        title = content.find('h1', id='firstHeading')
        return title.renderContents()

    def _extractExcerpt(self, bsoup):
        """Return the introduction section of the current article"""
        ret = ''
        content = bsoup.find('div', id='content')
        body = content.find('div', id='bodyContent')
        current = body.next
        while current:
            # If it is the table of contents, break
            if isinstance(current, Tag) and current.name == 'table' and current.get('id') == 'toc':
                break
            if isinstance(current, Tag) and current.name in ['p', 'ul']:
                # If it is an intermediate title, break
                if len(current) == 1 and isinstance(current.next, Tag) and \
                   current.next.name == 'a' and current.next.get('name') != None:
                    break
                # Update links inside the tag
                links = current.findAll('a')
                for l in links:
                    l['href'] = WIKIPEDIA_URL + l['href']
                    l['class'] = 'link-plain'
                ret += str(current)
            current = current.nextSibling
        return ret
