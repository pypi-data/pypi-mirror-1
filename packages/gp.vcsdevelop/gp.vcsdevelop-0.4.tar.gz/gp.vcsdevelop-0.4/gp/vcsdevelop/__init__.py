import zc.buildout
import pip
import sys
import os

import logging

pip.__dict__['logger'] = pip.Logger(((logging.INFO, sys.stdout),))

vcs = pip.VcsSupport()

def asbool(buildout, name, default='true'):
    value = buildout['buildout'].get(name, default)
    if value == 'false':
        return False
    return True

def has_setup(dirname):
    if os.path.isfile(os.path.join(dirname, 'setup.py')):
        return True
    return False

def install(buildout=None):
    offline = asbool(buildout, 'offline', 'false')
    newest = asbool(buildout, 'newest', 'false')

    develop_dir = buildout['buildout'].get('develop-dir', os.getcwd())
    if develop_dir.startswith('~'):
        develop_dir = os.path.expanduser(develop_dir)

    if not os.path.isdir(develop_dir):
        os.makedirs(develop_dir)

    develop = buildout['buildout'].get('develop', '')
    develop = [d.strip() for d in develop.split('\n') if d.strip()]

    vcs_extend = buildout['buildout'].get('vcs-extend-develop', '')
    vcs_extend = [d.strip() for d in vcs_extend.split('\n') if d.strip()]

    if vcs_extend:
        for url in vcs_extend:
            dummy, package = url.split('#egg=')
            if not [p for p in develop if p.endswith(package)]:
                develop.append(url)

    new_develop = []
    for url in develop:
        if '+' in url and len([s for s in vcs.schemes if url.startswith(s+'+')]):
            if '#egg=' in url:
                dummy, package = url.split('#egg=')
            elif has_setup(url, 'setup.py'):
                new_develop.append(url)
                continue
            else:
                raise ValueError('Invalid url %s. You must add #egg=packagename' % url)
            source_dir = os.path.join(develop_dir, package.strip())
            if not has_setup(source_dir):
                if not offline:
                    req = pip.InstallRequirement.from_editable(url)
                    req.source_dir = source_dir
                    req.update_editable()
            new_develop.append(source_dir)
        else:
            new_develop.append(os.path.abspath(url))

    if len(new_develop):
        buildout['buildout']['develop'] = '\n'.join(new_develop)

