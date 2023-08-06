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

"""

A Python library to ease the publication of REST-style web services in Django applications, specially (but not exclusively) those using the Django Model framework.

Acknowledgement
===============

@summary: Python interface to SPARQL services FIXME
@authors: U{Diego Berrueta<http://berrueta.net>, Jana Álvarez, U{Sergio Fernández<http://www.wikier.org>}, U{Carlos Tejo Alonso<http://dayures.net>}
@organization: U{Foundation CTIC<http://www.fundacionctic.org/>}.
@license: U{GNU Lesser General Public License (LGPL), Version 3<href="http://www.gnu.org/licenses/lgpl-3.0.html">}
@requires: U{simplejson<http://cheeseshop.python.org/pypi/simplejson>} package.
@requires: U{mimeparse<http://code.google.com/p/mimeparse/>} package.
"""

__version__ = "0.1.0"
__authors__  = u"Diego Berrueta, Jana Álvarez, Sergio Fernández, Carlos Tejo Alonso"
__license__ = u"GNU Lesser General Public License (LGPL), Version 3"
__contact__ = "rest-in-py-devel@lists.sourceforge.net"
__date__    = "2009-03-26"
__agent__   = "RESTinpy %s (http://rest-in-py.sourceforge.net/)" % __version__

import sys
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(pathname)s:%(lineno)s %(levelname)s: %(message)s", stream=sys.stdout)

logging.info("Logger configured for RESTinpy")
