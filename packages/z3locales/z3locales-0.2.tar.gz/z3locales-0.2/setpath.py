import os
import sys

# a bit hackish, but this allows using the z3locale package as a Zope 2
# product, it will add all dirs in the 'src' directory to the path,
# making them available as Python packages
srcpath = '%s/src' % (os.path.split(os.path.abspath(__file__))[0])
sys.path.insert(0, srcpath)

def initialize(context):
    pass
