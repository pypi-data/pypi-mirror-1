"""Contains a class for testing registry API
with nose.
"""


import _winreg
import registry
import time
import types

QWORD = 11

software = 'HKEY_CURRENT_USER'
testkey = 'HKEY_CURRENT_USER\\test'
testkey_unicode = u'HKEY_CURRENT_USER\\test\u3002'
subkey = '%s\\test' % testkey
subsubkey = '%s\\test' % subkey
subsubsubkey = '%s\\test' % subsubkey
subkey2 = '%s\\test2' % testkey


# Create test (key, value) - pairs
testkeys = ['test1', u'test2', u'test\u3002']
# None is for default values
testnames = [None, 'test1', u'test2', u'test\u3002']


class TestRegistry(object):
    '''A class for testing registry API with nose.'''
    def __init__(self):
        self.testitems = []
        for key in testkeys:
            for name in testnames:
                self.testitems.append(('%s\\%s' % (testkey, key), name))


    def _run_value_test(self, key, name, value, valtype,
                        expected=None, expected_valtype=None):
        '''Test setting and getting value.'''
        # If expected value not specified, use value of 'value'
        if expected is None:
            expected = value
        if expected_valtype is None:
            # If expected value type not specified, use valtype
            if isinstance(valtype, types.StringTypes):
                expected_valtype = getattr(_winreg, valtype)
            elif isinstance(valtype, types.IntType):
                expected_valtype = valtype
        # Verify that expected entry not found within key
        assert (name, value, expected_valtype) not in registry.GetKeyValues(key)
        # Set value
        registry.SetValue(key, name, value, valtype)
        # Verify that value is set with correct parameters
        assert registry.GetValue(key, name) == (expected, expected_valtype)
        if name != None:
            # Check inclusion in GetKeyValues, if not the default value
            assert (name, expected, expected_valtype) in \
                   registry.GetKeyValues(key)
        # Remove value
        registry.DeleteValue(key, name)
        # Check that registry value does not exist
        try:
            value = registry.GetValue(key, name)
        except WindowsError, error:
            assert str(error) == str(2)
        # Check that removal worked with GetKeyValues, too
        assert (name, expected, expected_valtype) not in \
               registry.GetKeyValues(key)


    def setUp(self):
        '''Prepare test key for tests.'''
        subkeys = registry.GetSubKeys(software)
        if 'test' in subkeys:
            raise WindowsError, \
                  'Key \'test\' already exists under HKEY_CURRENT_USER'
        registry.CreateKey(testkey)
        for key in testkeys:
            registry.CreateKey('%s\\%s' % (testkey, key))


    def tearDown(self):
        '''Remove test data.'''
        registry.DeleteTree(testkey)


    def test_sz_values(self):
        '''Test setting and getting string registry values.'''
        for key, name in self.testitems:
            for value in ('', u'', 'text', u'text2', u'text\u3002'):
                # Test guessing value_type
                self._run_value_test(key, name, value, None,
                                     expected_valtype=_winreg.REG_SZ)
                # Test giving value_type as a string
                self._run_value_test(key, name, value, _winreg.REG_SZ)
                # Test giving value_type as a number
                self._run_value_test(key, name, value, 'REG_SZ')


    def test_expand_sz_values(self):
        '''Test setting and getting expand_sz values.'''
        for key, name in self.testitems:
            for value in ('',
                          u'',
                          '%WINDIR%',
                          u'C:\\%WINDIR%',
                          u'C:\\%WINDIR%\\\u3002'):
                # Test giving value_type as a string
                self._run_value_test(key, name, value, 'REG_EXPAND_SZ')
                # Test giving value_type as a number
                self._run_value_test(key, name, value, _winreg.REG_EXPAND_SZ)


    def test_multi_sz_values(self):
        '''Test setting and getting multi_sz registry values.'''
        for key, name in self.testitems:
            for value in ([],
                          ['val1'],
                          [u'val2'],
                          [u'test\u3002'],
                          ['val1', 'test1'],
                          [u'val2', u'test2'],
                          [u'val\u3002', u'test\u3002'],
                          ['val3', u'test3'],
                          ['val4', u'test\u3002'],
                          [u'val5', u'test5\u3002']
                          ):
                # Test guessing value_type
                self._run_value_test(key, name, value, None,
                                     expected_valtype=_winreg.REG_MULTI_SZ)
                # Test giving value_type as a string
                self._run_value_test(key, name, value, 'REG_MULTI_SZ')
                # Test giving value_type as a number
                self._run_value_test(key, name, value, _winreg.REG_MULTI_SZ)


    def test_dword_values(self):
        '''Test setting and getting dword registry values.'''
        for key, name in self.testitems:
            # Test guessing value_type
            self._run_value_test(key, name, 0, None,
                                 expected_valtype=_winreg.REG_DWORD)
            # Test giving value_type as a string
            self._run_value_test(key, name, 5, 'REG_DWORD')
            # Test giving value_type as a number
            self._run_value_test(key, name, 10, _winreg.REG_DWORD)
            # Test giving value_type as a string
            self._run_value_test(key, name, '15', 'REG_DWORD',
                                 expected=15)
            # Test giving value_type as a number
            self._run_value_test(key, name, '20', _winreg.REG_DWORD,
                                 expected=20)


    def test_dword_little_endian_values(self):
        '''Test setting and getting little endian integers in registry.'''
        for key, name in self.testitems:
            self._run_value_test(key, name, 0, 'REG_DWORD_LITTLE_ENDIAN')
            self._run_value_test(key, name, 5, _winreg.REG_DWORD_LITTLE_ENDIAN)
            self._run_value_test(key, name, '10', 'REG_DWORD_LITTLE_ENDIAN',
                                 expected=10)
            self._run_value_test(key, name, '15',
                                 _winreg.REG_DWORD_LITTLE_ENDIAN,
                                 expected=15)


    def test_dword_big_endian_values(self):
        '''Test setting and getting big endian integers in registry.'''
        for key, name in self.testitems:
            self._run_value_test(key, name, 0, 'REG_DWORD_BIG_ENDIAN')
            self._run_value_test(key, name, 5, _winreg.REG_DWORD_BIG_ENDIAN)
            self._run_value_test(key, name, '10', 'REG_DWORD_BIG_ENDIAN',
                                 expected=10)
            self._run_value_test(key, name, '15', _winreg.REG_DWORD_BIG_ENDIAN,
                                 expected=15)


    def test_qword_values(self):
        '''Test setting and getting QWORD integers in registry.'''
        for key, name in self.testitems:
            self._run_value_test(key, name, 0, QWORD)
            self._run_value_test(key, name, 5, 'REG_QWORD',
                                 expected_valtype=QWORD)
            self._run_value_test(key, name, '10', QWORD, expected=10)
            self._run_value_test(key, name, '15', 'REG_QWORD', expected=15,
                                 expected_valtype=QWORD)


    def test_raw_data_values(self):
        '''Test setting and getting registry values stored as raw data.'''
        for valtype in ('REG_BINARY',
                        'REG_NONE',
                        'REG_RESOURCE_LIST',
                        'REG_RESOURCE_REQUIREMENTS_LIST',
                        'REG_FULL_RESOURCE_DESCRIPTOR'):
            for key, name in self.testitems:
                self._run_value_test(key, name, '', valtype)
                self._run_value_test(key, name, '\x00\x01\x02\x03', valtype)
                valcode = getattr(_winreg, valtype)
                self._run_value_test(key, name, '\x01\x02\x03\x04', valcode)


    def test_createkey(self):
        '''Test that key was created by setUp().'''
        subkeys = registry.GetSubKeys(software)
        assert 'test' in subkeys


    def test_keys(self):
        '''Test creating keys.'''
        registry.CreateKey(subkey)
        registry.CreateKey(subkey2)
        registry.CreateKey(subsubkey)
        registry.SetValue(subkey, 'test', 5)
        registry.SetValue(subkey, 'test2', 6)
        info = registry.QueryInfoKey(subkey)
        # 1 subkey and 2 subvalues
        assert info[:2] == (1, 2)
        # test timestamp
        assert time.time() > info[2]
        assert (time.time() - 60) < info[2]


    def test_deletekey(self):
        '''Test creating and removing a registry key.'''
        for key in testkeys:
            test_subkey = '%s\\%s' % (testkey, key)
            registry.CreateKey(test_subkey)
            registry.SetValue(test_subkey, 'test', 'text')
            assert key in registry.GetSubKeys(testkey)
            # Test deleting registry key
            registry.DeleteKey(test_subkey)
            assert key not in registry.GetSubKeys(testkey)


    def test_deletetree(self):
        '''Test removing registry keys recursively.'''
        registry.CreateKey(subkey)
        registry.CreateKey(subsubkey)
        registry.CreateKey(subsubsubkey)
        registry.CreateKey(subkey2)
        registry.DeleteTree(subkey)
        assert 'test' not in registry.GetSubKeys(testkey)


    def test_dump(self):
        '''Test GetDump-function.'''
        dump = registry.GetDump(testkey)
        assert testkey in dump


    def test_keysmodifiedafter(self):
        '''Test GetKeysModifiedAfter-function.'''
        keys = registry.GetKeysModifiedAfter(testkey, time.time() - 120)
        assert testkey in keys
        keys = registry.GetKeysModifiedAfter(testkey, time.time())
        assert testkey not in keys


    def test_getvalues(self):
        '''Test GetValues-function.'''
        registry.SetValue(testkey, 'test', 'text')
        values = registry.GetValues(testkey, ignore_errors=True)
        assert (testkey, 'test', 'text', _winreg.REG_SZ) in values
