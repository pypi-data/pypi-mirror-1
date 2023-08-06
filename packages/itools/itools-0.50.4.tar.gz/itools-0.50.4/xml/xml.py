# -*- coding: UTF-8 -*-
# Copyright (C) 2003-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2007-2008 Sylvain Taverne <sylvain@itaapy.com>
# Copyright (C) 2008 David Versmisse <david.versmisse@itaapy.com>
# Copyright (C) 2008 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2008 Matthieu France <matthieu@itaapy.com>
# Copyright (C) 2008 Wynand Winterbach <wynand.winterbach@gmail.com>
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
from itools.datatypes import XMLAttribute, XMLContent
from itools.handlers import TextFile, register_handler_class
from namespaces import get_namespace, is_empty
from parser import (XMLParser, XML_DECL, DOCUMENT_TYPE, START_ELEMENT,
                    END_ELEMENT, TEXT, COMMENT, CDATA)


#############################################################################
# Data types
#############################################################################

# Serialize
def get_qname(ns_uri, name):
    """Returns the fully qualified name"""
    if ns_uri is None:
        return name
    prefix = get_namespace(ns_uri).prefix
    if prefix is None:
        return name
    return '%s:%s' % (prefix, name)


def get_attribute_qname(namespace, local_name):
    """Returns the fully qualified name"""
    if namespace is None:
        return local_name

    prefix = get_namespace(namespace).prefix
    if prefix is None:
        return local_name

    # Namespace declarations for the default namespace lack the local
    # name (e.g. xmlns="http://www.example.org"). Here 'xmlns' is always
    # the prefix, and there is not a local name. This an special case.
    if local_name is None:
        return prefix

    return '%s:%s' % (prefix, local_name)


def get_start_tag(tag_uri, tag_name, attributes):
    s = '<%s' % get_qname(tag_uri, tag_name)
    # Output the attributes
    for attr_uri, attr_name in attributes:
        value = attributes[(attr_uri, attr_name)]
        qname = get_attribute_qname(attr_uri, attr_name)
        value = XMLAttribute.encode(value)
        s += ' %s="%s"' % (qname, value)
    # Close the start tag
    if is_empty(tag_uri, tag_name):
        return s + '/>'
    else:
        return s + '>'


def get_end_tag(ns_uri, name):
    if is_empty(ns_uri, name):
        return ''
    return '</%s>' % get_qname(ns_uri, name)


def get_doctype(name, doctype):
    return '<!DOCTYPE %s %s>' % (name, doctype.to_str())


def stream_to_str(stream, encoding='UTF-8'):
    data = []
    for event, value, line in stream:
        if event == TEXT:
            value = XMLContent.encode(value)
            data.append(value)
        elif event == START_ELEMENT:
            ns_uri, name, attributes = value
            data.append(get_start_tag(ns_uri, name, attributes))
        elif event == END_ELEMENT:
            ns_uri, name = value
            data.append(get_end_tag(ns_uri, name))
        elif event == COMMENT:
            data.append('<!--%s-->' % value)
        elif event == XML_DECL:
            version, encoding, standalone = value
            if standalone is None:
                data.append('<?xml version="%s" encoding="%s"?>'
                    % (version, encoding))
            else:
                data.append(
                    '<?xml version="%s" encoding="%s" standalone="%s"?>'
                    % (version, encoding, standalone))
        elif event == DOCUMENT_TYPE:
            name, doctype = value
            data.append(get_doctype(name, doctype))
        elif event == CDATA:
            data.append('<![CDATA[%s]]>' % value)
        else:
            raise NotImplementedError, 'unknown event "%s"' % event
    return ''.join(data)



def find_end(events, start):
    """Receives a list of events and a position in the list of an start
    element.

    Returns the position in the list where the element ends.
    """
    c = 1
    n = len(events)
    i = start + 1
    while i < n:
        event, value, line = events[i]
        if event == START_ELEMENT:
            c += 1
        elif event == END_ELEMENT:
            c -= 1
            if c == 0:
                return i
        i = i + 1
    return None


def get_element(events, name):
    i = 0
    for event, value, line in events:
        if event == START_ELEMENT:
            if name == value[1]:
                return Element(events, i)
        i += 1
    return None


class Element(object):

    __slots__ = ['events', 'start', 'end']

    def __init__(self, events, start):
        self.events = events
        self.start = start
        self.end = find_end(events, start)


    def get_content_elements(self):
        events = self.events

        i = self.start + 1
        while i < self.end:
            yield events[i]
            i += 1


    def get_content(self, encoding='UTF-8'):
        return stream_to_str(self.get_content_elements())



#############################################################################
# Documents
#############################################################################
class XMLFile(TextFile):
    """An XML file is represented in memory as a tree where the nodes are
    instances of the classes 'Element' and 'Raw'. The 'Element' class
    represents an XML element, the 'Raw' class represents a text string.

    XML sub-classes will, usually, provide their specific semantics by
    providing their own Element and Raw classes. This is the reason why
    we use 'self.Element' and 'self.Raw' throghout the code instead of
    just 'Element' and 'Raw'.
    """

    class_mimetypes = ['text/xml', 'application/xml']
    class_extension = 'xml'


    def new(self):
        # XML is a meta-language, it does not make change to create a bare
        # XML handler without a resource.
        raise NotImplementedError


    def _load_state_from_file(self, file):
        data = file.read()
        stream = XMLParser(data)
        self.events = list(stream)


    #######################################################################
    # API
    #######################################################################
    def to_str(self, encoding='UTF-8'):
        return stream_to_str(self.events, encoding)


    def set_events(self, events):
        self.set_changed()
        self.events = events


    def __cmp__(self, other):
        if not isinstance(other, self.__class__):
            return 1
        return cmp(self.events, other.events)


    def to_text(self):
        """Removes the markup and returns a plain text string.
        """
        text = [ unicode(value, 'utf-8') for event, value, line in self.events
                 if event == TEXT ]
        return u' '.join(text)


    #######################################################################
    # API / Internationalization - Localization
    #######################################################################
    def get_units(self, srx_handler=None):
        from i18n import get_units

        return get_units(self.events, srx_handler)


    def translate(self, catalog, srx_handler=None):
        from i18n import translate

        stream = translate(self.events, catalog, srx_handler)
        return stream_to_str(stream)


register_handler_class(XMLFile)
