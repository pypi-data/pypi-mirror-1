#!/usr/bin/env python

DESCRIPTION="""This is a MySQL interface for Python that is written in Pyrex.

It is an effort to provide an object-oriented interface to the new Statement
interface introduced in MySQL 5.  It also provides a specialized interface to
the "classic" MySQL API that should be extremely easy to use.

It specifically does not conform to the Python DB API (PEP 249).  I wanted to
express a different style of API.  One could probably make a relatively close
wrapper, though.
"""

import sys

# Check Python version.
if sys.hexversion < 0x020402f0:
    print 'This library requires Python version 2.4.2 or newer (but not 2.5).'
    sys.exit(1)

if sys.hexversion >= 0x02050000:
    print 'This library does not yet support Python 2.5.'
    sys.exit(1)

from ez_setup import use_setuptools
use_setuptools()

import distutils.version
import re
import subprocess
from Pyrex.Distutils.build_ext import build_ext
from Pyrex.Distutils.extension import PyrexExtension
from setuptools import setup, Extension

def run(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        # Lazy
        raise OSError
    return stdout.strip()

# Check MySQL version.
try:
    mysql_version_string = run(['mysql_config', '--version'])
except OSError:
    print 'MySQL does not appear to be installed.'
    # Or version is older than 3.23.21.
    sys.exit(1)

mysql_version = distutils.version.LooseVersion(mysql_version_string)
mysql_min_version = distutils.version.LooseVersion('5.0.15')
mysql_max_version = distutils.version.LooseVersion('5.0.27')

if mysql_version < mysql_min_version:
    print 'Must have MySQL 5.0.15 or newer installed.'
    sys.exit(1)
if mysql_version > mysql_max_version:
    print 'WARNING: The version of mysql you have is newer than what has been'
    print '         tested with this library.  It may not work or may not even'
    print '         compile.  The latest tested version is %s.' % (mysql_max_version,)

mysql_match = re.match(r'(\d+)\.(\d+)\.(\d+)(.*)', mysql_version_string)
mysql_version_ext = mysql_match.group(4)
# Similar to Python's patchlevel.h.
RELEASE_LEVEL_ALPHA = 1
RELEASE_LEVEL_BETA  = 2
RELEASE_LEVEL_GAMMA = 3
RELEASE_LEVEL_FINAL = 9

# Not entirely familiar with MySQL's versioning scheme, this may need to be
# extended.
if mysql_version_ext == 'a':
    release_level = RELEASE_LEVEL_FINAL
    release_serial = 1
elif mysql_version_ext == '-alpha':
    release_level = RELEASE_LEVEL_ALPHA
    release_serial = 0
elif mysql_version_ext == '-beta':
    release_level = RELEASE_LEVEL_BETA
    release_serial = 0
elif mysql_version_ext == '':
    release_level = RELEASE_LEVEL_FINAL
    release_serial = 0
else:
    print 'Unable to parser MySQL version string properly (%s)' % (mysql_version_string,)
    sys.exit(1)

mysql_version_int = (int(mysql_match.group(1)) * 1000000 +
                     int(mysql_match.group(2)) * 10000 +
                     int(mysql_match.group(3)) * 100 +
                     release_level             * 10 +
                     release_serial
                     )

def MySQL_Extension(*args, **kwargs):

    kwargs['pyrex_include_dirs'] = ['./mysql']

    #kwargs['include_dirs'] = ['/usr/local/include/mysql']
    #kwargs['library_dirs'] = ['/usr/local/lib/mysql']
    #kwargs['libraries'] = ['mysqlclient', 'z']

    # Argh, distutils does not allow one to pass in a string of multiple
    # options.  This will break on paths with spaces in them.
    kwargs['extra_compile_args'] = run(['mysql_config', '--cflags']).split()
    kwargs['extra_link_args'] = run(['mysql_config', '--libs']).split()
    kwargs['compile_time_symbols'] = {'MYSQL_VERSION': mysql_version_int}

    # Until the time when I finish a reliable dependency finder, we'll just
    # specify them manually for now.
    kwargs.setdefault('depends', []).extend(['mysql/extern_mysql.pxd',
                                             'mysql/python.pxi',
                                             'mysql/libc.pxi',
                                             'mysql/util/inline.pyx',
                                             'mysql/util/inline.h',
                                            ]
                                           )
    kwargs.setdefault('include_dirs', []).extend(['mysql/util'])

#        --cflags         [-I/usr/local/include/mysql -O -pipe  -D_THREAD_SAFE]
#        --include        [-I/usr/local/include/mysql]
#        --libs           [-L/usr/local/lib -L/usr/local/lib/mysql -lmysqlclient -lz -lcrypt -lm]
#        --libs_r         [-L/usr/local/lib -L/usr/local/lib/mysql -lmysqlclient_r -lz -pthread -lcrypt -lm  -pthread]
#        --socket         [/tmp/mysql.sock]
#        --port           [3306]
#        --version        [5.0.15]
#        --libmysqld-libs [-L/usr/local/lib -L/usr/local/lib/mysql -lmysqld -lz -pthread -lcrypt -lm  -pthread   -lwrap]

    return PyrexExtension(*args, **kwargs)


setup(name='mysql-pyrex',
      version='0.9.0a1',
      packages=['mysql', 'mysql.constants',
                         'mysql.conversion',
                         'mysql.exceptions',
                         'mysql.stmt',
                         'mysql.util',
               ],
      author='Eric Huss',
      author_email='eric@ehuss.org',
      url='http://ehuss.org/mysql/',
      description='Pyrex interface to the MySQL 5 API.',
      long_description=DESCRIPTION,
      license='BSD',
      classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: BSD License',
            'Topic :: Database',
      ],
      ext_modules=[MySQL_Extension('mysql.connection',
                                   ['mysql/mysql.connection.pyx'],
                                   depends=['mysql/mysql.connection.pxd',
                                            'mysql/mysql.result.pxd',
                                           ],
                                  ),
                   MySQL_Extension('mysql.constants.client_flags',
                                   ['mysql/constants/client_flags.pyx'],
                                  ),
                   MySQL_Extension('mysql.constants.field_flags',
                                   ['mysql/constants/field_flags.pyx'],
                                  ),
                   MySQL_Extension('mysql.constants.field_types',
                                   ['mysql/constants/field_types.pyx'],
                                  ),
                   MySQL_Extension('mysql.exceptions.map',
                                   ['mysql/exceptions/map.pyx'],
                                   depends=['mysql/mysql_cr.pxi',
                                            'mysql/mysql_er.pxi',
                                           ],
                                  ),
                   MySQL_Extension('mysql.result',
                                   ['mysql/mysql.result.pyx'],
                                   depends=['mysql/mysql.result.pxd',
                                           ],
                                  ),
                   MySQL_Extension('mysql.stmt.stmt',
                                   ['mysql/stmt/mysql.stmt.stmt.pyx'],
                                   depends=['mysql/stmt/mysql.stmt.stmt.pxd',
                                            'mysql/mysql.result.pxd',
                                            'mysql/stmt/mysql.stmt.bind_in.pxd',
                                            'mysql/stmt/mysql.stmt.bind_out.pxd',
                                           ],
                                  ),
                   MySQL_Extension('mysql.stmt.bind_in',
                                   ['mysql/stmt/mysql.stmt.bind_in.pyx'],
                                   depends=['mysql/mysql.connection.pxd',
                                            'mysql/stmt/mysql.stmt.bind_in.pxd',
                                           ],
                                  ),
                   MySQL_Extension('mysql.stmt.bind_out',
                                   ['mysql/stmt/mysql.stmt.bind_out.pyx'],
                                   depends=['mysql/mysql.connection.pxd',
                                            'mysql/stmt/mysql.stmt.bind_out.pxd',
                                           ],
                                  ),
                   PyrexExtension('mysql.util.misc',
                                  ['mysql/util/misc.pyx'],
                                  pyrex_include_dirs = ['./mysql'],
                                 ),
                   Extension('mysql.util._c_only',
                             ['mysql/util/_c_only.c'],
                            ),
                  ],
      cmdclass={'build_ext': build_ext},
     )
