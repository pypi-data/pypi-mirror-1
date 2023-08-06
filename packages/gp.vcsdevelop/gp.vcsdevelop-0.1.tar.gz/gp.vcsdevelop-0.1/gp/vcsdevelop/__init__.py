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

def install(buildout=None):
    offline = asbool(buildout, 'offline', 'false')
    newest = asbool(buildout, 'newest', 'false')

    develop_dir = buildout['buildout'].get('develop-dir', os.getcwd())
    if develop_dir.startswith('~'):
        develop_dir = os.path.expanduser(develop_dir)

    if not os.path.isdir(develop_dir):
        os.makedirs(develop_dir)

    develop = buildout['buildout'].get('develop', '')
    develop = set([d.strip() for d in develop.split('\n') if d.strip()])

    vcs_extend = buildout['buildout'].get('vcs-extend-develop', '')
    vcs_extend = set([d.strip() for d in vcs_extend.split('\n') if d.strip()])

    if vcs_extend:
        for url in vcs_extend:
            dummy, package = url.split('#egg=')
            if not [p for p in develop if p.endswith(package)]:
                develop.add(url)

    new_develop = set([])
    for url in develop:
        if url.startswith('.') or url.startswith('/'):
            # dir path
            new_develop.add(os.path.abspath(url))
        else:
            try:
                dummy, package = url.split('#egg=')
            except:
                raise ValueError(url)
            source_dir = os.path.join(develop_dir, package.strip())
            if not os.path.isdir(source_dir):
                if not offline:
                    req = pip.InstallRequirement.from_editable(url)
                    req.source_dir = source_dir
                    req.update_editable()
            new_develop.add(source_dir)

    if len(new_develop):
        buildout['buildout']['develop'] = '\n'.join(new_develop)

