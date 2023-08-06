"""
Copyright (c) 2008-2009 H. Turgut Uyar <uyar@tekir.org>
              2005-2008 Davide Alberani <da@erlug.linux.it>
                   2006 Martin Kirst <martin.kirst@s1998.tu-chemnitz.de>

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
import glob
import urllib2
import gettext
import msgfmt

import imdb
from imdb import helpers

import time
from threading import RLock
from paste.deploy import CONFIG

BASE_DIR = os.path.dirname(__file__)
CACHE_DIR = os.path.join(BASE_DIR, 'web', 'static', 'cache')
LOCALE_DIR = os.path.join(BASE_DIR, 'locale')


def _imageurl_to_filename(url):
    basename = url.split('/images/')[-1].replace('/', '_')
    return os.path.join(CACHE_DIR, basename)


class Cache(dict):
    """Dictionary used to cache object for a specified amount of time."""

    def __init__(self, maxtime=3600):
        dict.__init__(self)
        self._lock = RLock()
        self.maxtime = maxtime

    def __getitem__(self, key, update=True):
        value, ttime = dict.__getitem__(self, key) or (None, None)
        if value is not None and update:
            self.__setitem__(key, value) # to update the time.
        return value

    def get(self, key, default=None, update=True):
        try: value = self.__getitem__(key, update)
        except KeyError: value = default
        return value

    def __setitem__(self, key, value):
        self._lock.acquire()
        try:
            ttime = time.time()
            dict.__setitem__(self, key, (value, ttime))
        finally:
            self._lock.release()

    def clearCache(self, force=False):
        ctime = time.time()
        for key, (value, ttime) in dict.items(self):
            if force or (ctime - ttime > self.maxtime):
                self._lock.acquire()
                try:
                    del self[key]
                finally:
                    self._lock.release()
        if force:
            if os.path.exists(CACHE_DIR):
                for filename in glob.glob(CACHE_DIR + "/*"):
                    os.unlink(filename)

class App(object):

    # Function used to modify references inside text values.
    xmlModFunct = helpers.makeModCGILinks(
        movieTxt='<movie id="%(movieID)s"><title>%(title)s</title></movie>',
        personTxt='<person id="%(personID)s"><name>%(name)s</name></person>',
        characterTxt='<character id="%(characterID)s"><name>%(name)s</name></character>')

    imdb = imdb.IMDb(defaultModFunct=xmlModFunct)

    maxtime = int(CONFIG.get('maxtime'))

    moviesCache = Cache(maxtime=maxtime)
    peopleCache = Cache(maxtime=maxtime)
    charactersCache = Cache(maxtime=maxtime)
    companiesCache = Cache(maxtime=maxtime)

    searchMoviesCache = Cache(maxtime=maxtime)
    searchEpisodesCache = Cache(maxtime=maxtime)
    searchPeopleCache = Cache(maxtime=maxtime)
    searchCharactersCache = Cache(maxtime=maxtime)
    searchCompaniesCache = Cache(maxtime=maxtime)

    def __init__(self):
        lang_glob = '%s%simdbpykit-*.po' % (LOCALE_DIR, os.path.sep)
        for input_file in glob.glob(lang_glob):
            lang = input_file[len(LOCALE_DIR)+len(os.path.sep)+10:-3]
            lang_dir = os.path.join(LOCALE_DIR, lang)
            if not os.path.exists(lang_dir):
                os.mkdir(lang_dir)
            lang_dir = os.path.join(lang_dir, 'LC_MESSAGES')
            if not os.path.exists(lang_dir):
                os.mkdir(lang_dir)
            output_file = os.path.join(lang_dir, 'imdbpykit.mo')
            msgfmt.make(input_file, output_file)
        gettext.bindtextdomain('imdbpykit', LOCALE_DIR)
        gettext.textdomain('imdbpykit')

    def clearAllCaches(self, force=False):
        for cache in (self.moviesCache, self.searchMoviesCache,
                      self.peopleCache, self.searchPeopleCache,
                      self.charactersCache, self.searchCharactersCache,
                      self.companiesCache, self.searchCompaniesCache):
            cache.clearCache(force)

    def get_image(self, ob, key):
        url = ob.get(key) or ''
        if url:
            filename = _imageurl_to_filename(url)
            if not os.path.exists(CACHE_DIR):
                os.mkdir(CACHE_DIR)
            if not os.path.exists(filename):
                data = urllib2.urlopen(url).read()
                image_file = open(filename, 'w')
                image_file.write(data)
                image_file.close()

    def get_movie(self, movieID):
        """Return a movie object, retrieving it if not already in the cache."""
        if movieID in self.moviesCache:
            movie = self.moviesCache[movieID]
        else:
            movie = self.imdb.get_movie(movieID)
            self.moviesCache[movieID] = movie
        self.get_image(movie, 'cover url')
        return movie

    def get_person(self, personID):
        """Return a person object, retrieving it if not already in the cache."""
        if personID in self.peopleCache:
            person = self.peopleCache[personID]
        else:
            person = self.imdb.get_person(personID)
            self.peopleCache[personID] = person
        self.get_image(person, 'headshot')
        return person

    def get_character(self, characterID):
        """Return a character object, retrieving it if not in the cache."""
        if characterID in self.charactersCache:
            character = self.charactersCache[characterID]
        else:
            character = self.imdb.get_character(characterID)
            self.charactersCache[characterID] = character
        self.get_image(character, 'headshot')
        return character

    def get_company(self, companyID):
        """Return a company object, retrieving it if not in the cache."""
        if companyID in self.companiesCache:
            company = self.companiesCache[companyID]
        else:
            company = self.imdb.get_company(companyID)
            self.companiesCache[companyID] = company
        return company

    def search_movie(self, query):
        """Return a movie search query result object, retrieving it if not
        already in the cache."""
        if query in self.searchMoviesCache:
            result = self.searchMoviesCache[query]
        else:
            result = self.imdb.search_movie(query)
            self.searchMoviesCache[query] = result
        return result

    def search_episode(self, query):
        """Return a episode search query result object, retrieving it if not
        already in the cache."""
        if query in self.searchEpisodesCache:
            result = self.searchEpisodesCache[query]
        else:
            result = self.imdb.search_episode(query)
            self.searchEpisodesCache[query] = result
        return result

    def search_person(self, query):
        """Return a person search query result object, retrieving it if not
        already in the cache."""
        if query in self.searchPeopleCache:
            result = self.searchPeopleCache[query]
        else:
            result = self.imdb.search_person(query)
            self.searchPeopleCache[query] = result
        return result

    def search_character(self, query):
        """Return a character search query result object, retrieving it if not
        already in the cache."""
        if query in self.searchCharactersCache:
            result = self.searchCharactersCache[query]
        else:
            result = self.imdb.search_character(query)
            self.searchCharactersCache[query] = result
        return result

    def search_company(self, query):
        """Return a company search query result object, retrieving it if not
        already in the cache."""
        if query in self.searchCompaniesCache:
            result = self.searchCompaniesCache[query]
        else:
            result = self.imdb.search_company(query)
            self.searchCompaniesCache[query] = result
        return result

    def update(self, item_kind, item_id, item_info):
        """Update an object (taken from the cache or newly fetched)."""
        if item_kind == 'title':
            item = self.get_movie(item_id)
        elif item_kind == 'name':
            item = self.get_person(item_id)
        elif item_kind == 'character':
            item = self.get_character(item_id)
        elif item_kind == 'company':
            item = self.get_company(item_id)
        else:
            return
        self.imdb.update(item, item_info)
        return item

