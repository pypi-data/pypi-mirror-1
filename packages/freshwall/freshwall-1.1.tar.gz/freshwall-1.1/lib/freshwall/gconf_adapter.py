# Copyright 2009 Chad Daelhousen.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#

"""Convert between Python values and GConfValue objects.

Supported types are str/unicode, list/tuple, bool, int, and float. Due to
the limitations of GConf, lists must be of a homogenous scalar type."""

import gconf

# Python native type => gconf.VALUE_* flag and 
_typemap = {bool: (gconf.VALUE_BOOL, "bool"),
            str: (gconf.VALUE_STRING, "string"),
            unicode: (gconf.VALUE_STRING, "string"),
            int: (gconf.VALUE_INT, "int"),
            float: (gconf.VALUE_FLOAT, "float"),
            list: (gconf.VALUE_LIST, "list"),
            tuple: (gconf.VALUE_LIST, "list")}

_revmap = {gconf.VALUE_STRING: (str, "string"),
          gconf.VALUE_LIST: (list, "list")}

for key, info in _typemap.items():
    gc_type, method_tail = info
    if gc_type in _revmap:
        continue
    _revmap[gc_type] = (key, method_tail)



def _get_type_of_value (value):
    """Return the GConfValueType of the Python value."""

    t = type(value)
    if t in _typemap:
        return _typemap[t][0]
    else:
        return None

def _get_method_tail_of_value (value):
    """Return the method name that deals with the Python value.

    For instance, an integer (Python int) is used with GConfValue.set_int()
    and this method returns 'int'."""

    t = type(value)
    if t in _typemap:
        return _typemap[t][1]
    else:
        return None

def box (value):
    """Convert a Python value to a GConfValue."""

    error_format = "Can't convert %s%s to GConfValue"

    gc_type = _get_type_of_value(value)
    if gc_type is None:
        raise NotImplementedError(error_format % ("", type(value)))

    gc_value = gconf.Value(gc_type)
    if gc_type == gconf.VALUE_LIST:
        list_type = _get_type_of_value(value[0])
        if list_type is None or list_type == gconf.VALUE_LIST:
            raise NotImplementedError(error_format % ("list/tuple of ",
                                                      type(value)))
        gc_value.set_list_type(gc_list_type)

    method_tail = _get_method_tail_of_value(value)
    method = getattr(gc_value, "set_" + method_tail)
    method(value)

    return gc_value

def unbox (gc_value):
    """Convert a GConfValue to a Python value."""

    if gc_value is None:
        return None

    gc_type = gc_value.type
    if gc_type in _revmap:
        t, method_tail = _revmap[gc_type]
        method = getattr(gc_value, "get_" + method_tail)
        value = method()
        return value
    else:
        raise NotImplementedError("Can't read GConfValue %s" % gc_type)

