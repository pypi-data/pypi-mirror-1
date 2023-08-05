#! /usr/bin/env python
#
# Copyright (c) 2001 Bizar Software Pty Ltd (http://www.bizarsoftware.com.au/)
# This module is free software, and you may redistribute it and/or modify
# under the same terms as Python, so long as this copyright message and
# disclaimer are retained in their original form.
#
# IN NO EVENT SHALL BIZAR SOFTWARE PTY LTD BE LIABLE TO ANY PARTY FOR
# DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING
# OUT OF THE USE OF THIS CODE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# BIZAR SOFTWARE PTY LTD SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE.  THE CODE PROVIDED HEREUNDER IS ON AN "AS IS"
# BASIS, AND THERE IS NO OBLIGATION WHATSOEVER TO PROVIDE MAINTENANCE,
# SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
# 
# $Id$

from distutils.core import setup, Extension
from distutils.util import get_platform
from distutils.command.build_scripts import build_scripts

import sys, os, string
from glob import glob

# patch distutils if it can't cope with the "classifiers" keyword
from distutils.dist import DistributionMetadata
if not hasattr(DistributionMetadata, 'classifiers'):
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None


#############################################################################
### Build script files
#############################################################################

class build_scripts_create(build_scripts):
    """ Overload the build_scripts command and create the scripts
        from scratch, depending on the target platform.

        You have to define the name of your package in an inherited
        class (due to the delayed instantiation of command classes
        in distutils, this cannot be passed to __init__).

        The scripts are created in an uniform scheme: they start the
        run() function in the module

            <packagename>.scripts.<mangled_scriptname>

        The mangling of script names replaces '-' and '/' characters
        with '-' and '.', so that they are valid module paths. 
    """
    package_name = None

    def copy_scripts(self):
        """ Create each script listed in 'self.scripts'
        """
        if not self.package_name:
            raise Exception("You have to inherit build_scripts_create and"
                " provide a package name")
        
        to_module = string.maketrans('-/', '_.')

        self.mkpath(self.build_dir)
        for script in self.scripts:
            outfile = os.path.join(self.build_dir, os.path.basename(script))

            #if not self.force and not newer(script, outfile):
            #    self.announce("not copying %s (up-to-date)" % script)
            #    continue

            if self.dry_run:
                self.announce("would create %s" % outfile)
                continue

            module = os.path.splitext(os.path.basename(script))[0]
            module = string.translate(module, to_module)
            cmdopt=self.distribution.command_options
            if (cmdopt.has_key('install') and
                cmdopt['install'].has_key('prefix')):
                prefix = cmdopt['install']['prefix'][1]
                version = '%d.%d'%sys.version_info[:2]
                prefix = '''
import sys
sys.path.insert(1, "%s/lib/python%s/site-packages")
'''%(prefix, version)
            else:
                prefix = ''
            script_vars = {
                'python': os.path.normpath(sys.executable),
                'package': self.package_name,
                'module': module,
                'prefix': prefix,
            }

            self.announce("creating %s" % outfile)
            file = open(outfile, 'w')

            try:
                if sys.platform == "win32":
                    file.write('@echo off\n'
                        'if NOT "%%_4ver%%" == "" "%(python)s" -O -c "from %(package)s.scripts.%(module)s import run; run()" %%$\n'
                        'if     "%%_4ver%%" == "" "%(python)s" -O -c "from %(package)s.scripts.%(module)s import run; run()" %%*\n'
                        % script_vars)
                else:
                    file.write('#! %(python)s -O\n%(prefix)s'
                        'from %(package)s.scripts.%(module)s import run\n'
                        'run()\n'
                        % script_vars)
            finally:
                file.close()
                os.chmod(outfile, 0755)


class build_scripts_roundup(build_scripts_create):
    package_name = 'roundup'


def scriptname(path):
    """ Helper for building a list of script names from a list of
        module files.
    """
    script = os.path.splitext(os.path.basename(path))[0]
    script = string.replace(script, '_', '-')
    if sys.platform == "win32":
        script = script + ".bat"
    return script



#############################################################################
### Main setup stuff
#############################################################################

def main():
    # build list of scripts from their implementation modules
    roundup_scripts = map(scriptname, glob('roundup/scripts/[!_]*.py'))

    # template munching
    packagelist = [
        'roundup',
        'roundup.cgi',
        'roundup.cgi.PageTemplates',
        'roundup.cgi.TAL',
        'roundup.cgi.ZTUtils',
        'roundup.backends',
        'roundup.scripts'
    ]
    installdatafiles = [
        ('share/roundup/cgi-bin', ['cgi-bin/roundup.cgi']),
    ]

    # install man pages on POSIX platforms
    if os.name == 'posix':
        installdatafiles.append(('man/man1', ['doc/roundup-admin.1',
            'doc/roundup-mailgw.1', 'doc/roundup-server.1']))

    # add the templates to the data files lists
    from roundup.init import listTemplates
    templates = [t['path'] for t in listTemplates('templates').values()]
    for tdir in templates:
        # scan for data files
        for idir in '. detectors html'.split():
            idir = os.path.join(tdir, idir)
            tfiles = []
            for f in os.listdir(idir):
                if f.startswith('.'):
                    continue
                ifile = os.path.join(idir, f)
                if os.path.isfile(ifile):
                    tfiles.append(ifile)
            installdatafiles.append(
                (os.path.join('share', 'roundup', idir), tfiles)
            )

    # perform the setup action
    from roundup import __version__
    setup(
        name = "roundup",
        version = __version__,
        description = "Roundup is a simple-to-use and -install "\
            "issue-tracking system with command-line, web and e-mail "\
            "interfaces.",
        long_description =
'''Roundup is a simple-to-use and -install issue-tracking system with
command-line, web and e-mail interfaces. It is based on the winning design
from Ka-Ping Yee in the Software Carpentry "Track" design competition.

0.6.11 is a SECURITY FIX release of Roundup. All users are encouraged
to upgrade immediately.
''',
        author = "Richard Jones",
        author_email = "richard@users.sourceforge.net",
        url = 'http://roundup.sourceforge.net/',
        download_url = 'http://sourceforge.net/project/showfiles.php?group_id=31577',
        packages = packagelist,
        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Environment :: Web Environment',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: Python Software Foundation License',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Topic :: Communications :: Email',
            'Topic :: Office/Business',
            'Topic :: Software Development :: Bug Tracking',
        ],

        # Override certain command classes with our own ones
        cmdclass = {
            'build_scripts': build_scripts_roundup,
        },
        scripts = roundup_scripts,

        data_files =  installdatafiles
    )

if __name__ == '__main__':
    main()

# vim: set filetype=python ts=4 sw=4 et si
