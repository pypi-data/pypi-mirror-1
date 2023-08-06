#!/usr/bin/env python
import os
import httprpclib

cfg = os.path.join(os.path.dirname(__file__), 'reviewboard.cfg')
rpc = httprpclib.ServerProxy('http://demo.review-board.org/', cfg)
print rpc.get_repositories()
print rpc.get_groups()
