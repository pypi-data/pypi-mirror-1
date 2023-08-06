"""
EggFreezer creates single-file installers for an EGG distribution, along with
all dependencies, which can be used without network access.

The result is a .py script which bootstraps a virtualenv and installs the
requirements that have been "frozen".

Multi-platform "universal" installers can be created by adding extra platform
identifiers with the --platform command-line option. Note that binary eggs
are not too portable, see http://philikon.wordpress.com/2008/06/26/is-there-a-point-to-distributing-egg-files/ 
for more details.

This software is licensed under the terms of the MIT license.
Questions, comments or whatever can be directed at the distutils-sig mailing
list.

Usage: eggfreezer [OPTIONS] [requirements ...]

Options:
  -h, --help            show this help message and exit
  -i INDEX_URL, --index-url=INDEX_URL
                        Use this index to locate distributions instead of PyPI
  -p PLATFORMS, --platform=PLATFORMS
                        Add binary eggs for this platform (may be used several
                        times
  -f FIND_LINKS, --find-links=FIND_LINKS
                        Try to locate distributions in here too
  -o OUTPUT, --output=OUTPUT
                        Prefix of the resulting single-file installer
  --as-helper           This is used internally by eggfreezer
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
                          resource_filename, find_distributions, get_platform
from setuptools.package_index import PackageIndex, Environment

#TODO: [ ] Support dev snapshots. Currently if a requirement has a ==dev version
#          it will tried to be downloaded when executing the resulting script.
#      [ ] Support creating *reliable* "universal" installers with binary eggs for multiple platforms.

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

    def get_extra_binaries(self, requirements, extra_platforms):
        tempdir = os.path.join(self.tempdir, '.binary_extra')
        os.makedirs(tempdir)
        if sys.argv[0].endswith('.py'):
            executable = [sys.executable, sys.argv[0]]
        else:
            executable = sys.argv[:1]
        common_args = executable
        common_args.extend(['-o', tempdir, '-i', self.index_url, '--as-helper'])
        for l in self.find_links:
            common_args.extend(['-f', l])
        for platform in extra_platforms:
            for dist in self.get_dependencies(requirements):
                if dist.platform:
                    req_str = str(dist.as_requirement())
                    args = common_args + ['-p', platform, req_str]
                    env = os.environ.copy()
                    status = subprocess.call(args, env=env)
                    if status != 0:
                        raise RuntimeError("Process exited with status %d" %
                                           status)
        return find_distributions(tempdir)

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
    easy_install = join(
        home_dir,
        sys.platform == 'win32' and 'Scripts' or 'bin',
        'easy_install'
        )
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
        is_win = sys.platform == 'win32'
        activate = join(home_dir, is_win and 'Scripts' or 'bin', 'activate')
        if is_win:
            print "You can activate it by executing: '" + activate + "'"
        else:
            print "You can activate it by typing: 'source " + activate +"'"
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
# It creates an isolated virtualenv and installs inside the following eggs:
#
%(egg_list)s
#
# With support for the following platforms
#
%(platform_list)s
#
"""

def freeze_eggs(fname, requirements, gatherer=None, extra=[],
                extra_platforms=[]):
    if gatherer is None:
        gatherer = RequirementGatherer()
    py_version = gatherer.get_py_version(requirements)
    fname = "%s-py%s.py" % (fname, py_version)
    dists = list(gatherer.get_dependencies(requirements))
    bin_dists = list(gatherer.get_extra_binaries(requirements, extra_platforms))
    bin_eggs = [d.location for d in bin_dists]
    data = gatherer.get_tarfile(requirements, bin_eggs + extra).getvalue()
    data = data.encode('zlib').encode('base64')
    egg_ball = ball_tpl % data

    output = virtualenv.create_bootstrap_script(bootstrap_tpl % locals())
    output = '\n'.join(_remove_header(output.splitlines()))
    egg_list = '\n'.join(["#     " + d.egg_name() for d in (dists + bin_dists)])
    platforms = extra_platforms + [get_platform()]
    platform_list = '\n'.join(["#     " + p for p in platforms])
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

parser = OptionParser(usage="%prog [OPTIONS] [requirements ...]")
parser.add_option("-i", "--index-url",
                  dest="index_url",
                  default="http://pypi.python.org/simple",
                  help="Use this index to locate distributions instead of PyPI",
                  )
parser.add_option("-p", "--platform",
                  dest="platforms",
                  action="append",
                  default=[],
                  help="Add binary eggs for this platform (may be used several"\
                       " times",
                  )
parser.add_option("-f", "--find-links",
                  dest="find_links",
                  action="append",
                  default=[],
                  help="Try to locate distributions in here too",
                  )
parser.add_option("-o", "--output",
                  dest="output",
                  default=None,
                  help="Prefix of the resulting single-file installer",
                  )
parser.add_option("", "--as-helper",
                  dest="as_helper",
                  action="store_true",
                  default=False,
                  help="This is used internally by eggfreezer",
                  )

def main(argv=None):
    opts, args = parser.parse_args(argv)
    if opts.as_helper:
        return helper(opts, args)
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
    fname = freeze_eggs(
        opts.output, requirements, gatherer, [setuptools], opts.platforms
        )
    print "Succesfully froze all dependencies into " + fname

def helper(opts, requirements):
    """
    A helper to fetch platform dependent distributions without messing up the
    original python environment.
    """
    index =  PackageIndex(opts.index_url)
    index.platform = opts.platforms[0]
    index.add_find_links(opts.find_links)
    for requirement in requirements:
        requirement = _ensure_requirement(requirement)
        dist = index.fetch_distribution(requirement, opts.output)
        if dist.platform != index.platform:
            raise RuntimeError("Could not locate binary egg %s for %s" %
                               (dist, index.platform))

    
    

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
