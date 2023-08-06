
import _winreg
import registry
import time

software = 'HKEY_CURRENT_USER'
testkey = 'HKEY_CURRENT_USER\\test'
subkey = '%s\\test' % testkey
subsubkey = '%s\\test' % subkey
subsubsubkey = '%s\\test' % subsubkey
subkey2 = '%s\\test2' % testkey


class TestRegistry(object):
    def setUp(self):
        '''Prepare test key for tests.'''
        if 'test' in registry.GetSubKeys(software):
            raise WindowsError, 'Key \'test\' already exists under HKEY_CURRENT_USER'
        registry.CreateKey(testkey)


    def tearDown(self):
        '''Remove test data.'''
        registry.DeleteTree(testkey)


    def test_createkey(self):
        '''Test that key was created by setUp().'''
        assert 'test' in registry.GetSubKeys(software)


    def test_delete_value(self):
        '''Test deleting value from the registry.'''
        registry.SetValue(testkey, 'test1', 'text')
        # Test enumerating registry values
        assert ('test1', 'text', _winreg.REG_SZ) in registry.GetKeyValues(testkey)
        # Test removing registry value
        registry.DeleteValue(testkey, 'test1')
        assert ('test1', 'text', _winreg.REG_SZ) not in registry.GetKeyValues(testkey)


    def test_sz_values(self):
        '''Test setting and getting string registry values.'''
        # Test guessing value_type
        registry.SetValue(testkey, 'test1', 'text')
        assert registry.GetValue(testkey, 'test1') == ('text', _winreg.REG_SZ)
        # Test giving value_type as a string
        registry.SetValue(testkey, 'test2', 'test', 'REG_SZ')
        assert registry.GetValue(testkey, 'test2') == ('test', _winreg.REG_SZ)
        #registry.DeleteValue(testkey, 'test2')
        # Test giving value_type as a number
        registry.SetValue(testkey, 'test3', 'test', _winreg.REG_SZ)
        assert registry.GetValue(testkey, 'test3') == ('test', _winreg.REG_SZ)
        #registry.DeleteValue(testkey, 'test3')


    def test_expand_sz_values(self):
        '''Test setting and getting expand_sz values.'''
        # Test giving value_type as a string
        registry.SetValue(testkey, 'test12', '%WINDIR%', 'REG_EXPAND_SZ')
        assert registry.GetValue(testkey, 'test12') == ('%WINDIR%', _winreg.REG_EXPAND_SZ)
        #registry.DeleteValue(testkey, 'test12')
        # Test giving value_type as a number
        registry.SetValue(testkey, 'test13', '%WINDIR%', _winreg.REG_EXPAND_SZ)
        assert registry.GetValue(testkey, 'test13') == ('%WINDIR%', _winreg.REG_EXPAND_SZ)
        #registry.DeleteValue(testkey, 'test13')


    def test_multi_sz_values(self):
        '''Test setting and getting multi_sz registry values.'''
        # Test guessing value_type
        registry.SetValue(testkey, 'test7', ['jee', 'kyll'])
        assert registry.GetValue(testkey, 'test7') == (['jee', 'kyll'], _winreg.REG_MULTI_SZ)
        #registry.DeleteValue(testkey, 'test7')
        # Test giving value_type as a string
        registry.SetValue(testkey, 'test8', ['jee', 'kyll'], 'REG_MULTI_SZ')
        assert registry.GetValue(testkey, 'test8') == (['jee', 'kyll'], _winreg.REG_MULTI_SZ)
        #registry.DeleteValue(testkey, 'test8')
        # Test giving value_type as a number
        registry.SetValue(testkey, 'test9', ['jee', 'kyll'], _winreg.REG_MULTI_SZ)
        assert registry.GetValue(testkey, 'test9') == (['jee', 'kyll'], _winreg.REG_MULTI_SZ)
        #registry.DeleteValue(testkey, 'test9')


    def test_dword_values(self):
        '''Test setting and getting dword registry values.'''
        # Test guessing value_type
        registry.SetValue(testkey, 'test4', 10)
        assert registry.GetValue(testkey, 'test4') == (10, _winreg.REG_DWORD)
        #registry.DeleteValue(testkey, 'test4')
        # Test giving value_type as a string
        registry.SetValue(testkey, 'test5', 10, 'REG_DWORD')
        assert registry.GetValue(testkey, 'test5') == (10, _winreg.REG_DWORD)
        #registry.DeleteValue(testkey, 'test5')
        # Test giving value_type as a number
        registry.SetValue(testkey, 'test6', 10, _winreg.REG_DWORD)
        assert registry.GetValue(testkey, 'test6') == (10, _winreg.REG_DWORD)
        #registry.DeleteValue(testkey, 'test6')


    def test_binary_values(self):
        '''Test setting and getting binary registry values.'''
        # Test giving value_type as a string
        registry.SetValue(testkey, 'test10', '\x00\x01\x02\x03', 'REG_BINARY')
        assert registry.GetValue(testkey, 'test10') == ('\x00\x01\x02\x03', _winreg.REG_BINARY)
        #registry.DeleteValue(testkey, 'test10')
        # Test giving value_type as a number
        registry.SetValue(testkey, 'test11', '\x00\x01\x02\x03', _winreg.REG_BINARY)
        assert registry.GetValue(testkey, 'test11') == ('\x00\x01\x02\x03', _winreg.REG_BINARY)
        #registry.DeleteValue(testkey, 'test11')


    def test_none_values(self):
        registry.SetValue(testkey, 'test14', '\x00\x01\x02\x03', 'REG_NONE')
        assert registry.GetValue(testkey, 'test14') == ('\x00\x01\x02\x03', _winreg.REG_NONE)
        registry.SetValue(testkey, 'test15', '\x00\x01\x02\x03', _winreg.REG_NONE)
        assert registry.GetValue(testkey, 'test15') == ('\x00\x01\x02\x03', _winreg.REG_NONE)


    def test_dword_big_endian_values(self):
        registry.SetValue(testkey, 'test16', '20', 'REG_DWORD_BIG_ENDIAN')
        assert registry.GetValue(testkey, 'test16') == ('20', _winreg.REG_DWORD_BIG_ENDIAN)
        registry.SetValue(testkey, 'test17', '20', _winreg.REG_DWORD_BIG_ENDIAN)
        assert registry.GetValue(testkey, 'test17') == ('20', _winreg.REG_DWORD_BIG_ENDIAN)


    def test_keys(self):
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


    def test_dump(self):
        dump = registry.GetDump(testkey)
        assert testkey in dump


    def test_keysmodifiedafter(self):
        keys = registry.GetKeysModifiedAfter(testkey, time.time() - 120)
        assert testkey in keys
        keys = registry.GetKeysModifiedAfter(testkey, time.time())
        assert testkey not in keys


    def test_deletekey(self):
        registry.CreateKey(subkey)
        assert 'test' in registry.GetSubKeys(testkey)
        # Test deleting registry key
        registry.DeleteKey(subkey)
        assert 'test' not in registry.GetSubKeys(testkey)


    def test_deletetree(self):
        registry.CreateKey(subkey)
        registry.CreateKey(subsubkey)
        registry.CreateKey(subsubsubkey)
        registry.CreateKey(subkey2)
        registry.DeleteTree(subkey)
        assert 'test' not in registry.GetSubKeys(testkey)


    def test_getdump(self):
        d = registry.GetDump('HKEY_CURRENT_USER', ignore_errors=True)


    def test_getvalues(self):
        v = registry.GetValues('HKEY_CURRENT_USER', ignore_errors=True)
