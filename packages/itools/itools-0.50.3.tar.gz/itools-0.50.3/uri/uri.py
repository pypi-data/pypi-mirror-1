# -*- coding: UTF-8 -*-
# Copyright (C) 2005-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2006 Nicolas Deram <nicolas@itaapy.com>
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

# Import from the Standard Library
from os import getcwd
from os.path import sep

# Import from itools
from generic import Path, Reference, GenericDataType
from registry import get_scheme



def get_reference(reference):
    """Returns a URI reference of the good type from the given string.
    """
    if ':' in reference:
        scheme_name, scheme_specifics = reference.split(':', 1)
        scheme = get_scheme(scheme_name)
    else:
        scheme = GenericDataType
    return scheme.decode(reference)



def get_cwd():
    """Returns the current working directory as a URI object.
    """
    # Get the base path
    base = getcwd()
    # Make it working with Windows
    if sep == '\\':
        # Internally we use always the "/"
        base = base.replace(sep, '/')

    return GenericDataType.decode('file://%s/' % base)



def get_absolute_reference(reference, base=None):
    """Returns the absolute URI for the given reference. Uses "base" to
    resolve the reference, if "base" is not given default to the current
    working directory.
    """
    # Check the reference is of the good type
    if not isinstance(reference, Reference):
        reference = get_reference(reference)
    # Check the reference is absolute
    if reference.scheme:
        return reference
    # Default to the current working directory
    if base is None:
        base = get_cwd()
    return base.resolve(reference)



def get_absolute_reference2(reference, base=None):
    """Like "get_absolute_reference", but uses the "resolve2" algorithm
    (ignores trailing slashes).
    """
    # Check the reference is of the good type
    if not isinstance(reference, Reference):
        reference = get_reference(reference)
    # Check the reference is absolute
    if reference.scheme:
        return reference
    # Default to the current working directory
    if base is None:
        base = get_cwd()
    return base.resolve2(reference)

