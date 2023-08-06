"""
Copyright (c) 2009 Davide Alberani <da@erlug.linux.it>
              2009 H. Turgut Uyar <uyar@tekir.org>

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

import urllib
from imdbpykit.sitepage import SitePage, CONFIG

class update(SitePage):

    def setup(self):
        request = self.request()
        srequest = request.uri().split('/')
        item_kind = srequest[-3]
        item_id = srequest[-2]
        item_info = urllib.unquote_plus(srequest[-1])
        # Update the item.
        self.data = self.app.update(item_kind, item_id, item_info)
        base_uri = request.uri().split('/update/')[0]
        self.new_uri = '/'.join((base_uri, item_kind, item_id))

    def writeHTML(self):
        # Redirect back to the page we came from.
        self._response.setHeader('Status', '302 Redirect')
        self._response.setHeader('Location', self.new_uri)
