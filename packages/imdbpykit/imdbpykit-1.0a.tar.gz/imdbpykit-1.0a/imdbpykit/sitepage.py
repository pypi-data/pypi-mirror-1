"""
Copyright (c) 2008-2009 H. Turgut Uyar <uyar@tekir.org>
                   2009 Davide Alberani <da@erlug.linux.it>

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

import os

from gettext import gettext as _

from WebKit.Page import Page
from paste.deploy import CONFIG
from paste.url import URL

from imdbpykit.app import App
from imdbpykit.app import BASE_DIR

from xmladapter import get_transform, apply_transform
from xmladapter import fromstring, tostring
from xmladapter import appendchild
from xmladapter import find_all_elements

from imdb.Movie import Movie
from imdb.Person import Person
from imdb.Character import Character
from imdb.Company import Company

__all__ = ['SitePage', 'CONFIG']

class SitePage(Page):
    """Base class for all pages (servlets) in the application."""

    app = App()

    output = CONFIG.get('output')
    pretty_print = (CONFIG.get('pretty_print') == 'on')

    style = CONFIG.get('style')
    template_file = os.path.join(BASE_DIR, 'web', 'static', '%s.xsl' % style)
    transform = get_transform(open(template_file).read())

    i18n = (CONFIG.get('i18n') == 'on')

    INFOSET_MAP = {Movie: app.imdb.get_movie_infoset,
                    Person: app.imdb.get_person_infoset,
                    Character: app.imdb.get_character_infoset,
                    Company: app.imdb.get_company_infoset}


    def title(self):
        return 'IMDbPYKit'

    def awake(self, trans):
        Page.awake(self, trans)
        # Add application-wide setup routines here
        self.setup()

    def setup(self):
        # This method should only be overridden by servlets, not
        # abstract classes (also teardown()).
        pass

    def sleep(self, trans):
        self.teardown()
        Page.sleep(self, trans)

    def teardown(self):
        pass

    def writeHTML(self):
        if self.output == 'html':
            text = self.asXML()
            page = apply_transform(self.transform, text,
                                   pretty_print=self.pretty_print)
            self.writeln(page.encode('utf-8'))
        elif self.output == 'xml':
            self._response.setHeader('Content-type', 'text/xml')
            self.writeXML()
        else:
            raise ValueError("Invalid output value in config file")
        self.app.clearAllCaches()

    def writeXML(self):
        content = self.asXML()
        ##if self.pretty_print and 0:
        if self.pretty_print:
            content = tostring(fromstring(content), pretty_print=True)
        page = u'<?xml version="1.0" ?>\n'
        page += u'<?xml-stylesheet type="text/xsl" href="/static/%s.xsl" ?>\n' \
             % self.style
        page += content
        self.writeln(page.encode('utf-8'))

    def preAction(self, action):
        self.setView('writeContent')

    def postAction(self, action):
        if self.view() is not None:
            self.writeHTML()

    def clear(self):
        self.app.clearAllCaches(True)

    def asXML(self):
        ##return self.data.asXML()
        root = fromstring(self.data.asXML())

        # Collect a list of information available but not yet fetched.
        available_infoset = self.INFOSET_MAP.get(self.data.__class__)
        if available_infoset:
            available_infoset = available_infoset()
        retrieved_infoset = self.data.current_info
        left_out_infoset = [k for k in available_infoset
                            if k not in retrieved_infoset]

        # Append left-out-infoset information.
        if left_out_infoset:
            # Catch-all special key.
            left_out_infoset.append('all')
            infoSection = appendchild(root, 'left-out-infoset')
            for infoset in left_out_infoset:
                infoNode = appendchild(infoSection, 'infoset')
                infoNode.set('info', infoset)
                # XX: more introspection than I like...
                infoNode.set('kind', self.__class__.__name__)
                infoNode.set('id', unicode(self.data.getID()))
        if self.i18n:
            self.setTitles(root)
        return tostring(root)

    def setTitles(self, root):
        for element in find_all_elements(root):
            title = element.get('title') or ''
            if not title:
                translated = _(element.tag).decode('utf-8')
                if translated != element.tag:
                    element.set('title', translated)
