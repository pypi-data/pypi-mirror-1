import zc.buildout
from subprocess import call
import os
import logging

def install(buildout=None):
    develop = buildout['buildout'].get('develop', '')
    if not develop:
        return
    develop = set([d.strip() for d in develop.splitlines() if d])
    
    svn_repos = buildout['buildout'].get('svn-repos', '')
    svn_repos = [repo.strip().split('#') for repo in svn_repos.splitlines() if repo]
    svn_repos = [(name, repo) for name, repo in svn_repos if name in develop] #filter out repos not in develop
    if not svn_repos:
        return
    
    offline = buildout['buildout']['offline'] == 'true'
    newest = buildout['buildout']['newest'] == 'true'
    if offline and newest:
        logging.error("In offline mode, can't update or get subversion checkouts, some may be missing")
        return
    
    base = buildout['buildout']['directory']
    for name, repo in svn_repos:
        path = os.path.join(base, name)
        if os.path.isdir(path) and newest:
            logging.info("Updating %s" % name)
            assert 0 == call(['svn', 'up', path])
        if not os.path.isdir(path):
            logging.info("Checking out %s" % name)
            assert 0 == call(['svn', 'co', repo, path])
