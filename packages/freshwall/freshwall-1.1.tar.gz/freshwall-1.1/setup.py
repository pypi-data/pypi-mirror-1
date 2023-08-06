#!/usr/bin/env python

from distutils.command.build_py import build_py as _build_py
from distutils.core import setup
from subprocess import Popen, PIPE
import time

version = '1.1'

# NOTE: There is at the present time no License :: OSI Approved :: Apache 2.0.
# As the version MAY be important for determining GPLv2 compatibility or DFSG
# status, I refuse to use an unversioned license tag in its place.
classes="""
Development Status :: 5 - Production/Stable
Environment :: X11 Applications :: Gnome
Intended Audience :: End Users/Desktop
License :: OSI Approved
Operating System :: Unix
Programming Language :: Python :: 2
Programming Language :: Python :: 2.4
Programming Language :: Python :: 2.5
Programming Language :: Python :: 2.6
Topic :: Desktop Environment :: Gnome
"""
classifiers = [c.strip() for c in classes.splitlines() if c.strip()]

long_desc = """Selects a random background from the ~/.gnome2/backgrounds.xml
file (or any other file in the same format). The chosen background is then set
as the current GNOME background via gconf.

A preferences mode is also included, using the ``-p`` or ``--preferences``
option.

Version 1.1 adds a daemon mode; the daemon can be launched with ``-d`` or
``--daemon`` and shut down with ``-x`` or ``--exit-daemon``."""


def _cmd_output (*cmdline, **kwargs):
    proc = Popen(cmdline, stdout=PIPE)
    output = proc.communicate()[0]

    if 'strip' not in kwargs or kwargs['strip']:
        output = output.strip()

    return output


def install_gconf_schemas (schema_files):
    for file in schema_files:
        proc = Popen(['gconftool-2', '--install-schema-file', file])
        proc.communicate()


def get_dbus_services_path ():
    return _cmd_output('pkg-config', '--variable=session_dbus_services_dir',
                       'dbus-1')


class VersionWriter (object):
    version_py_file = 'lib/freshwall/version.py'
    version_published = version

    def write (self):
        rev = self.get_revision_tag()
        self.write_for_revision(rev)

    def get_revision_tag (self):
        try:
            rev = _cmd_output('hg', '-q', 'id')
        except Exception, e:
            rev = ''

        return rev

    def write_for_revision (self, revision):
        output = self.version_py_file

        if type(output) in (str, unicode):
            outfp = open(output, 'w')
        else:
            outfp = output

        outfp.write("version = %s\n" % repr(self.version_published))
        outfp.write("revision = %s\n" % repr(revision))
        outfp.write("build_time = %f\n" % time.time())


class build_py (_build_py):
    def run (self):
        vwriter = VersionWriter()
        vwriter.write()

        _build_py.run(self)


def do_setup ():
    setup(cmdclass={'build_py': build_py},
          name='freshwall',
          version=version,
          description='GNOME wallpaper changer',
          long_description=long_desc,
          author='Chad Daelhousen',
          author_email='release@sapphirepaw.org',
          url='http://www.sapphirepaw.org/projects/freshwall.php',
          scripts=['bin/freshwall'],
          license='Apache 2.0',
          package_dir={'': 'lib'},
          packages=['freshwall'],
          classifiers=classifiers)

def main(argv=None):
    do_setup()

if __name__ == '__main__':
    main()

