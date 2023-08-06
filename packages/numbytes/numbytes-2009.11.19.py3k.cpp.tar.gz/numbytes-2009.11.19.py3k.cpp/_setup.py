import os, sys
ss = open(os.path.join("asciiporn", "__init__.py")).read() ## get __init__.py
exec("\n".join(ss.split("\n")[:8]), globals()) ## python version check

## load __init__
_README = open("README.asciiporn").read()
_IMPORT_EXTENSION = None
_SETUP = True
cc = compile(ss, os.path.join("asciiporn", "__init__.py"), "exec")
exec(cc, globals())

