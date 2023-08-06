# Copyright (C) 2009-2010 Mark A. Matienzo
#
# This file is part of iii, the Python Innovative Interfaces utility module.
#
# iii is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# iii is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with iii.  If not, see <http://www.gnu.org/licenses/>.

# webpac.py - WebPAC-related functions (for record checking/retrieval, etc.)

from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup as BS

from iii.exceptions import RecordDoesNotExistError, \
    InvalidWebPACInstanceError
    
class WebPACReader(object):
    """iii.record.WebPACReader: A class to interact with WebPAC instances"""
    
    def __init__(self, webpac_url=None, quiet=True):
        if webpac_url is None:
            raise InvalidWebPACInstanceError
        else:
            self.webpac_url = webpac_url
            self.quiet = quiet
    
    def record_exists(self, bnumber):
        recordreq = urlopen(self.webpac_url + '/record=' + bnumber)
        recordsoup = BS(recordreq.read())
        if recordsoup.h2.string == 'No Such Record':
            if self.quiet is True:
                return False
            else:
                raise RecordDoesNotExistError
        else:
            return True

    def record_get_marc(self, bnumber):
        if self.record_exists(bnumber):
            recordreq = urlopen(self.webpac_url + '/search/.' + bnumber + \
            '/.' + bnumber + '/1,1,1,B/detlmarc~' + bnumber)
            recordsoup = BS(recordreq.read())
            return recordsoup.pre.string
