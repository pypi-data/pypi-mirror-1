##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from cgi import FieldStorage

import re
import tempfile

newlines = re.compile('\r\n|\n\r|\r')

# Flag Constants
SEQUENCE = 1
DEFAULT = 2
RECORD = 4
RECORDS = 8
REC = RECORD | RECORDS
CONVERTED = 32
DEFAULTABLE_METHODS = 'GET', 'POST', 'HEAD'

class ZopeFieldStorage(FieldStorage):

    def make_file(self, binary=None):
        return tempfile.NamedTemporaryFile('w+b')

class Record(object):

    _attrs = frozenset(('get', 'keys', 'items', 'values', 'copy',
                       'has_key', '__contains__'))

    def __getattr__(self, key, default=None):
        if key in self._attrs:
            return getattr(self.__dict__, key)
        raise AttributeError(key)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __str__(self):
        items = self.__dict__.items()
        items.sort()
        return "{" + ", ".join(["%s: %s" % item for item in items]) + "}"

    def __repr__(self):
        items = self.__dict__.items()
        items.sort()
        return ("{"
            + ", ".join(["%s: %s" % (key, repr(value))
            for key, value in items]) + "}")

class FileUpload(object):
    '''File upload objects

    File upload objects are used to represent file-uploaded data.

    File upload objects can be used just like files.

    In addition, they have a 'headers' attribute that is a dictionary
    containing the file-upload headers, and a 'filename' attribute
    containing the name of the uploaded file.
    '''

    def __init__(self, aFieldStorage):

        file = aFieldStorage.file
        if hasattr(file, '__methods__'):
            methods = file.__methods__
        else:
            methods = ['close', 'fileno', 'flush', 'isatty',
                'read', 'readline', 'readlines', 'seek',
                'tell', 'truncate', 'write', 'writelines',
                'name']

        d = self.__dict__
        for m in methods:
            if hasattr(file,m):
                d[m] = getattr(file,m)

        self.headers = aFieldStorage.headers
        self.filename = unicode(aFieldStorage.filename, 'UTF-8')

ArrayTypes = (list, tuple)

def field2string(v):
    return str(v)

def field2text(v, nl=newlines):
    return nl.sub("\n", field2string(v))

def field2required(v):
    v = field2string(v)
    if not v.strip():
        raise ValueError('No input for required field<p>')
    return v

def field2int(v):
    if isinstance(v, ArrayTypes):
        return map(field2int, v)
    v = field2string(v)
    if not v:
        raise ValueError('Empty entry when <strong>integer</strong> expected')
    try:
        return int(v)
    except ValueError:
        raise ValueError("An integer was expected in the value '%s'" % v)

def field2float(v):
    if isinstance(v, ArrayTypes):
        return map(field2float, v)
    v = field2string(v)
    if not v:
        raise ValueError(
            'Empty entry when <strong>floating-point number</strong> expected')
    try:
        return float(v)
    except ValueError:
        raise ValueError(
                "A floating-point number was expected in the value '%s'" % v)

def field2long(v):
    if isinstance(v, ArrayTypes):
        return map(field2long, v)
    v = field2string(v)

    # handle trailing 'L' if present.
    if v and v[-1].upper() == 'L':
        v = v[:-1]
    if not v:
        raise ValueError('Empty entry when <strong>integer</strong> expected')
    try:
        return long(v)
    except ValueError:
        raise ValueError("A long integer was expected in the value '%s'" % v)

def field2tokens(v):
    return field2string(v).split()

def field2lines(v):
    if isinstance(v, ArrayTypes):
        return [str(item) for item in v]
    return field2text(v).splitlines()

def field2boolean(v):
    return bool(v)

type_converters = {
    'float':    field2float,
    'int':      field2int,
    'long':     field2long,
    'string':   field2string,
    'required': field2required,
    'tokens':   field2tokens,
    'lines':    field2lines,
    'text':     field2text,
    'boolean':  field2boolean,
    }

get_converter = type_converters.get

class FieldMarshaller:
    def __init__(self, environ, fp, get_converter=get_converter):
        self._environ = environ
        self.fp = fp
        self.method = self._environ.get('REQUEST_METHOD', 'GET')
        self.charsets = ['utf-8']
        self.form = {}
        self.get_converter = get_converter
        
    def processInputs(self):
        'See IPublisherRequest'

        if self.method not in ('GET', 'HEAD'):
            # Process input fp if not a GET request.
            fp = self.fp
            if self.method == 'POST':
                content_type = self._environ.get('CONTENT_TYPE')
                if content_type and not (
                    content_type == 'application/x-www-form-urlencoded'
                    or
                    content_type.startswith('multipart/')
                    ):
                    # for non-multi and non-form content types, FieldStorage
                    # consumes the body and we have no good place to put it.
                    # So we just won't call FieldStorage. :)
                    return
        else:
            fp = None

        # If 'QUERY_STRING' is not present in self._environ
        # FieldStorage will try to get it from sys.argv[1]
        # which is not what we need.
        if 'QUERY_STRING' not in self._environ:
            self._environ['QUERY_STRING'] = ''

        fs = ZopeFieldStorage(fp=fp, environ=self._environ,
                              keep_blank_values=1)

        fslist = getattr(fs, 'list', None)
        if fslist is not None:
            self.meth = None
            self.tuple_items = {}
            self.defaults = {}

            # process all entries in the field storage (form)
            for item in fslist:
                self.processItem(item)

            if self.defaults:
                self.insertDefaults()

            if self.tuple_items:
                self.convertToTuples()

            if self.meth:
                self.setPathSuffix((self.meth,))

        return self.form

    _typeFormat = re.compile('([a-zA-Z][a-zA-Z0-9_]+|\\.[xy])$')

    def _decode(self, text):
        """Try to decode the text using one of the available charsets."""
        for charset in self.charsets:
            try:
                text = unicode(text, charset)
                break
            except UnicodeError:
                pass
        return text

    def processItem(self, item):
        """Process item in the field storage."""

        # Check whether this field is a file upload object
        # Note: A field exists for files, even if no filename was
        # passed in and no data was uploaded. Therefore we can only
        # tell by the empty filename that no upload was made.
        key = item.name
        if (hasattr(item, 'file') and hasattr(item, 'filename')
            and hasattr(item,'headers')):
            if (item.file and
                (item.filename is not None and item.filename != ''
                 # RFC 1867 says that all fields get a content-type.
                 # or 'content-type' in map(lower, item.headers.keys())
                 )):
                item = FileUpload(item)
            else:
                item = item.value

        flags = 0
        converter = None

        # Loop through the different types and set
        # the appropriate flags
        # Syntax: var_name:type_name

        # We'll search from the back to the front.
        # We'll do the search in two steps.  First, we'll
        # do a string search, and then we'll check it with
        # a re search.

        while key:
            pos = key.rfind(":")
            if pos < 0:
                break
            match = self._typeFormat.match(key, pos + 1)
            if match is None:
                break

            key, type_name = key[:pos], key[pos + 1:]

            # find the right type converter
            c = self.get_converter(type_name, None)

            if c is not None:
                converter = c
                flags |= CONVERTED
            elif type_name == 'list':
                flags |= SEQUENCE
            elif type_name == 'tuple':
                self.tuple_items[key] = 1
                flags |= SEQUENCE
            elif (type_name == 'method' or type_name == 'action'):
                if key:
                    self.meth = key
                else:
                    self.meth = item
            elif (type_name == 'default_method'
                    or type_name == 'default_action') and not self.meth:
                if key:
                    self.meth = key
                else:
                    self.meth = item
            elif type_name == 'default':
                flags |= DEFAULT
            elif type_name == 'record':
                flags |= RECORD
            elif type_name == 'records':
                flags |= RECORDS
            elif type_name == 'ignore_empty' and not item:
                # skip over empty fields
                return

        # Make it unicode if not None
        if key is not None:
            key = self._decode(key)

        if isinstance(item, str):
            item = self._decode(item)

        if flags:
            self.setItemWithType(key, item, flags, converter)
        else:
            self.setItemWithoutType(key, item)

    def setItemWithoutType(self, key, item):
        """Set item value without explicit type."""
        form = self.form
        if key not in form:
            form[key] = item
        else:
            found = form[key]
            if isinstance(found, list):
                found.append(item)
            else:
                form[key] = [found, item]

    def setItemWithType(self, key, item, flags, converter):
        """Set item value with explicit type."""
        #Split the key and its attribute
        if flags & REC:
            key, attr = self.splitKey(key)

        # defer conversion
        if flags & CONVERTED:
            try:
                item = converter(item)
            except:
                if item or flags & DEFAULT or key not in self.defaults:
                    raise
                item = self.defaults[key]
                if flags & RECORD:
                    item = getattr(item, attr)
                elif flags & RECORDS:
                    item = getattr(item[-1], attr)

        # Determine which dictionary to use
        if flags & DEFAULT:
            form = self.defaults
        else:
            form = self.form

        # Insert in dictionary
        if key not in form:
            if flags & SEQUENCE:
                item = [item]
            if flags & RECORD:
                r = form[key] = Record()
                setattr(r, attr, item)
            elif flags & RECORDS:
                r = Record()
                setattr(r, attr, item)
                form[key] = [r]
            else:
                form[key] = item
        else:
            r = form[key]
            if flags & RECORD:
                if not flags & SEQUENCE:
                    setattr(r, attr, item)
                else:
                    if not hasattr(r, attr):
                        setattr(r, attr, [item])
                    else:
                        getattr(r, attr).append(item)
            elif flags & RECORDS:
                last = r[-1]
                if not hasattr(last, attr):
                    if flags & SEQUENCE:
                        item = [item]
                    setattr(last, attr, item)
                else:
                    if flags & SEQUENCE:
                        getattr(last, attr).append(item)
                    else:
                        new = Record()
                        setattr(new, attr, item)
                        r.append(new)
            else:
                if isinstance(r, list):
                    r.append(item)
                else:
                    form[key] = [r, item]

    def splitKey(self, key):
        """Split the key and its attribute."""
        i = key.rfind(".")
        if i >= 0:
            return key[:i], key[i + 1:]
        return key, ""

    def convertToTuples(self):
        """Convert form values to tuples."""
        form = self.form

        for key in self.tuple_items:
            if key in form:
                form[key] = tuple(form[key])
            else:
                k, attr = self.splitKey(key)

                # remove any type_names in the attr
                i = attr.find(":")
                if i >= 0:
                    attr = attr[:i]

                if k in form:
                    item = form[k]
                    if isinstance(item, Record):
                        if hasattr(item, attr):
                            setattr(item, attr, tuple(getattr(item, attr)))
                    else:
                        for v in item:
                            if hasattr(v, attr):
                                setattr(v, attr, tuple(getattr(v, attr)))

    def insertDefaults(self):
        """Insert defaults into form dictionary."""
        form = self.form

        for keys, values in self.defaults.iteritems():
            if not keys in form:
                form[keys] = values
            else:
                item = form[keys]
                if isinstance(values, Record):
                    for k, v in values.items():
                        if not hasattr(item, k):
                            setattr(item, k, v)
                elif isinstance(values, list):
                    for val in values:
                        if isinstance(val, Record):
                            for k, v in val.items():
                                for r in item:
                                    if not hasattr(r, k):
                                        setattr(r, k, v)
                        elif not val in item:
                            item.append(val)

def marshal(environ, fp):
    marshaller = FieldMarshaller(environ, fp)
    return marshaller.processInputs()
