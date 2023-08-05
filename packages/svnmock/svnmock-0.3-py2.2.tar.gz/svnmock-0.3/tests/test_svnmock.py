import support
from support import TODO, TestCase

if __name__ == '__main__':
    support.adjust_path()
### /Bookkeeping ###

import svnmock

class Test_module(TestCase):
    def test_module_takes_over_svn_namespace(self):
        import sys
        
        assert 'svn' in sys.modules
        assert sys.modules['svn'] is svnmock
        
### Bookkeeping ###
if __name__ == '__main__':
    import __main__
    support.run_all_tests(__main__)
