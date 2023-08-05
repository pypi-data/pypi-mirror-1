#! /usr/bin/python
#
# Copyright (C) 2006 Giuseppe Corbelli
#
# This file is part of Pyreb.
#
# Pyreb is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# Pyreb is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Pyreb; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from distutils.core import setup
import sys
from distutils.command.install_scripts import install_scripts as _install_scripts
from distutils.command.build_scripts import build_scripts as _build_scripts
from pprint import pprint
from os.path import split, join
from Pyreb import PYREB_VERSION
import py2exe

manifest_template = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
/>
<description>Pyreb Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
'''
RT_MANIFEST = 24

SCRIPT="""#!/usr/bin/python
import Pyreb
PyrebApp(%s, redirect=False).MainLoop()
"""

if (sys.platform.startswith('win')):
    ScriptName = 'pyreb.bat'
    Script = "@ECHO OFF\r\n%s -c \"import Pyreb;Pyreb.main()\"" % (sys.executable)
else:
    ScriptName = 'pyreb'
    Script = "#! /bin/sh\n%s -c \"import Pyreb;Pyreb.main()\"" % (sys.executable)

class build_scripts(_build_scripts):
    """ Generate the startup script.
    """
    def __init__(self, dist):
        _build_scripts.__init__(self, dist)
        fd = file (ScriptName, "w")
        fd.write(Script)
        fd.close()

class install_scripts(_install_scripts):
    """ This can be used to get the full installation path of scripts.
    """
    def __init__(self, dist):
        _install_scripts.__init__(self, dist)
        install_cmd = self.get_finalized_command('install')
        install_base = getattr(install_cmd, 'install_base')
        install_scripts =  getattr(install_cmd, 'install_scripts')
        destdir = join(install_base, split(install_scripts)[-1])
        destfile = join(destdir, "Pyreb_start.py")


# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None

#This is an hack needed for py2exe
#since py2exe does not (still?) support the files listed in package_data
#I was forced to put them into data_files
DataFiles = [("Pyreb-doc", ["README", "AUTHORS", "LICENSE"])]
if ("py2exe" in sys.argv):
    DataFiles.append( ("Resource", ['Pyreb/Resource/pyreb_wxglade.xrc', 'Pyreb/Resource/PreMade.list']) )

#py2exe main object
pyreb_exe = dict(
    script='start.py',
    other_resources=[ (RT_MANIFEST, 1, manifest_template) ],    
)

dist = setup(
    name='Pyreb',
    version=PYREB_VERSION,
    description='Pyreb is a wxPython based tool that helps building Python Regular expressions',
    long_description="""\
Pyreb is a wxPython GUI to the re python module; it will speed up the \
development of Python regular expression (similar to PCRE).\
The GUI is simple and features 3 parts:
    1) A text box where the text to be analyzed is displayed
    2) A text box where the regular expression to be applied is displayed
    3) A tree control where the results are displayed

When one of the two textboxes change the regex is compiled and applied. Errors \
in the regex are shown in a statusbar.

Pyreb ships with a simple XMLRPC server that can be used to control pyreb \
from an external application.

Pyreb is somewhat similar to Activestate RX Toolkit (part of Komodo IDE), but \
is a completely different project.""",
    author='Giuseppe "Cowo" Corbelli',
    author_email='cowo@lugbs.linux.it',
    url='http://pyreb.nongnu.org/',
    packages=['Pyreb', 'Pyreb.Controls', 'Pyreb.Dialogs', 'Pyreb.Server'],
    package_dir={'Pyreb': 'Pyreb'},
    package_data={'Pyreb': ['Resource/pyreb_wxglade.xrc', 'Resource/PreMade.list']},
    data_files=DataFiles,
    scripts=[ScriptName],
    license='GPL',
    platforms='GNU/Linux, Win32',
    keywords={
        'Metadata-Version' : 1.0,
        'Requires' : 're',
        'Requires' : 'wxPython (>=2.6.0)'
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Office/Business',
        'Topic :: Software Development',
        'Topic :: Text Processing',
    ],
    cmdclass={
        'build_scripts': build_scripts,
    },
    options={"py2exe": {
        "excludes": ["Tkinter"],
        "packages": ['Pyreb', 'Pyreb.Controls', 'Pyreb.Dialogs', 'Pyreb.Server'],
        "compressed": 1,
        }
    },
    windows=[pyreb_exe],
)
