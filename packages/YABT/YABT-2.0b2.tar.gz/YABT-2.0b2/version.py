"""Module to retrieve version information about the repository"""
from __future__ import with_statement
import binascii
import re
import os
import string

repository = None
info = None

try:
    from mercurial import hg, context, repo, node, ui
except ImportError:
    stripchars = string.whitespace + "+"
    nid = os.popen("hg identify --id").read().strip(stripchars)
    rev = os.popen("hg identify --num").read().strip(stripchars)
    if nid != '' and rev != '':
        info = {'rev': rev, 'node': nid}
else:
    try:
        repository = hg.repository(ui.ui(), '.')
    except repo.RepoError:
        pass
    else:
        ctx = context.changectx(repository)
        info = {'rev': ctx.rev(), 'node': binascii.hexlify(ctx.node())}

def getVersion(bv):
    global info
    if not bv.endswith(".dev"):
        # This is a release version
        return bv
    if info is not None:
        # We have repository information so let's use it
        return "%s-r%s-%s" % (bv, info['rev'], info['node'][:12])
    if os.path.isdir(".hg"):
        # Appears to be a repository but can't find mercurial
        return "%s-rUnknown" % bv
    if os.path.isfile("PKG-INFO"):
        # This doesn't seem to exist in mercurial, assume release
        # Try and use PKG-INFO
        with open('PKG-INFO') as f:
            pattern = re.compile('^Version:\s+(\S+)')
            for line in f:
                mo = pattern.match(line)
                if mo is not None:
                    return mo.group(1)
        return bv
    return "%s-rUnknown" % bv
