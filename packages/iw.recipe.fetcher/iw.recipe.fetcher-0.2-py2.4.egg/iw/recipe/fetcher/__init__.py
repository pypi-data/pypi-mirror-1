# -*- coding: utf-8 -*-
# Copyright (C)2007 'Ingeniweb'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""Recipe fetcher"""
import os
import socket
import urlparse
import urllib2


class Recipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.urls = options.get('urls', '').split('\n')

        base_url = options.get('base_url', '')
        files = options.get('files', '').split('\n')
        if base_url and files:
            self.urls.extend(['%s/%s' % (base_url, f.strip()) for f in files if f])

        find_links = options.get('find-links', '').split('\n')
        self.find_links = [l.strip() for l in find_links if l.strip()]

        self.offline = buildout['buildout'].get('offline', 'false')
        self.location = os.path.join(buildout['buildout']['directory'], name)
        if self.offline.strip() != 'true':
            self.offline = False
        self.install_from_cache = buildout['buildout'].get('install-from-cache', 'false')
        if self.install_from_cache.strip() != 'true':
            self.install_from_cache = False

    def install(self):
        """installer"""
        if self.install_from_cache or self.offline:
            return
        if not os.path.isdir(self.location):
            os.mkdir(self.location)
        for url in self.urls:
            parsed = urlparse.urlparse(url)
            scheme = parsed[0]
            filename = url.split('/')[-1]
            if scheme in ('http', 'https'):
                path = os.path.join(self.location, filename)
                if not os.path.isfile(path):
                    data = None
                    req = urllib2.Request(url=url)
                    try:
                        resp = urllib2.urlopen(req)
                        data = resp.read()
                    except (urllib2.URLError, socket.error):
                        for link in self.find_links:
                            if not link.endswith('/'):
                                link += '/'
                            req = urllib2.Request(url=link+filename)
                            try:
                                resp = urllib2.urlopen(req)
                                data = resp.read()
                            except (urllib2.URLError, socket.error):
                                pass
                            else:
                                break
                    if not data:
                        raise RuntimeError("Can't retrieve url %s" % url)
                    fd = open(path, 'wb')
                    fd.write(data)
                    fd.close()
        return tuple()

    update = install
