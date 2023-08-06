"""
Copyright (c) 2008-2009 H. Turgut Uyar <uyar@tekir.org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

from imdbpykit.sitepage import SitePage, CONFIG
from imdbpykit.xmladapter import fromstring, tostring
from imdbpykit.xmladapter import appendchild


class search(SitePage):

    attrmap = {
        'title':     ('title',     'movieID',     'long imdb title'),
        'episode':   ('title',     'movieID',     'long imdb title'),
        'people':    ('name',      'personID',    'long imdb name'),
        'character': ('character', 'characterID', 'long imdb name'),
        'company':   ('company',   'companyID',   'long imdb name'),
        # 'keyword' shows results for keywords similar to the given one.
        'keyword':   ('keyword', None, None),
        # 'getkeyword' shows a list of movies with the given keyword.
        'getkeyword':   ('title', 'movieID', 'long imdb title'),
        'topbottom':   ('title', 'movieID', 'long imdb title')
        }

    def setup(self):
        request = self.request()
        self.kind = request.field('kind')
        self.query = request.field('q')

        self.query = self.query.decode('utf8')

        self.page_title = u'Search %s' % self.query

        if self.kind == 'title':
            self.items = self.app.search_movie(self.query)
        elif self.kind == 'episode':
            self.items = self.app.search_episode(self.query)
        elif self.kind == 'people':
            self.items = self.app.search_person(self.query)
        elif self.kind == 'character':
            self.items = self.app.search_character(self.query)
        elif self.kind == 'company':
            self.items = self.app.search_company(self.query)
        elif self.kind == 'keyword':
            self.items = self.app.search_keyword(self.query)
        elif self.kind == 'getkeyword':
            self.items = self.app.get_keyword(self.query)
        elif self.kind == 'topbottom':
            if self.query == 'top250':
                self.items = self.app.get_top250()
            elif self.query == 'bottom100':
                self.items = self.app.get_bottom100()

        self.item_kind, self.item_id, self.item_title = self.attrmap[self.kind]

    def asXML(self):
        root = fromstring('<search />')
        child = appendchild(root, 'query', text=self.query)
        child = appendchild(root, 'kind', text=self.kind)

        result = appendchild(root, 'result')
        for item in self.items:
            if self.item_title is not None:
                text = item.get(self.item_title)
            else:
                text = item
            child = appendchild(result, 'item', text=text)
            child.set('kind', self.item_kind)
            if self.item_id is not None:
                value = getattr(item, self.item_id)
            else:
                value = item
            child.set('id', unicode(value))
        return tostring(root)

