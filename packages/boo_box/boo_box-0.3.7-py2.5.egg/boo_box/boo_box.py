#  Copyright (C) 2008 by Walter Cruz
#  waltercruz@gmail.com
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
#  along with this program; if not, write to the
#  Free Software Foundation, Inc.,
#  59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# Public License can be found at http://www.gnu.org/copyleft/gpl.html

import urllib
import sys

class Box(object):
    def __init__(self, aff, uid):
        """ You should suply your affiliate and your user id"""
        self.limit = 6
        self.aff = aff
        self.uid = uid

    def _do_get(self, tags, limit):
        """
        This will make the real API call
        API format: http://boo-box.com/api/format:formato/aff:ecommid/uid:userid/tags:searchterms/limit:number
        docs: http://www.boo-box.com/blog/br/2009/boo-api-nova-versao/
        """
        import sys
        caller = sys._getframe(1).f_code.co_name
        method = caller.split('_')[-1]
        tags = urllib.quote(tags)
        url_base = 'http://boo-box.com/api/format:%(method)s/aff:%(aff)s/uid:%(uid)s/tags:%(tags)s/limit:%(limit)s'
        url = url_base % {'method':method,'aff':self.aff,'uid':self.uid,'tags':tags,'limit':limit}
        content = urllib.urlopen(url).read()
        return content.strip()

    def _do_get_xml(self,tags,limit):
        content = self._do_get(tags,limit)
        return content

    def _do_get_json(self,tags,limit):
        content = self._do_get(tags,limit)
        return content

    def _do_get_object(self,tags,limit):
        content = self._do_get_json(tags,limit)
        content = content.replace('jsonBooboxApi(','')
        import simplejson
        return simplejson.loads(content[:-2])

    def get(self, format, tags, limit=6):
        """get the response for your tags. Three formats supported by now:
        object, that returns a dict, json, that returns a json string
        and XML, that returns XML"""
        handler = getattr(self, '_do_get_%s' % format.lower(),None)
        if handler:
            return  handler(tags,limit)
        else:
            raise NotImplementedError


