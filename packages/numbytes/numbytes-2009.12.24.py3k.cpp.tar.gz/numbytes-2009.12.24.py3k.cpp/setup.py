import os, re, sys

## get __init__.py
ss = open(os.path.join('numbytes', 'main.py')).read().replace('from __future__ import py3k_sugar', '', 1)

## python version check
exec('\n'.join(ss.split('\n')[:8]), globals())

## load __init__
_EXTENSION = None
_SETUP = True
ss = re.compile('if 0: ## __init__ beg.*## __init__ end\n', re.S).search(ss).group().replace('if 0: ## __init__', 'if 1: ## __init__', 1)
open('numbytes/__init__.py', 'w').write(ss)
cc = compile(ss, os.path.join('numbytes', '__init__.py'), 'exec')
exec(cc, globals())
