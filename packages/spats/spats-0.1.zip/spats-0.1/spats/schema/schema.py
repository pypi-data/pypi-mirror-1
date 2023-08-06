# This module reads a configuration file
# for a schema and outputs fileds on that schema
#
# Think Archetypes without any extra Archetypes stuff

import sys
import os
import types

from win32com.client import GetObject
import isapi.install
import pywintypes
import pythoncom

from ConfigParser import ConfigParser, NoOptionError
from validation import getValidator, ValidationError

import logging
logger=logging.getLogger('spats')

templates = (
        # Return relative paths so the "app" can control things
        "spats/schema/templates/registry.pt",
        "spats/schema/templates/text.pt",
        "spats/schema/templates/password.pt",
        "spats/schema/templates/text_lines.pt",
        "spats/schema/templates/boolean.pt",
        "spats/schema/templates/choice.pt",
)

def get_iis_sites():
    ret = []
    try:
        try:
            pythoncom.CoInitializeEx(0)
        except pythoncom.com_error:
            pass
        ob = GetObject(isapi.install._IIS_OBJECT)
        for sub in ob:
            if sub.Class == isapi.install._IIS_SERVER:
                ret.append((sub.Name, sub.ServerComment))
    except pywintypes.com_error:
        logger.exception("Failed to locate IIS on this computer")
    return ret

def truncate(string):
    data = string.split(' ')
    if len(data) < 25:
        return string
    else:
        before = data[:20]
    return ' '.join(before) + '... see help for more'

class NoValue: pass
_marker = []

# This schema class is a little confused - it is both a schema *and*
# a container for field values.
class Schema:

    def __init__(self, id=None):
        self._fields_order = []
        self._fields = {}
        self._id = id

    def getId(self):
        return self._id

    def read(self, config, category):
        assert os.path.exists(config), "Config file could not be found"

        c = ConfigParser()
        c.read(config)
        all_sects = c.sections()
        all_sects.sort()
        for section in all_sects:
            schema_id = self.getId(), category
            f = Field(schema_id)

            # 'categories' is required, else fields will never be shown
            data = c.get(section, 'categories')
            cats = [ cat.strip() for cat in data.split(',') ]

            if category not in cats:
                # not part of this category
                continue
            f.setProperties(c.items(section))
            id = f.getId()

            assert id not in self._fields, "duplicate field ID %r" % (id,)
            self._fields_order.append(id)
            self._fields[id] = f

    def getField(self, id):
        field = self.getFields({'id':id})
        # should be just one field in the list
        if len(field)==0:
            raise KeyError, id
        assert len(field) == 1, "Can't have more than 1 ID"
        return field[0]

    def getFields(self, filter=None):
        res = []
        for field in self._fields_order:
            obj = self._fields[field]
            skip = False
            if filter:
                for k, v in filter.items():
                    if obj.getProperty(k) != v:
                        skip = True
            if not skip:
                res.append(obj)
        return res

    def allFields(self):
        return self._fields

    # A little helper for IIS site names.
    def siteIdToName(self, site_id):
        for id, name in get_iis_sites():
            if site_id.lower() == id.lower():
                return name
        # not found - who knows - just return the ID.
        return site_id

class Field:
    _properties = {}

    def __init__(self, schema_id):
        self._schema_id = schema_id # only used for logging/debugging.
        self._value = None
        self._properties = {}
        self._changed = False
        self._required = ['id',]
        self.error = None

    def hasChanged(self):
        return self._changed

    def setChanged(self, changed):
        self._changed = changed

    def getProperties(self):
        return self._properties

    def setProperty(self, k, v):
        self._properties[k] = v

    def setProperties(self, items):
        for key, value in items:
            self._properties[key] = value

        # add the 'default' value - ideally this would be done in a method,
        # but lots of things just refer directly to this property...
        if 'description' in self._properties:
            default = self.getProperty("default", '')
            if not default:
                default = "blank"
            self._properties['description'] += (u" (default=%s)" % default)

        for required in self._required:
            assert self._properties.get(required, None), "The value %s is required on the field: %s." % (required, self.getId())

    def getId(self):
        return self._properties['id']

    def getProperty(self, k, default=_marker):
        if not self._properties.has_key(k):
            if default is not _marker:
                return default
            else:
                raise KeyError, self.getId()
        else:
            return self._properties[k]

    def getType(self):
        try:
            return self.getProperty("type")
        except KeyError:
            return ''

    def getVocabulary(self):
        # hackery - but this code already sucks and is unlikely to be
        # truly general purpose.
        prop = self.getProperty("vocabulary", '').strip()
        if prop == '${iis_sites}':
            return get_iis_sites()

        # else ...
        ret = []
        for full in prop.split(';'):
            name, val=full.split('=', 1)
            ret.append((name.strip(), val.strip()))
        return ret

    def getValue(self, blank=_marker, raw=False):
        value = self._value
        if value is None:
            value = self.getProperty("default", '')

        logger.debug("getValue for [%s].%s=%r", self._schema_id, self.getId(), value )

        if not raw:
            # 'text_lines' is mis-named.  These are values which are space
            # sep'd in the INI file, but multi-line in the UI.
            if self.getType() == 'text_lines':
                value = value.replace(' ', '\n')
        return value

    def setValue(self, v, raw=False):
        if not raw:
            # 'text_lines' is mis-named.  These are values which are space
            # sep'd in the INI file, but multi-line in the UI.
            if self.getType() == 'text_lines':
                v = v.replace('\n', ' ')

        self.validate(v)
        if self.error is None:
            if self._value != v:
                self._changed = True
                self._value = v
            return True
        return False

    def validate(self, v):
        validator = self.getProperty('validator', None)
        if validator:
            try:
                getValidator(validator)(v)
                self.error = None
            except ValidationError, e:
                self.error = e
