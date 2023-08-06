
from distutils.core import setup
import py2exe

setup(
    name = "registry",
    version = "0.2.2",
    author = 'Lauri Hallila',
    maintainer = 'Lauri Hallila',
    description = 'Windows registry API',
    long_description = 'Wrapper around _winreg for using registry.',
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
    py_modules = ['registry']
    )
