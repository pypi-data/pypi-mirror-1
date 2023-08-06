# Copyright (C) 2009 Mark A. Matienzo
#
# This file is part of the digitalnz Python module.
#
# digitalnz is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# digitalnz is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with digitalnz.  If not, see <http://www.gnu.org/licenses/>.

# request.py - request classes

from urllib import urlencode as uenc
import urllib2
from digitalnz.response import DigitalNZResponse

class DigitalNZAPI(object):
    """DigitalNZAPI: class to perform requests to the APIs"""
    def __init__(self, api_key=None, version=1, format='json', parsing=True):
        if api_key is None:
            raise
        else:
            self.api_key = api_key
        self.base_url = 'http://api.digitalnz.org'
        self.parsing = parsing
        self.version = version
        self.format = format


    def search(self, **kwargs):
        args = kwargs
        req_url = '{0}/records/v{1}.{2}?api_key={3}&{4}'.format(\
            self.base_url,
            self.version,
            self.format,
            self.api_key,
            uenc(kwargs))
        rsp = urllib2.urlopen(req_url).read()
        return DigitalNZResponse(self, rsp)


    def custom_search(self, title=None, **kwargs):
        args = kwargs
        if title is None:
            raise
        req_url = '{0}/custom_searches/v{1}/{2}.{3}?api_key={4}&{5}'.format(\
            self.base_url,
            self.version,
            title,
            self.format,
            self.api_key,
            uenc(kwargs))
        rsp = urllib2.urlopen(req_url).read()
        return DigitalNZResponse(self, rsp)        


    def metadata(self, rec_num=None):
        if rec_num is None:
            raise
        req_url = '{0}/records/v{1}/{2}.{3}?api_key={4}'.format(\
            self.base_url,
            self.version,
            rec_num,
            self.format,
            self.api_key)
        rsp = urllib2.urlopen(req_url).read()
        return DigitalNZResponse(self, rsp)

        
    def partners(self):
        req_url = '{0}/content_partners/v{1}.{2}?api_key={3}'.format(\
            self.base_url,
            self.version,
            self.format,
            self.api_key)
        rsp = urllib2.urlopen(req_url).read()
        return DigitalNZResponse(self, rsp)
