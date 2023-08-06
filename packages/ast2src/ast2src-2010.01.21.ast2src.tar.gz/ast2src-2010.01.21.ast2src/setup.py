import os, re, sys

## get __init__
ss = open(os.path.join('ast2src', 'main.py')).read()

## python version check
exec( re.search('(?s)(.*)if 0: ######## INIT\n', ss).group(1), globals() )

## write __init__
ss = re.match('(?s).*?## END\n', ss).group().replace('if 0: ######## INIT', 'if 1: ###### INIT', 1)
open('ast2src/__init__.py', 'w').write(ss)

## load __init__
sys.modules['ast2src.setup'] = True ## setup magic
import ast2src
