import os, re, sys

## get __init__
ss = open(os.path.join('pseudomethod', 'main.py')).read()

## python version check
exec('\n'.join(ss.split('\n')[:8]), globals())

## write __init__
ss = re.compile('.*## __init__ end\n', re.S).search(ss).group().replace('if 0: ## __init__', 'if 1: ## __init__', 1)
open('pseudomethod/__init__.py', 'w').write(ss)

## load __init__
sys.modules['pseudomethod.setup'] = True ## setup magic
import pseudomethod
