# -*- coding: utf-8 -*-
# Copyright Fundacion CTIC, 2009 http://www.fundacionctic.org/
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

#https://mdp.cti.depaul.edu/web2py_wiki/default/wiki/JSONdatetime

import re
import simplejson
from datetime import datetime, date

__jsdateregexp__ = re.compile(r'"\*\*(new Date\([0-9,]+\))"')

class __JSONDateEncoder__(simplejson.JSONEncoder):
    def default(self, obj):
        if (isinstance(obj, datetime) or isinstance(obj, date)):
            return obj.isoformat()
        return simplejson.JSONEncoder.default(self, obj)

def dumps(obj, ensure_ascii=True):
    """ A (simple)json wrapper that can wrap up python datetime and date
    objects into Javascript date objects.
    @param obj: the python object (possibly containing dates or datetimes) for
        (simple)json to serialize into JSON
    @param ensure_ascii: If ensure_ascii is false (default: True), then some 
        chunks written to fp may be unicode instances, subject to normal Python 
        str to unicode coercion rules.

    @returns: JSON version of the passed object
    """
    return __jsdateregexp__.sub(r'\1', simplejson.dumps(obj, ensure_ascii=ensure_ascii, cls=__JSONDateEncoder__))
