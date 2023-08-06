# -*- coding: UTF-8 -*-
# Copyright (C) 2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from itools
from base import CatalogAware
from catalog import Catalog, make_catalog
from exceptions import XapianIndexError
from fields import BaseField, register_field, get_field
from fields import BoolField, KeywordField, IntegerField, TextField
from queries import RangeQuery, PhraseQuery, AndQuery, OrQuery
from queries import AllQuery, NotQuery, StartQuery


__all__ = [
    'make_catalog',
    'Catalog',
    'CatalogAware',
    # Exceptions
    'XapianIndexError',
    # Fields
    'BaseField',
    'TextField',
    'KeywordField',
    'IntegerField',
    'BoolField',
    'register_field',
    'get_field',
    # Queries
    'RangeQuery',
    'PhraseQuery',
    'AndQuery',
    'OrQuery',
    'AllQuery',
    'NotQuery',
    'StartQuery']

