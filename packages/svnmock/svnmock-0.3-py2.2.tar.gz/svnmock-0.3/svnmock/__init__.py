import sys

__all__ = ['repos', 'fs', 'core', 'ra', 'wc', 'client', 'delta']

if 'svn' in sys.modules:
    if sys.modules['svn'] is not sys.modules['svnmock']:
        raise RuntimeError("module 'svn' already exists in sys.modules; cannot take over namespace")
    
# We import these first, since they need the real svn.* modules
# in order to know which functions/constants to emulate
from svnmock import *

# We need a default dispatcher
import svnmock.mock

# Take over the svn.* namespace so that modules calling that code
# get redirected to us
sys.modules['svn'] = sys.modules['svnmock']
