#!/usr/bin/python
import os
import subprocess

def _update(location, vcs):
    os.chdir(location)
    if vcs == 'svn':
        subprocess.call('svn up', shell=True)
    else:
        subprocess.call('hg pull', shell=True)
        subprocess.call('hg up', shell=True)

def _init(url, location, vcs):
    if vcs == 'svn':
        subprocess.call('svn co %s %s' % (url, location), shell=True)
    else:
        subprocess.call('hg clone %s %s' % (url, location), shell=True)

def externals(ui, repo, node, **opts):

    node = os.path.realpath(node)
    if os.path.isdir(node):
        file = os.path.join(node, 'EXTERNALS')
    else:
        file = node

    if not os.path.exists(file):
        return

    curdir = os.path.split(file)[0]
    curwdir = os.getcwd()
    try:
        for line in open(file):
            line = line.split()
            if len(line) not in (2, 3):
                continue

            name = line[0]
            url = line[1]
            if len(line) > 2:
                vcs = line[2]
            else:
                vcs = 'hg'

            fullname = os.path.join(curdir, name)
            if os.path.exists(fullname):
                _update(fullname, vcs)
            else:
                _init(url, fullname, vcs)
    finally:
        os.chdir(curwdir)


cmdtable = {
    "externals": (externals, [], None, 'hg externals PATH')
}

