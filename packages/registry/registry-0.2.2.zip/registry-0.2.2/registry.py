'''Registry API for common registry tasks.'''

import _winreg
import types


def _GuessValueType(value):
    '''Guess the type of the registry value.'''
    if isinstance(value, types.StringTypes):
        return _winreg.REG_SZ
    elif isinstance(value, types.IntType) or isinstance(value, types.LongType):
        return _winreg.REG_DWORD
    elif isinstance(value, types.ListType):
        return _winreg.REG_MULTI_SZ
    else:
        return _winreg.REG_BINARY


def _ChangeToMKTime(seconds):
    '''Change time by QueryInfoKey to mktime.'''
    # Time difference is 134774 days = days from 1.1.1600 -> 31.12.1968
    diff = 11644473600
    seconds = seconds / pow(10, 7)
    mktime = seconds - diff
    return mktime


# FUNCTIONS HANDLING SPECIFIC KEY-VALUE

def GetValue(keypath, valuename):
    '''Return (registry, registry type)-tuple.'''
    try:
        keytype, keyname = keypath.split('\\', 1)
    except ValueError:
        # key is a main-level key
        keytype, keyname = keypath, None

    key = getattr(_winreg, keytype)
    reg = _winreg.ConnectRegistry(None, key)
    handle = _winreg.OpenKey(reg, keyname, 0, _winreg.KEY_QUERY_VALUE)
    value, valuetype = _winreg.QueryValueEx(handle, valuename)
    _winreg.CloseKey(handle)
    return value, valuetype


def SetValue(keypath, valuename, value, valuetype=None):
    '''Set registry value.'''
    try:
        keytype, keyname = keypath.split('\\', 1)
    except ValueError:
        # key is a main-level key
        keytype, keyname = keypath, None

    key = getattr(_winreg, keytype)
    if valuetype is None:
        valuetype = _GuessValueType(value)
    elif isinstance(valuetype, types.StringTypes):
        valuetype = getattr(_winreg, valuetype)
    reg = _winreg.ConnectRegistry(None, key)
    handle = _winreg.OpenKey(reg, keyname, 0, _winreg.KEY_SET_VALUE)
    _winreg.SetValueEx(handle, valuename, 0, valuetype, value)
    _winreg.CloseKey(handle)


def DeleteValue(keypath, valuename):
    '''Delete a registry value.'''
    try:
        keytype, keyname = keypath.split('\\', 1)
    except ValueError:
        # key is a main-level key
        keytype, keyname = keypath, None

    key = getattr(_winreg, keytype)
    reg = _winreg.ConnectRegistry(None, key)
    handle = _winreg.OpenKey(reg, keyname, 0, _winreg.KEY_SET_VALUE)
    _winreg.DeleteValue(handle, valuename)
    _winreg.CloseKey(handle)



# FUNCTIONS FOR KEYS

def CreateKey(keypath):
    '''Create a key to registry.'''
    keypath, subkey = keypath.rsplit('\\', 1)
    try:
        keytype, keyname = keypath.split('\\', 1)
    except ValueError:
        # key is a main-level key
        keytype, keyname = keypath, None

    key = getattr(_winreg, keytype)
    reg = _winreg.ConnectRegistry(None, key)
    handle = _winreg.OpenKey(reg, keyname, 0, _winreg.KEY_CREATE_SUB_KEY)
    _winreg.CreateKey(handle, subkey)
    _winreg.CloseKey(handle)
   

def DeleteKey(keypath):
    '''Remove a key from the registry.'''
    keypath, subkey = keypath.rsplit('\\', 1)
    try:
        keytype, keyname = keypath.split('\\', 1)
    except ValueError:
        # key is a main-level key
        keytype, keyname = keypath, None
    key = getattr(_winreg, keytype)
    reg = _winreg.ConnectRegistry(None, key)
    handle = _winreg.OpenKey(reg, keyname, 0, _winreg.KEY_CREATE_SUB_KEY)
    _winreg.DeleteKey(handle, subkey)
    _winreg.CloseKey(handle)


def DeleteTree(keypath):
    '''Recursive remove keys and registry values from the registry.'''
    # Recursively delete subkeys first, from bottom up.
    subkeys = GetSubKeys(keypath)
    for subkey in subkeys:
        DeleteTree('%s\\%s' % (keypath, subkey))

    # Delete registry values
    subvalues = GetKeyValues(keypath)
    for value in subvalues:
        DeleteValue(keypath, value[0])

    # Delete current key
    DeleteKey(keypath)


def QueryInfoKey(key):
    '''Query information about a registry key.'''
    try:
        keytype, keyname = key.split('\\', 1)
    except ValueError:
        # key is a main-level key
        keytype, keyname = key, None
   
    keytype = getattr(_winreg, keytype)
    reg = _winreg.ConnectRegistry(None, keytype)
    handle = _winreg.OpenKey(reg, keyname, 0, _winreg.KEY_QUERY_VALUE)
    info = _winreg.QueryInfoKey(handle)
    _winreg.CloseKey(handle)
    return (info[0], info[1], _ChangeToMKTime(info[2]))


def GetKeyValues(key):
    '''Get (valuename, value, valuetype)-tuples from a given registry key.'''
    try:
        keytype, keyname = key.split('\\', 1)
    except ValueError:
        # key is a main-level key
        keytype, keyname = key, None
   
    lines = []
    info = QueryInfoKey(key)
    # Get values from current key-path
    keytype = getattr(_winreg, keytype)
    reg = _winreg.ConnectRegistry(None, keytype)
    handle = _winreg.OpenKey(reg, keyname, 0, _winreg.KEY_QUERY_VALUE)
    for i in range(info[1]):
        lines.append(_winreg.EnumValue(handle, i))
    _winreg.CloseKey(handle)
    lines.sort()
    return lines


def GetSubKeys(key):
    '''Find keys under given registry key.'''
    try:
        keytype, keyname = key.split('\\', 1)
    except ValueError:
        # key is a main-level key
        keytype, keyname = key, None

    lines = []
    info = QueryInfoKey(key)
    # Get values from current key-path
    keytype = getattr(_winreg, keytype)
    reg = _winreg.ConnectRegistry(None, keytype)
    handle = _winreg.OpenKey(reg, keyname, 0, _winreg.KEY_ENUMERATE_SUB_KEYS)
    for i in range(info[0]):
        lines.append(_winreg.EnumKey(handle, i))
    _winreg.CloseKey(handle)
    return lines


# FUNCTIONS FOR GETTING INFORMATION ABOUT KEYS

def GetDump(keypath):
    '''Return a registry tree dump under a given registry key.'''
    dump = {}
    dump[keypath] = []
    for valuename, data, valuetype in GetKeyValues(keypath):
        dump[keypath].append((valuename, data, valuetype))
    for subkey in GetSubKeys(keypath):
        dump.update(GetDump("%s\\%s" % (keypath, subkey)))
    return dump
   

def GetKeysModifiedAfter(keypath, after):
    '''Return a dump of registry keys modified after a given time.'''
    keys = {}
    info = QueryInfoKey(keypath)
    if info[2] >= after:
        keys[keypath] = info[2]
    for subkey in GetSubKeys(keypath):
        keys.update(GetKeysModifiedAfter("%s\\%s" % (keypath, subkey), after))
    return keys
