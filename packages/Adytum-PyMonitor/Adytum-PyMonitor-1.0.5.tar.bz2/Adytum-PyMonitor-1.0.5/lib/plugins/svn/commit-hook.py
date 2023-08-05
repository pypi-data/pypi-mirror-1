#!/usr/local/bin/python

import commands
import sys
import time
from adytum.plugins.svn import convert

svnlook_bin      = '/opt/bin/svnlook'
notes_dir        = '/tmp/svncommits'
t                = time.time()
filename         = '%s/%s' % (notes_dir, t)
main_section     = 'main'
comments_section = 'status'

(script, repos, rev) = sys.argv
log = commands.getoutput('%s log -r %s %s' % (svnlook_bin, rev, repos))
author = commands.getoutput('%s author -r %s %s' % (svnlook_bin, rev, repos))
changed = commands.getoutput('%s changed -r %s %s' % (svnlook_bin, rev, repos))

p = convert.SVNConfigParser()
p.setRepository(repos)
p.setRevision(rev)
p.setAuthor(author)
p.setChanged(changed)
p.setLog(log)
p.write(filename)
