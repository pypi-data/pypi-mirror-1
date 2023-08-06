##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Install packages as eggs

$Id: egg.py 72431 2007-02-07 23:43:36Z jim $
"""

import logging
import os
import pkg_resources
import re
import sys

import zc.buildout.easy_install

class Eggs(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        links = options.get('find-links',
                            buildout['buildout'].get('find-links'))
        if links:
            links = links.split()
            options['find-links'] = '\n'.join(links)
        else:
            links = ()
        self.links = links

        index = options.get('index', buildout['buildout'].get('index'))
        if index is not None:
            options['index'] = index
        self.index = index

        options['eggs-directory'] = buildout['buildout']['eggs-directory']
        options['_e'] = options['eggs-directory'] # backward compat.
        options['develop-eggs-directory'
                ] = buildout['buildout']['develop-eggs-directory']
        options['_d'] = options['develop-eggs-directory'] # backward compat.
        
        assert options.get('unzip') in ('true', 'false', None)

        python = options.get('python', buildout['buildout']['python'])
        options['executable'] = buildout[python]['executable']

    def working_set(self, extra=()):
        """Separate method to just get the working set

        This is intended for reuse by similar recipes.
        """
        options = self.options

        distributions = [
            r.strip()
            for r in options.get('eggs', self.name).split('\n')
            if r.strip()]
        orig_distributions = distributions[:]
        distributions.extend(extra)

        if self.buildout['buildout'].get('offline') == 'true':
            ws = zc.buildout.easy_install.working_set(
                distributions, options['executable'],
                [options['develop-eggs-directory'], options['eggs-directory']]
                )
        else:
            ws = zc.buildout.easy_install.install(
                distributions, options['eggs-directory'],
                links = self.links,
                index = self.index, 
                executable = options['executable'],
                always_unzip=options.get('unzip') == 'true',
                path=[options['develop-eggs-directory']],
                newest=self.buildout['buildout'].get('newest') == 'true',
                )

        return orig_distributions, ws

    def install(self):
        reqs, ws = self.working_set()
        return ()

    update = install

class Scripts(Eggs):

    def __init__(self, buildout, name, options):
        super(Scripts, self).__init__(buildout, name, options)

        options['bin-directory'] = buildout['buildout']['bin-directory']
        options['_b'] = options['bin-directory'] # backward compat.

        self.extra_paths = [
            os.path.join(buildout['buildout']['directory'], p.strip())
            for p in options.get('extra-paths', '').split('\n')
            if p.strip()
            ]
        if self.extra_paths:
            options['extra-paths'] = '\n'.join(self.extra_paths)

    parse_entry_point = re.compile(
        '([^=]+)=(\w+(?:[.]\w+)*):(\w+(?:[.]\w+)*)$'
        ).match
    def install(self):
        reqs, ws = self.working_set()
        options = self.options

        scripts = options.get('scripts')
        if scripts or scripts is None:
            if scripts is not None:
                scripts = scripts.split()
                scripts = dict([
                    ('=' in s) and s.split('=', 1) or (s, s)
                    for s in scripts
                    ])

            for s in options.get('entry-points', '').split():
                parsed = self.parse_entry_point(s)
                if not parsed:
                    logging.getLogger(self.name).error(
                        "Cannot parse the entry point %s.", s)
                    raise zc.buildout.UserError("Invalid entry point")
                reqs.append(parsed.groups())

            return scripts__(
                reqs, ws, options['executable'],
                options['bin-directory'],
                scripts=scripts,
                extra_paths=self.extra_paths,
                interpreter=options.get('interpreter'),
                initialization=options.get('initialization', ''),
                arguments=options.get('arguments', ''),
                dependent_scripts=asbool(options.get('dependent_scripts',True))
                )

        return ()

    update = install

Egg = Scripts

def asbool(value):
    value = str(value)
    if value.strip().lower() in ['1','true']:
        return True
    elif value.strip().lower() in ['0','false']:
        return False
    else: 
        raise Exception("Unrecognised option %s for bool"% value)


py_script_template = '''\
#!%(python)s
import sys, os
    
sys.path[0:0] = [
  %(path)s,
  os.getcwd(),
  ]

_interactive = True
if len(sys.argv) > 1:
    import getopt
    _options, _args = getopt.getopt(sys.argv[1:], 'ic:')
    _interactive = False
    for (_opt, _val) in _options:
        if _opt == '-i':
            _interactive = True
        elif _opt == '-c':
            exec _val
            
    if _args:
        sys.argv[:] = _args
        execfile(sys.argv[0])

if _interactive:
    import code
    code.interact(banner="", local=globals())
'''

def scripts__(reqs, working_set, executable, dest,
            scripts=None,
            extra_paths=(),
            arguments='',
            interpreter=None,
            initialization='',
            launcher=None,
            dependent_scripts=False
            ):
    path = [dist.location for dist in working_set]
    path.extend(extra_paths)
    path = repr(path)[1:-1].replace(', ', ',\n  ')
    generated = []

    if isinstance(reqs, str):
        raise TypeError('Expected iterable of requirements or entry points,'
                        ' got string.')

    if initialization:
        initialization = '\n'+initialization+'\n'

    entry_points = []
    if dependent_scripts:
        requirements = [x[1][0] for x in working_set.entry_keys.items()]
    else:
        requirements = []
    
    for req in reqs:
        if req not in requirements:
            requirements.append(req)
    for req in requirements:
        if isinstance(req, str):
            req = pkg_resources.Requirement.parse(req)
            dist = working_set.find(req)
            for name in pkg_resources.get_entry_map(dist, 'console_scripts'):
                entry_point = dist.get_entry_info('console_scripts', name)
                entry_points.append(
                    (name, entry_point.module_name,
                     '.'.join(entry_point.attrs))
                    )
        else:
            entry_points.append(req)

    for name, module_name, attrs in entry_points:
        if name.startswith('easy_install'):
            continue
        if scripts is not None:
            sname = scripts.get(name)
            if sname is None:
                continue
        else:
            sname = name

        sname = os.path.join(dest, sname)
        try:
            generated.extend(
                zc.buildout.easy_install._script(module_name, attrs, path,
                                                 sname, executable, arguments,
                                                 initialization, False)
                )
        except TypeError: # too many args (< zc.buildout 1.2.1)
            generated.extend(
                zc.buildout.easy_install._script(module_name, attrs, path,
                                                 sname, executable, arguments,
                                                 initialization)
                )

    if interpreter:
        sname = os.path.join(dest, interpreter)
        generated.extend(_pyscript(path, sname, executable, launcher))

    return generated

def _pyscript(path, dest, executable, launcher):
    generated = []
    script = dest
    if sys.platform == 'win32':
        script+='-script'
    if launcher:
        dest += '.buildout'

    contents = py_script_template % dict(
        python = executable,
        path = path,
        )
    changed = not (os.path.exists(dest) and open(dest).read() == contents)

    if sys.platform == 'win32':
        # generate exe file and give the script a magic name:
        exe = script + '.exe'
        open(exe, 'wb').write(
            pkg_resources.resource_string('setuptools', 'cli.exe')
            )
        generated.append(exe)
    elif launcher:
        exe = script
        open(exe, 'wb').write(
            open(launcher, 'rb').read()
        )
        generated.append(exe)
        try:
            os.chmod(exe,0755)
        except (AttributeError, os.error):
            pass
        logging.getLogger('buildout').error(
                        "Generated launcher %r.", exe)


    if changed:
        open(dest, 'w').write(contents)
        try:
            os.chmod(dest,0755)
        except (AttributeError, os.error):
            pass
        logging.getLogger('buildout').info(
            "Generated interpreter %r.", script)

    generated.append(dest)
    return generated
