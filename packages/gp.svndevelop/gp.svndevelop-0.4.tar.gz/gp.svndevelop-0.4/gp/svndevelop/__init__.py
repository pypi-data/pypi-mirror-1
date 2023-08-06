import zc.buildout
from subprocess import call
import os

def install(buildout=None):
    develop_dir = buildout['buildout'].get('develop-dir', os.getcwd())
    if develop_dir.startswith('~'):
        develop_dir = os.path.expanduser(develop_dir)

    develop = buildout['buildout'].get('develop', '')
    develop = [d.strip() for d in develop.split('\n') if d.strip()]

    svn_develop = buildout['buildout'].get('svn-develop', '')
    svn_develop = [d.strip() for d in svn_develop.split('\n') if d.strip()]
    svn_develop = [d.split('#egg=') for d in svn_develop]
    svn_develop = dict([(e, u) for u, e in svn_develop])

    if svn_develop and not develop:
        raise zc.buildout.UserError(
                "You can't use the svn-develop options without develop option."
                "\n\tUse the svn-extend-develop option instead."
                "\n\tSee http://pypi.python.org/pypi/gp.svndevelop/")

    svn_extend = buildout['buildout'].get('svn-extend-develop', '')
    svn_extend = [d.strip() for d in svn_extend.split('\n') if d.strip()]
    svn_extend = [d.split('#egg=') for d in svn_extend]
    svn_extend = dict([(e, u) for u, e in svn_extend])

    if svn_extend:
        for package in svn_extend:
            if not [p for p in develop if p.endswith(package)]:
                develop.append(package)

    svn_develop.update(svn_extend)

    if svn_develop:
        buildout['buildout']['svn-eggs'] = '\n'.join(svn_develop.keys())

    eggs=[]
    scan_eggs = buildout['buildout'].get('scan-eggs', False)
    if scan_eggs:
        versions = buildout['buildout'].get('versions','')
        for section in buildout.keys():
            if buildout[section].has_key('eggs'):
                for egg in buildout[section]['eggs'].split():
                    egg = egg.strip()
                    if '>' in egg or '<' in egg or '=' in egg:
                        continue
                    if egg in versions:
                        continue
                    eggs.append(egg)
            if buildout[section].has_key('recipe'):
                recipe = buildout[section]['recipe']
                if '#' in recipe:
                    recipe = recipe.split('#')[0]
                eggs.append(recipe)

    eggs = [e.strip() for e in eggs]
    for egg in eggs:
        if (egg in svn_develop or egg in os.listdir(develop_dir)) \
           and egg not in develop:
            develop.append(egg)

    for path in develop:
        if path == '.':
            continue
        if path.endswith('/'):
            dirname, package = os.path.split(path[:-1])
        else:
            dirname, package = os.path.split(path)
        p = os.path.join(develop_dir, package)
        if os.path.isdir(p):
            develop[develop.index(path)] = p
        elif not os.path.isdir(path) and not os.path.isdir(p):
            if package in svn_develop:
                url = svn_develop.get(package, None)
                if url is not None:
                    del svn_develop[package]
                    pwd = os.getcwd()
                    os.chdir(develop_dir)
                    code = call('svn co %s %s' % (url, package), shell=True)
                    os.chdir(pwd)
                    if code == 0:
                        develop[develop.index(path)] = p
                    else:
                        raise zc.buildout.UserError(
                                'Invalid svn url %s' % url)

    for package in develop:
        if os.path.isdir(os.path.join(package, '.svn')):
            call('svn up %s' % package, shell=True)

    if len(develop):
        buildout['buildout']['develop'] = '\n'.join(develop)

