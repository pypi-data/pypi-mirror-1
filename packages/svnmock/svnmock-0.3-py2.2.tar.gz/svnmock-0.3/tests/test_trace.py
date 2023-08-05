import support
from support import TODO, TestCase

if __name__ == '__main__':
    support.adjust_path()
### /Bookkeeping ###

import svnmock
from svnmock import trace, common
from svn import fs, core

class TraceTest(TestCase):
    def setUp(self):
        self.old_dispatcher = common.dispatcher
        common.dispatcher = trace.trace_call
        
    def tearDown(self):
        common.dispatcher = self.old_dispatcher

class Test_module(TraceTest):
    def test_module_takes_over_svn_namespace(self):
        import sys

        assert 'svn' in sys.modules
        assert sys.modules['svn'] is svnmock
        
class Test_tracing(TraceTest):
    def tearDown(self):
        trace.active_tracer = None

    def test_init_activates(self):
        tracer = trace.Tracer()
        tracer.make_active()
        assert trace.active_tracer is tracer
        
        tracer_new = trace.Tracer()
        assert trace.active_tracer is tracer
        
    def test_make_active(self):
        tracer = trace.Tracer()
        tracer.make_active()
        assert trace.active_tracer is tracer
        
        tracer_new = trace.Tracer()
        old = tracer_new.make_active()
        
        assert old is tracer
        assert trace.active_tracer is tracer_new
        
    def test_trace_return_call(self):
        from svnmock.trace import Returned
    
        tracer = trace.Tracer()
        tracer.make_active()
        
        core.apr_initialize()
        
        assert tracer.get_event(0) == Returned(core.apr_initialize, (), 0)
        
    def test_trace_raise_call(self):
        from svnmock.trace import Raised, Returned
        
        tracer = trace.Tracer()
        tracer.make_active()
        
        core.apr_initialize()
        try:
            pool = core.svn_pool_create(5)
        except:
            pass
            
        assert tracer.get_event(0) == Returned(core.apr_initialize, (), 0)
        
        assert tracer.get_event(1).api_func == core.svn_pool_create
        assert tracer.get_event(1).args == (5,)
        assert isinstance(tracer.get_event(1).exc, TypeError)
        
### Bookkeeping ###
if __name__ == '__main__':
    import __main__
    support.run_all_tests(__main__)
