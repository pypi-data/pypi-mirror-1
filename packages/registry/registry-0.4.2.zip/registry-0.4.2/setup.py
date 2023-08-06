
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name = "registry",
    version = "0.4.2",
    author = 'Lauri Hallila',
    author_email = 'lhallila at welho dot com',
    license = 'Public domain',
    maintainer = 'Lauri Hallila',
    maintainer_email = 'lhallila at welho dot com',
    description = 'Windows registry API',
    long_description = '''Wrapper around Windows API registry calls.

Registry calls are handled through ctypes by calling functions
from advapi32.dll.
''',
    classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Win32 (MS Windows)',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: Freely Distributable',
          'Operating System :: Microsoft :: Windows',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules'
          ],
    py_modules = ['registry', '_registry'],
    ext_packages = ['test'],
    tests_require = ['nose']
    )
