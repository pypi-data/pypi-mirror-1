#   Copyright (c) 2007-2008 Open Source Applications Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os, sys

python_ver = '%d.%d.%d' %(sys.version_info[0:3])

try:
    if 'USE_DISTUTILS' in os.environ:
        raise ImportError
    from setuptools import setup, Extension
    from pkg_resources import require
    with_setuptools = require('setuptools')[0].version 
    enable_shared = (with_setuptools >= '0.6c7' and
                     sys.platform in ('darwin', 'linux2', 'win32'))
except ImportError:
    if python_ver < '2.4':
        raise ImportError, 'setuptools is required when using Python 2.3'
    else:
        from distutils.core import setup, Extension
        with_setuptools = None
        enable_shared = False

# Add or edit the entry corresponding to your system in the INCLUDES, CFLAGS
# and LFLAGS dictionaries below. These entries are used to build JCC _and_
# by JCC to drive compiling and linking via distutils or setuptools the
# extensions it generated code for.
# The key for your system is determined by sys.platform.
#
# Instead of editing the entries below, you may also override these
# dictionaries with JCC_INCLUDES, JCC_CFLAGS and JCC_LFLAGS environment
# variables using os.pathsep as value separator.

INCLUDES = {
    'darwin': ['/System/Library/Frameworks/JavaVM.framework/Versions/Current/Headers'],
    'linux2': ['/usr/lib/jvm/java-6-sun/include',
               '/usr/lib/jvm/java-6-sun/include/linux'],
    'sunos5': ['/usr/jdk/instances/jdk1.6.0/include',
               '/usr/jdk/instances/jdk1.6.0/include/solaris'],
    'win32': ['o:/Java/jdk1.6.0_02/include',
              'o:/Java/jdk1.6.0_02/include/win32'],
}

CFLAGS = {
    'darwin': ['-fno-strict-aliasing'],
    'linux2': ['-fno-strict-aliasing'],
    'sunos5': ['-features=iddollar',
               '-erroff=badargtypel2w,wbadinitl,wvarhidemem'],
    'win32': [],
}

LFLAGS = {
    'darwin': ['-framework', 'JavaVM'],
    'linux2': ['-L/usr/lib/jvm/java-6-sun/jre/lib/i386', '-ljava',
               '-Wl,-rpath=/usr/lib/jvm/java-6-sun/jre/lib/i386:/usr/lib/jvm/java-6-sun/jre/lib/i386/client'],
    'sunos5': ['-L/usr/jdk/instances/jdk1.6.0/jre/lib/i386', '-ljava',
               '-R/usr/jdk/instances/jdk1.6.0/jre/lib/i386:/usr/jdk/instances/jre/lib/i386/client'],
    'win32': ['/LIBPATH:o:/Java/jdk1.6.0_02/lib', 'jvm.lib']
}

#alternatives
#    'linux2': ['-L/usr/lib/jvm/java-6-sun/jre/lib/amd64', '-ljava',
#               '-Wl,-rpath=/usr/lib/jvm/java-6-sun/jre/lib/amd64:/usr/lib/jvm/java-6-sun/jre/lib/amd64/server'],


def main():

    _jcc_argsep = os.environ.get('JCC_ARGSEP', os.pathsep)

    if 'JCC_INCLUDES' in os.environ:
        _includes = os.environ['JCC_INCLUDES'].split(_jcc_argsep)
    else:
        _includes = INCLUDES[sys.platform]

    if 'JCC_CFLAGS' in os.environ:
        _cflags = os.environ['JCC_CFLAGS'].split(_jcc_argsep)
    else:
        _cflags = CFLAGS[sys.platform]

    if 'JCC_LFLAGS' in os.environ:
        _lflags = os.environ['JCC_LFLAGS'].split(_jcc_argsep)
    else:
        _lflags = LFLAGS[sys.platform]

    config = file(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'jcc', 'config.py'), 'w')
    print >>config
    print >>config, 'INCLUDES=%s' %(_includes)
    print >>config, 'CFLAGS=%s' %(_cflags)
    print >>config, 'LFLAGS=%s' %(_lflags)
    print >>config
    config.close()

    extensions = []

    boot = '_jcc'

    cflags = ['-DPYTHON'] + _cflags
    includes = _includes + [boot, 'jcc/sources']
    lflags = _lflags
    if sys.platform == 'win32':
        pass
    elif sys.platform == 'sunos5':
        lflags += ['-Wl,-s']
    else:
        lflags += ['-Wl,-S']

    sources = ['jcc/sources/jcc.cpp',
               'jcc/sources/JCCEnv.cpp',
               'jcc/sources/JObject.cpp',
               'jcc/sources/functions.cpp',
               'jcc/sources/types.cpp']
    for path, dirs, names in os.walk(boot):
        for name in names:
            if name.endswith('.cpp'):
                sources.append(os.path.join(path, name))

    if with_setuptools and enable_shared:
        from setuptools import Library
        if sys.platform == 'darwin':
            shlflags = lflags + ['-install_name', '@rpath/libjcc.dylib']
        else:
            shlflags = lflags
        extensions.append(Library('jcc',
                                  extra_compile_args=cflags,
                                  extra_link_args=shlflags,
                                  include_dirs=includes,
                                  sources=sources[0:2]))

    extensions.append(Extension('jcc._jcc',
                                extra_compile_args=cflags,
                                extra_link_args=lflags,
                                include_dirs=includes,
                                sources=sources))

    args = {
        'name': 'JCC',
        'version': '1.9',
        'description': 'a C++ code generator for calling Java from C++/Python',
        'long_description': open('DESCRIPTION').read(),
        'author': 'Andi Vajda',
        'author_email': 'vajda@osafoundation.org',
        'classifiers': ['Development Status :: 5 - Production/Stable',
                        'Environment :: Console',
                        'Intended Audience :: Developers',
                        'License :: OSI Approved :: Apache Software License',
                        'Operating System :: OS Independent',
                        'Programming Language :: C++',
                        'Programming Language :: Java',
                        'Programming Language :: Python',
                        'Topic :: Software Development :: Code Generators',
                        'Topic :: Software Development :: Libraries :: Java Libraries'],
        'packages': ['jcc'],
        'package_dir': {'jcc': 'jcc'},
        'package_data': {'jcc': ['sources/*.cpp', 'sources/*.h']},
        'ext_modules': extensions
    }
    if with_setuptools:
        args['zip_safe'] = False
        
    setup(**args)


if __name__ == "__main__":
    main()
