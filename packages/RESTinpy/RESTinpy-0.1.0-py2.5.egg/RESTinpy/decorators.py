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


def rename_param(source, target):
    def decorator(fn):
        def wrapper(*args, **kw_args):
            new_kw_args = dict(kw_args)
            new_kw_args[target] = new_kw_args[source]
            del new_kw_args[source]
            return fn(*args, **new_kw_args)
        return wrapper
    return decorator

def drop_param(*param_names):
    def decorator(fn):
        def wrapper(*args, **kw_args):
            new_kw_args = dict(kw_args)
            for p in param_names:
                del new_kw_args[p]
            return fn(*args, **new_kw_args)
        return wrapper
    return decorator