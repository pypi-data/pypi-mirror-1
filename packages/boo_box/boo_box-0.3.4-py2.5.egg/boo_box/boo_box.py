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
    def __init__(self,aff,uid):
        """ You should suply your affiliate and your user id"""
        self.aff = aff
        self.uid = uid

    def _do_get(self,tags):
        import sys
        caller = sys._getframe(1).f_code.co_name
        method = caller.split('_')[-1]
        tags = urllib.quote(tags)
        add = 'http://boo-box.com/api/format:' + method +'/aff:' + self.aff +'/uid:' + self.uid + '/tags:' + tags
        content = urllib.urlopen(add).read()
        return content

    def _do_get_xml(self,tags):
        content = self._do_get(tags)
        return content

    def _do_get_json(self,tags):
        content = self._do_get(tags)
        return content

    def _do_get_object(self,tags):
        content = self._do_get_json(tags)
        content = content.replace('jsonBooboxApi(','')
        import simplejson
        return simplejson.loads(content[:-1])

    def get(self, format, tags):
        """get the response for your tags. Three formats supported by now:
        object, that returns a dict, json, that returns a json string
        and XML, that returns XML"""
        handler = getattr(self, '_do_get_%s' % format.lower(),None)
        if handler:
            return  handler(tags)
        else:
            raise NotImplementedError


