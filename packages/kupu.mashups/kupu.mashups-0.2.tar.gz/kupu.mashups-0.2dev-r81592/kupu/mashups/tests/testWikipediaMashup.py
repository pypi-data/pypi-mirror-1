# -*- coding: utf-8 -*-
#
# File: testWikipediaMashup.py
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

import unittest
from base import MashupsTestCase

from kupu.mashups.browser.wikipediamashup import WikipediaView, WIKIPEDIA_URL

from Products.CMFCore.utils import getToolByName

class TestWikipediaView(MashupsTestCase):
    """Test the wikipedia article mashup view
    """

    def afterSetUp(self):
        self.wv = WikipediaView(self.portal, None)
        self.article = self.wv._getWikiArticle('albert einstein')

    def testGetUrlFromTitle(self):
        url = self.wv._getArticleUrl('soccer')
        url2 = self.wv._getArticleUrl('albert einstein')
        self.assertEquals(url, WIKIPEDIA_URL + "/w/index.php?title=soccer")
        self.assertEquals(url2, WIKIPEDIA_URL + "/w/index.php?title=albert_einstein")

    def testGetArticleFromTitle(self):
        self.assert_(self.article is not None)

    def testGetTitleFromArticle(self):
        title = self.wv._extractTitle(self.article)
        self.assertEquals(title, 'Albert Einstein')

    def testExtractExcerpt(self):
        excerpt = self.wv._extractExcerpt(self.article)
        self.assert_('Youth and schooling' not in excerpt)
        self.assert_('<table>' not in excerpt)
        self.assert_(excerpt.count('Einstein') > 0 and \
                     excerpt.count('relativity') > 0 and \
                     excerpt.count('physics') > 0)


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestWikipediaView))
    return suite
