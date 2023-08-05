import zc.buildout
from subprocess import call
import os

def install(buildout=None):
    develop_dir = buildout['buildout'].get('develop-dir', '.')
    if develop_dir.startswith('~'):
        develop_dir = os.path.expanduser(develop_dir)

    develop = buildout['buildout'].get('develop', '')
    develop = [d.strip() for d in develop.split('\n') if d.strip()]

    svn_develop = buildout['buildout'].get('svn-develop', '')
    svn_develop = [d.strip() for d in svn_develop.split('\n') if d.strip()]
    svn_develop = [d.split('#egg=') for d in svn_develop]
    svn_develop = dict([(e, u) for u, e in svn_develop])

    for package in svn_develop:
        if package not in develop:
            develop.append(package)

    for package in develop:
        if not os.path.isdir(package):
            p = os.path.join(develop_dir, package)
            if os.path.isdir(p):
                develop[develop.index(package)] = p
            else:
                url = svn_develop.get(package, None)
                if url is not None:
                    del svn_develop[package]
                    code = call('svn co %s %s' % (url, package), shell=True)
                    if code != 0:
                        raise zc.buildout.UserError(
                                'Invalid svn url %s' % url)

    if len(develop):
        buildout['buildout']['develop'] = '\n'.join(develop)

