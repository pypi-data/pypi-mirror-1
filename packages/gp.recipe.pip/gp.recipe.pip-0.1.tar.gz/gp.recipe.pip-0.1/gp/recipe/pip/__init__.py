# -*- coding: utf-8 -*-
"""Recipe pip"""
import zc.buildout.easy_install
from zc.recipe.egg import Scripts
from subprocess import call
from copy import deepcopy
from os.path import join
from pip import pypi_url
import glob
import sys
import os

PYTHON = 'python%s' % sys.version[0:3]

def to_list(value):
    value = value.split('\n')
    value = [v.strip() for v in value]
    value = [v for v in value if v]
    return value

def get_executable(part_dir):
    for bin in ('python', PYTHON, 'Python.exe', '%s.exe' % PYTHON.title()):
        executable = join(part_dir, 'bin', bin)
        if os.path.isfile(executable):
            break
    return executable

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

    def pip_install(self, part_dir, src_dir, extra_args):
        """Installer"""
        print extra_args
        args = ['install',
                '-i', self.buildout['buildout'].get('index', pypi_url),
                '-E', part_dir,
                '--log', '%s-log.txt' % self.name,
                '-b', join(part_dir, 'build'),
                '--src', src_dir,
               ]
        if 'find-links' in self.buildout['buildout']:
            for l in to_list(self.buildout['buildout']['find-links']):
                args.extend(['-f', l])

        indexes = to_list(self.options.get('indexes', ''))
        for o in indexes:
            args.append('--install-option=%s' % o)

        install_options = to_list(self.options.get('install-options', ''))
        for o in install_options:
            args.append('--install-option=%s' % o)


        include_dir = join(part_dir, 'include', PYTHON)
        executable = get_executable(part_dir)

        # try to use venv executable if already avalaible
        if os.path.isfile(executable):
            cmd = [executable, '-c']
        else:
            cmd = [sys.executable, '-c']
        cmd.append('"from pip import main; main(%r)"' % (args+extra_args,))

        env = os.environ.copy()
        env.update({
             'PYTHONPATH': ':'.join(sys.path),
             'CFLAGS': '-I%s' % include_dir,
             'LDFLAGS': '-I%s' % include_dir,
             'PIP_DOWNLOAD_CACHE': self.buildout['buildout'].get('download-cache')
             })

        if sys.platform in ('darwin',):
            # We compile Universal if we are on a machine > 10.3
            major_version = int(os.uname()[2].split('.')[0])
            if major_version > 7:
                isysroot = glob.glob('/Developer/SDKs/MacOSX10*')[-1]
                env.update({
                    'CFLAGS' : "-arch ppc -arch i386 -isysroot %s -O2 -I%s" % (isysroot, include_dir),
                    'LDFLAGS' : "-arch ppc -arch i386 -isysroot %s -I%s" % (isysroot, include_dir),
                    'MACOSX_DEPLOYMENT_TARGET' : "10.5" in isysroot and "10.5" or "10.4"
                    })

        code = call(' '.join(cmd), shell=True, env=env)
        if code != 0:
            raise RuntimeError('An error occur during pip installation. See %s-log.txt' % self.name)

    def install(self):
        part_dir = join(self.buildout['buildout']['parts-directory'],
                        self.options.get('venv', 'pip'))
        src_dir = self.options.get('sources-directory',
                                   join(self.buildout['buildout']['directory'], 'src'))

        editables = [('-e', e) for e in to_list(self.options.get('editables', ''))]
        for e in editables:
            self.pip_install(part_dir, src_dir, e)
        for i in to_list(self.options.get('install', '')):
            self.pip_install(part_dir, src_dir, [i])

        site_packages = glob.glob(join(part_dir, 'lib', '*', 'site-packages'))[0]
        executable = get_executable(part_dir)

        egg_infos = glob.glob(join(site_packages, '*.egg-info'))
        eggs = [os.path.basename(p) for p in glob.glob(join(src_dir, '*'))]
        versions = []
        for info in egg_infos:
            info = os.path.basename(info)
            name, ver, r = info.split('-', 2)
            eggs.append(name)
            versions.append((name, ver))

        _options = self.buildout['buildout'].copy()
        self.buildout['buildout']['develop-eggs-directory'] = site_packages
        self.buildout['buildout']['executable'] = executable
        zc.buildout.easy_install.default_versions(dict(versions))

        options = {}
        for k in self.options:
            options[k] = self.options[k]

        options['eggs'] = '\n'.join(eggs)

        extra_paths = glob.glob(join(src_dir, '*'))

        eggs_dir = self.buildout['buildout']['eggs-directory']
        extra_paths.extend('\n'.join([p for p in sys.path if p.startswith(eggs_dir)]))
        options['extra-paths'] = '\n'.join([p for p in sys.path if p.startswith(eggs_dir)])

        egg = Scripts(self.buildout, self.name, options)
        egg.install()

        for k in _options:
            self.buildout['buildout'][k] = _options[k]
        versions = self.buildout['buildout'].get('versions')
        if versions:
            zc.buildout.easy_install.default_versions(dict(self.buildout[versions]))

        return tuple()

    update = install

