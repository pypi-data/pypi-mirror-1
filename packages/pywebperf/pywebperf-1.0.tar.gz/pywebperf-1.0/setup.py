#!/usr/local/bin/python

import os, string, sys, glob
from distutils.core import setup
from distutils.util import get_platform
from distutils.command.build_scripts import build_scripts

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

    def copy_scripts(self):
        """ Create each script listed in 'self.scripts'
        """
        to_module = string.maketrans('-/', '_.')

        self.mkpath(self.build_dir)
        for script in self.scripts:
            outfile = os.path.join(self.build_dir, os.path.basename(script))

            if self.dry_run:
                self.announce("would create %s" % outfile)
                continue

            self.announce("creating %s" % outfile)
            file = open(outfile, 'w')
            python = os.path.normpath(sys.executable)

            try:
                if sys.platform == "win32":
                    file.write('@echo off\n'
                        'if NOT "%%_4ver%%" == "" %s -c "from webperf.run import run; run()" %%$\n'
                        'if     "%%_4ver%%" == "" %s -c "from webperf.run import run; run()" %%*\n'
                        % python)
                else:
                    file.write('#! %s\n'
                        'from webperf.run import run\n'
                        'run()\n'
                        % python)
            finally:
                file.close()
                os.chmod(outfile, 0755)

def scriptname(path):
    """ Helper for building a list of script names from a list of
        module files.
    """
    script = os.path.splitext(os.path.basename(path))[0]
    script = string.replace(script, '_', '-')
    if sys.platform == "win32":
        script = script + ".bat"
    return script

if __name__ == '__main__':
    import webperf
    setup(
        name = 'pywebperf',
        version = webperf.__version__,
        description = 'Web Performance Testing',
        long_description = webperf.__doc__,
        maintainer = 'Richard Jones',
        maintainer_email = 'richard@mechanicalcat.net',
        url = 'http://pywebperf.sourceforge.net/',
        packages = ['webperf'],
        scripts = ['pywebperf'],
        cmdclass = {
            'build_scripts': build_scripts_create,
        },
    )

