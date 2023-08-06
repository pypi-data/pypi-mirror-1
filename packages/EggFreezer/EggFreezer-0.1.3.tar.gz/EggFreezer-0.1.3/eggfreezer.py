"""
EggFreezer creates single-file installers for an EGG distribution along with all requirements
that can be used without network access.

The result is a .py script which bootstraps a virtualenv and installs the requirements that
have been "frozen".

Note that currently the installers it creates are platform-dependant, that is, if any of
the requirements is a platform-dependant egg it will only be installable in the same platform.
I'm more than happy to accept a patch that overcomes this limitation to support
"universal" installers :)

This software is licensed under the terms of the MIT license.
Questions, comments or whatever can be directed at the turbogears-trunk google group.


Usage: eggfreezer [OPTIONS] <requirement> [requirementN]

Options:
  -h, --help            show this help message and exit
  -i INDEX_URL, --index-url=INDEX_URL
  -f FIND_LINKS, --find-links=FIND_LINKS
  -o OUTPUT, --output=OUTPUT
"""
import datetime
import subprocess
import textwrap
import sys
import os
import shutil
import tempfile
import site
import tarfile
from optparse import OptionParser
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import virtualenv
from pkg_resources import WorkingSet, Requirement, get_distribution,\
                          resource_filename
from setuptools.package_index import PackageIndex, Environment

#TODO: [ ] Support dev snapshots. Currently if a requirement has a ==dev version
#          it will tried to be downloaded when executing the resulting script.
#      [ ] Support creating "universal" installers with binary eggs for multiple platforms.

__PACKAGE__ = 'EggFreezer'
__VERSION__ = get_distribution(__PACKAGE__).version
__AUTHOR__ = 'Alberto Valverde Gonzalez'
__COPYRIGHT__ = "Copyright 2008 " + __AUTHOR__
__LICENSE__ = "MIT"

class RequirementGatherer(object):
    def __init__(self, index_url='http://pypi.python.org/simple',
                 find_links=[]):
        self.find_links = find_links
        self.index_url = index_url
        self.tempdir = tempfile.mkdtemp()
        self.local_index = Environment([self.tempdir])
    
    def get_dependencies(self, requirements):
        self._install_in_tempdir(requirements)
        site.addsitedir(self.tempdir)
        # must instantiate index after self.tempdir is added as a sitedir
        # so distributions are picked up from there
        index = PackageIndex(self.index_url)
        return WorkingSet([]).resolve(
            map(_ensure_requirement, requirements),
            self.local_index,
            lambda r: index.fetch_distribution(r, self.tempdir)
            )

    def get_py_version(self, requirements):
        for dist in self.get_dependencies(requirements):
            if dist.py_version:
                return dist.py_version

    def get_platform(self, requirements):
        for dist in self.get_dependencies(requirements):
            if dist.platform:
                return dist.platform

    def get_tarfile(self, requirements, extra=[]):
        buffer = StringIO()
        tfile = tarfile.TarFile(mode='w', fileobj=buffer)
        for dist in self.get_dependencies(requirements):
            name = os.path.basename(dist.location)
            tfile.add(dist.location, name)
        for fname in extra:
            name = os.path.basename(fname)
            tfile.add(fname, name)
        buffer.seek(0)
        return buffer
            
    def _install_in_tempdir(self, requirements):
        env = os.environ.copy()
        env['PYTHONPATH'] = self.tempdir
        args = ['easy_install-%d.%d' % sys.version_info[:2],
                '--install-dir', self.tempdir,
                '--index-url', self.index_url,
                '--exclude-scripts',
                '--always-copy',
                '--local-snapshots-ok']
        for link in self.find_links:
            args.extend(['-f', link])
        args.extend(requirements)
        status = subprocess.call(args, env=env)
        if status != 0:
            raise RuntimeError("Process exited with status %d"%status)

    def __del__(self):
        try:
            shutil.rmtree(self.tempdir)
        except:
            pass

def _ensure_requirement(req):
    if not isinstance(req, Requirement):
        req = Requirement.parse(req)
    return req

bootstrap_tpl = """\
import tempfile, shutil
def install_setuptools(py_executable, unzip=False):
    tempdir = tempfile.mkdtemp()
    try:
        version = str(sys.version_info[0]) + '.' + str(sys.version_info[1])
        member = 'setuptools-0.6c8-py' + version + '.egg'
        EGG_BALL.extract(member, tempdir)
        setup_fn = join(tempdir, member)
        cmd = [py_executable, '-c', EZ_SETUP_PY]
        if unzip:
            cmd.append('--always-unzip')
        env = {}
        if logger.stdout_level_matches(logger.INFO):
            cmd.append('-v')
        logger.info('Using existing Setuptools egg: ' + setup_fn)
        cmd.append(setup_fn)
        if os.environ.get('PYTHONPATH'):
            env['PYTHONPATH'] = setup_fn + os.path.pathsep + os.environ['PYTHONPATH']
        else:
            env['PYTHONPATH'] = setup_fn
        logger.start_progress('Installing setuptools...')
        logger.indent += 2
        cwd = None
        if not os.access(os.getcwd(), os.W_OK):
            cwd = '/tmp'
        try:
            call_subprocess(cmd, show_stdout=False,
                            filter_stdout=filter_ez_setup,
                            extra_env=env,
                            cwd=cwd)
        finally:
            logger.indent -= 2
            logger.end_progress()
    finally:
        shutil.rmtree(tempdir)

import subprocess
from tarfile import TarFile
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

def after_install(options, home_dir):
    easy_install = join(home_dir, 'bin', 'easy_install')
    egg_dir = tempfile.mkdtemp()
    args = [easy_install, '-f', egg_dir]
    args.extend(%(requirements)r)
    try:
        logger.start_progress('Uncompressing EGGS...')
        for member in EGG_BALL.getmembers():
            EGG_BALL.extract(member, egg_dir)
        logger.end_progress()
        status = subprocess.call(args)
        logger.start_progress('Installing EGGS...')
        if status != 0:
            raise RuntimeError("Process exited with status " + str(status))
        logger.end_progress()
        print
        print "Virtual environment has been created at " + home_dir
        print "You can activate it by typing: 'source " + home_dir + "/bin/activate' on *nix"
        print "Or by executing: '" + home_dir + "/bin/activate.bat' on Windows"
    finally:
        shutil.rmtree(egg_dir)

EGG_BALL = %(egg_ball)s
"""

ball_tpl = 'TarFile(fileobj=StringIO("""%s""".decode("base64").decode("zlib")))'

header_tpl = """\
#!/usr/bin/env python%(py_version)s
#
# This is an offline installer created on %(now)s by %(creator)s.
#
# It creates an isolated virtualenv and installs the following eggs:
#
%(egg_list)s
#
"""

def freeze_eggs(fname, requirements, gatherer=None, extra=[]):
    if gatherer is None:
        gatherer = RequirementGatherer()
    py_version = gatherer.get_py_version(requirements)
    if py_version:
        fname += '-py' + py_version
    platform = gatherer.get_platform(requirements)
    if platform:
        fname += '-' + platform
    fname += '.py'
    data = gatherer.get_tarfile(requirements, extra).getvalue()
    data = data.encode('zlib').encode('base64')
    egg_ball = ball_tpl % data
    dists = gatherer.get_dependencies(requirements)

    output = virtualenv.create_bootstrap_script(bootstrap_tpl % locals())
    output = '\n'.join(_remove_header(output.splitlines()))
    egg_list = '\n'.join(["#     " + d.egg_name() for d in dists])
    creator = "%s %s. %s" % (__PACKAGE__, __VERSION__, __COPYRIGHT__)
    now = datetime.date.today().strftime("%Y-%m-%d")
    header = header_tpl  % locals()
    open(fname, 'w').write(header+output)
    return fname

def _remove_header(lines):
    skipped = False
    for line in lines:
        if not line.startswith('#') and not skipped:
            skipped = True
            yield line
        elif skipped:
            yield line

parser = OptionParser(usage="%prog [OPTIONS] <requirement> [requirementN]")
parser.add_option("-i", "--index-url",
                  dest="index_url",
                  default="http://pypi.python.org/simple",
                  )
parser.add_option("-f", "--find-links",
                  dest="find_links",
                  action="append",
                  default=[],
                  )
parser.add_option("-o", "--output",
                  dest="output",
                  default=None,
                  )

def main(argv=None):
    opts, args = parser.parse_args(argv)
    gatherer = RequirementGatherer(opts.index_url, opts.find_links)
    if not opts.output:
        print >> sys.stderr, "ERROR: Need to provide an output filename prefix"
        parser.print_help(sys.stderr)
        return -1
    requirements = args
    if not requirements:
        print >> sys.stderr, "ERROR: Need to provide at least one top level "\
                             "requierement"
        parser.print_help(sys.stderr)
        return -1
    version = str(sys.version_info[0]) + '.' + str(sys.version_info[1])
    setuptools = 'setuptools-0.6c8-py' + version + '.egg'
    setuptools = resource_filename('virtualenv', 'support-files/'+setuptools)
    fname = freeze_eggs(opts.output, requirements, gatherer, [setuptools])
    print "Succesfully froze all dependencies into " + fname


if __name__ == '__main__':
    main(sys.argv[1:])
