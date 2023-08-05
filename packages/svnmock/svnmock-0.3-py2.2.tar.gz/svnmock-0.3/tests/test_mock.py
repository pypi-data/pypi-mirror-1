import support
from support import TODO, TestCase

if __name__ == '__main__':
    support.adjust_path()
### /Bookkeeping ###

from svnmock import mock, fs, core, common
from svnmock.mock import MockError, Command, MockSession, Error, AnyOrder, Sequence

# For Python 2.2
def enumerate(iterable):
    i = 0
    enum = []
    for obj in iterable:
        enum.append((i, obj))
        i += 1
    return enum

function_1 = fs.youngest_rev
function_2 = fs.revision_root
function_3 = core.apr_initialize

class MockTest(TestCase):
    def setUp(self):
        self.old_dispatcher = common.dispatcher
        common.dispatcher = mock.validate

    def tearDown(self):
        common.dispatcher = self.old_dispatcher

### Helper classes
##################
class TestState(mock.State):
    def __init__(self):
        self.next_count = 0
        self.prev_count = 0
        self.reset_count = 0

    def next(self):
        self.next_count += 1
        
    def prev(self):
        self.prev_count += 1
        
    def reset(self):
        self.reset_count += 1
        self.next_count = 0
        self.prev_count = 0
        
    def clone(self):
        return self
        
TestContainer = TestState
        
class MyError(Exception):
    pass
###################
### /Helper classes

### Helper Functions
####################
def add_command_check_return(cont, api_func, args):
    rv = cont.add_command(api_func, args)
    check_return(rv, api_func, args)
    return rv

def check_return(obj, api_func, args):
    assert isinstance(obj, mock.Return)
    assert obj.api_func is api_func
    assert obj.args == tuple(args)

def run_and_validate(api_func, args=()):
    obj = api_func(*args)
    check_return(obj, api_func, args)
    return obj

def add_and_validate(ses, api_func, args=()):
    obj = ses.add_command(api_func, args)
    check_return(obj, api_func, args)
    return obj
    
def check_command(api_func, args=()):
    args = tuple(args)

    com = Command(api_func, args)
    assert com.api_func is api_func
    assert com.args == args
    check_return(com.return_val, api_func, args)
    return com
    
#####################
### /Helper functions

class Test_Command(TestCase):
    def setUp(self):
        self.container = TestContainer()
        self.cont_next_count = 1
    
    def tearDown(self):
        assert self.container.next_count == self.cont_next_count
        assert self.container.prev_count == 0
        assert self.container.reset_count == 0

    def test_equality(self):
        # So tearDown doesn't blow up
        self.cont_next_count = 0
        
        eq_tests = [
            (Command(function_1), Command(function_1, [])),
            (Command(function_1, [None, [5, 6]]),
            Command(function_1, [None, [5, 6]])),
            ]
        
        ne_tests = [
            (Command(function_1), Command(function_1, [None])),
            (Command(function_1), Command(function_3)),
            (Error(function_1, [], Exception), Command(function_1, []))
            ]
            
        support.test_equality(eq_tests, ne_tests)
        
    def test_pass_with_args_1(self):
        obj = Command(function_1, [5, 6])(self.container, function_1, (5, 6))
        
        check_return(obj, function_1, (5, 6))

    def test_pass_with_args_2(self):
        obj = Command(function_1, (5, 6))(self.container, function_1, (5, 6))
        
        check_return(obj, function_1, (5, 6))
        
    def test_pass_wo_args(self):
        obj = Command(function_1)(self.container, function_1, ())
        
        check_return(obj, function_1, ())
        
    def test_fail_with_args(self):
        try:
            Command(function_1, [5, 6])(self.container, function_1, (5, 6, 7))
        except MockError, e:
            assert e.error_code == 'bad args'
        else:
            raise AssertionError("Failed to raise MockError")
            
    def test_fail_wo_args_1(self):
        try:
            Command(function_1)(self.container, function_1, (5, 6))
        except MockError, e:
            assert e.error_code == 'bad args'
        else:
            raise AssertionError("Failed to raise MockError")
            
    def test_fail_wo_args_2(self):
        try:
            Command(function_1)(self.container, function_2, ())
        except MockError, e:
            assert e.error_code == 'bad func'
        else:
            raise AssertionError("Failed to raise MockError")
            
    def test_returns_right_val(self):
        command = Command(function_1, return_val=7)
    
        assert 7 == command(self.container, function_1, ())
        
    def test_reset(self):
        # So tearDown doesn't blow up
        self.cont_next_count = 0
    
        # We just want to make sure it's there
        Command(function_1).reset()
        
    def test_len(self):
        # So tearDown doesn't blow up
        self.cont_next_count = 0
    
        assert len(Command(function_1)) == 1
        
    def test_freeze_thaw(self):
        # So tearDown doesn't blow up
        self.cont_next_count = 0
    
        comm = check_command(function_1, (4, 5, 6))
        f_comm = comm.freeze()

        assert f_comm == comm.freeze()
        assert comm == f_comm.thaw()
    
class Test_Error(TestCase):
    def setUp(self):
        self.container = TestContainer()
        self.cont_next_count = 1
    
    def tearDown(self):
        assert self.container.next_count == self.cont_next_count
        assert self.container.prev_count == 0
        assert self.container.reset_count == 0

    def test_equality(self):
        # So tearDown doesn't blow up
        self.cont_next_count = 0
    
        eq_tests = [
            (Error(function_1, (), Exception), Error(function_1, [], Exception)),
            (Error(function_1, (), Exception), Error(function_1, [], RuntimeError)),
            (Error(function_1, [None, [5, 6]], Exception),
            Error(function_1, [None, [5, 6]], Exception)),
            ]
        
        ne_tests = [
            (Error(function_1, [], Exception), Error(function_1, [None], Exception)),
            (Error(function_1, [], Exception), Error(function_3, [], Exception)),
            (Error(function_1, [], Exception), Command(function_1, []))
            ]
            
        support.test_equality(eq_tests, ne_tests)
        
    def test_pass_1(self):
        try:
            Error(function_1, [5, 6], MyError)(self.container, function_1, (5, 6))
        except MyError:
            pass
        else:
            raise AssertionError("Failed to raise MyError")
        
    def test_pass_2(self):
        try:
            Error(function_1, (5, 6), MyError)(self.container, function_1, (5, 6))
        except MyError:
            pass
        else:
            raise AssertionError("Failed to raise MyError")
            
    def test_fail_bad_func(self):
        try:
            Error(function_1, [5, 6], MyError)(self.container, function_2, (5, 6))
        except MockError, e:
            assert e.error_code == 'bad func'
        else:
            raise AssertionError("Failed to raise MockError")
            
    def test_fail_bad_args(self):
        try:
            Error(function_1, [5, 6], MyError)(self.container, function_1, (5, 7))
        except MockError, e:
            assert e.error_code == 'bad args'
        else:
            raise AssertionError("Failed to raise MockError")
            
    def test_reset(self):
        # So tearDown doesn't blow up
        self.cont_next_count = 0
    
        # We just want to make sure it's there
        Error(function_1, [], MyError).reset()
        
    def test_len(self):
        # So tearDown doesn't blow up
        self.cont_next_count = 0
    
        assert len(Error(function_1, [], MyError)) == 1
        
    def test_freeze_thaw(self):
        # So tearDown doesn't blow up
        self.cont_next_count = 0
    
        err = Error(function_1, (4, 5, 6), MyError)
        f_err = err.freeze()

        assert f_err == err.freeze()
        assert err == f_err.thaw()
    
class Test_AnyOrder(TestCase):
    def test_equality(self):
        eq_tests = [
            (AnyOrder([Command(function_1), Command(function_2)]),
            AnyOrder([Command(function_2), Command(function_1)])),
            ]
            
        ne_tests = [
            (AnyOrder([Error(function_1, [], Exception), Command(function_2)]),
            AnyOrder([Command(function_2), Command(function_1, [])])),
            (AnyOrder([Command(function_1), Command(function_2)]),
            AnyOrder([Command(function_2), Command(function_2), Command(function_1)])),
            ]
            
        support.test_equality(eq_tests, ne_tests)
        
    def test_pass_1(self):
        control = [
                    (function_3, (5, 6, [7]), 0),
                    (function_1, (7, 6, [5]), 0),
                    (function_3, (5, 5, 5), 1) ]
    
        ao = AnyOrder([check_command(func, args) for (func, args, _) in control])
        parent = TestContainer()
        
        def check_ao(func, args, next_count):
            val = ao(parent, func, args)
            assert parent.next_count == next_count
            assert parent.prev_count == 0
            assert parent.reset_count == 0
            check_return(val, func, args)

        for func, args, next_count in control:
            check_ao(func, args, next_count)
        
    def test_pass_2(self):
        com_a_1 = check_command(function_3)
        com_a_2 = check_command(function_1)
        
        com_b_1 = check_command(function_3)
        com_b_2 = check_command(function_2)
        
        for funcs in ((function_1, function_2), (function_2, function_1)):
            parent = TestContainer()
            seq_1 = Sequence([com_a_1, com_a_2])
            seq_2 = Sequence([com_b_1, com_b_2])
            ao = AnyOrder([seq_1, seq_2])
            
            # ao and parent get closed over
            def check_ao(func, args, next_count):
                val = ao(parent, func, args)
                assert parent.next_count == next_count
                assert parent.prev_count == 0
                assert parent.reset_count == 0
                check_return(val, func, args)

            for next_count, func in enumerate(funcs):
                check_ao(function_3, (), 0)
                check_ao(func, (), next_count)
        
    def test_fail_1(self):
        container = TestContainer()
        
        com_1 = check_command(function_3, [5, 6, [7]])
        com_2 = check_command(function_3, [7, 6, [5]])
        
        ao = AnyOrder([com_1, com_2])

        val = ao(container, function_3, (5, 6, [7]))
        assert container.next_count == 0
        assert container.prev_count == 0
        assert container.reset_count == 0
        assert isinstance(val, mock.Return)
        
        try:
            ao(container, function_3, (5, 6, 7))
        except MockError, e:
            assert e.error_code == 'bad call'
        else:
            raise AssertionError("Failed to raise MockError")
        
        # If all states in the AnyOrder have been exhausted, advance
        # our parent container
        assert container.next_count == 1
        assert container.prev_count == 0
        assert container.reset_count == 0
        
    def test_fail_2(self):
        container = TestContainer()
        
        com_1 = check_command(function_3, [5, 6, [7]])
        com_2 = check_command(function_3, [7, 6, [5]])
        com_3 = check_command(function_3, [7, [6], [5]])
        
        ao = AnyOrder([com_1, com_2, com_3])

        val = ao(container, function_3, (5, 6, [7]))
        assert container.next_count == 0
        assert container.prev_count == 0
        assert container.reset_count == 0
        check_return(val, function_3, (5, 6, [7]))
        
        try:
            ao(container, function_3, (5, 6, 7))
        except MockError, e:
            assert e.error_code == 'bad call'
        else:
            raise AssertionError("Failed to raise MockError")
        
        # If there are still available states in the AnyOrder, we don't
        # advance our parent container  
        assert container.next_count == 0
        assert container.prev_count == 0
        assert container.reset_count == 0
        
    def test_reset(self):
        com_1 = TestState()
        com_2 = TestState()
        
        ao = AnyOrder([com_1, com_2])
        
        ao.reset()
        
        for com in (com_1, com_2):
            assert com.reset_count == 1
            assert com.next_count == 0
            assert com.prev_count == 0
            
    def test_len(self):
        com_a_1 = check_command(function_3)
        com_a_2 = check_command(function_1)
        
        com_b_1 = check_command(function_3)
        com_b_2 = check_command(function_2)
        
        seq_1 = Sequence([com_a_1, com_a_2])
        seq_2 = Sequence([com_b_1, com_b_2])
        ao = AnyOrder([seq_1, seq_2])
        
        assert len(ao) == 4
        
    def test_add_command(self):
        ao = AnyOrder()
        assert len(ao) == 0
        
        rv = add_command_check_return(ao, function_1, (1, 2, 3))
        assert len(ao) == 1
        
    def test_add_error(self):
        ao = AnyOrder()
        assert len(ao) == 0
        
        ao.add_error(function_1, (1, 2, 3), MemoryError)
        assert len(ao) == 1
        
    def test_add_sequence_no_states(self):
        ao = AnyOrder()
        assert len(ao) == 0

        new_s = ao.add_sequence()
        add_command_check_return(new_s, function_1, (1, 2, 3))

        assert len(new_s) == 1
        assert len(ao) == 1

    def test_add_sequence_with_states(self):
        ao = AnyOrder()
        assert len(ao) == 0

        c1 = check_command(function_1, (1, 2, 3))
        c2 = check_command(function_2, (1, 2, 3))

        ao.add_sequence([c1, c2])

        assert len(ao) == 2

    def test_add_sequence_bad_state(self):
        ao = AnyOrder()
        assert len(ao) == 0

        c1 = check_command(function_1, (1, 2, 3))
        c2 = 5 # Oops

        try:
            ao.add_sequence([c1, c2])
        except TypeError:
            pass
        else:
            raise AssertionError("Failed to raise TypeError")

        assert len(ao) == 0
        
    def test_add_any_order_no_states(self):
        ao = AnyOrder()
        assert len(ao) == 0
        
        new_ao = ao.add_any_order()
        add_command_check_return(new_ao, function_1, (1, 2, 3))
        
        assert len(new_ao) == 1
        assert len(ao) == 1
        
    def test_add_any_order_with_states(self):
        ao = AnyOrder()
        assert len(ao) == 0
        
        c1 = check_command(function_1, (1, 2, 3))
        c2 = check_command(function_2, (1, 2, 3))
        
        ao.add_any_order([c1, c2])
        
        assert len(ao) == 2
        
    def test_add_anyordr_bad_state(self):
        ao = AnyOrder()
        assert len(ao) == 0
        
        c1 = check_command(function_1, (1, 2, 3))
        c2 = 5 # Oops
        
        try:
            ao.add_any_order([c1, c2])
        except TypeError:
            pass
        else:
            raise AssertionError("Failed to raise TypeError")
            
        assert len(ao) == 0
        
    def test_freeze_thaw(self):
        ao = AnyOrder([check_command(function_1, (1, 2, 3))])
        f_ao = ao.freeze()

        assert f_ao == ao.freeze()
        assert ao == f_ao.thaw()
    
class Test_Sequence(TestCase):
    def test_equality(self):
        def young_rev():
            return Command(function_1)
            
        def rev_root():
            return Command(function_2)
    
        eq_tests = [
            (Sequence([young_rev(), rev_root()]), Sequence([young_rev(), rev_root()])),
            
            (Sequence([young_rev(), Sequence([young_rev(), rev_root()])]),
            Sequence([young_rev(), Sequence([young_rev(), rev_root()])])),
            
            (Sequence([young_rev(), Sequence([young_rev(), rev_root()])]),
            Sequence([young_rev(), young_rev(), rev_root()])),
            ]
            
        ne_tests = [
            (Sequence([young_rev(), rev_root()]), Sequence([rev_root(), young_rev()])),
            
            (Sequence([young_rev(), rev_root()]),
            Sequence([rev_root(), rev_root(), young_rev()])),
            
            (Sequence([Error(function_1, [], Exception), Command(function_2)]),
            Sequence([Command(function_2), Command(function_1, [])])),
            ]
            
        support.test_equality(eq_tests, ne_tests)
        
    def test_fail_1(self):
        cnt = TestContainer()
        seq = Sequence()
        
        try:
            seq(cnt, function_1, ())
        except MockError, e:
            assert e.error_code == "empty container"
        else:
            raise AssertionError("Failed to raise MockError")
            
    def test_fail_2(self):
        cnt = TestContainer()
        seq = Sequence()
        seq.add_command(function_1)
        
        seq(cnt, function_1, ())
        assert cnt.next_count == 1
        
        try:
            seq(cnt, function_1, ())
        except MockError, e:
            assert e.error_code == "out of commands"
        else:
            raise AssertionError("Failed to raise MockError")
        
    def test_pass_1(self):
        ret_val = [6, 7]
        seq = Sequence([Command(function_1, return_val=v) for v in ret_val])
        
        container = TestContainer()
        for next_count, val in enumerate(ret_val):
            assert seq(container, function_1, ()) == val
            assert container.next_count == next_count
            
    def test_pass_2(self):
        com_1 = check_command(function_1)
        com_2 = check_command(function_2)
        
        for (f_1, f_2) in ((function_1, function_2), (function_2, function_1)):
            seq = Sequence([check_command(function_3), AnyOrder([com_1, com_2])])

            parent = TestContainer()
            
            def check(func, next_count):
                val = seq(parent, func, ())
                check_return(val, func, ())
                assert parent.next_count == next_count

            check(function_3, 0)
            check(f_1, 0)
            check(f_2, 1)
        
    def test_reset_1(self):
        com_1 = TestState()
        com_2 = TestState()
        
        seq = Sequence([com_1, com_2])
        
        seq.reset()
        
        assert com_1.reset_count == 1
        assert com_2.reset_count == 1
        
    def test_reset_2(self):
        # Adapted from test_pass_2
    
        com_1 = Command(function_1)
        com_2 = Command(function_2)
        
        seq = Sequence([Command(function_3), AnyOrder([com_1, com_2])])
        
        for (f_1, f_2) in ((function_1, function_2), (function_2, function_1)):
            for _ in range(0, 5):
                parent = TestContainer()
                
                def check(func, next_count):
                    val = seq(parent, func, ())
                    check_return(val, func, ())
                    assert parent.next_count == next_count

                check(function_3, 0)
                check(f_1, 0)
                check(f_2, 1)

                seq.reset()
            
    def test_reset_3(self):
        # Adapted from test_pass_1
    
        seq = Sequence([Command(function_1), Command(function_1)])
        
        for _ in range(0, 5):
            container = TestContainer()
            for next_count in (0, 1):
                val = seq(container, function_1, ())

                assert container.next_count == next_count
                check_return(val, function_1, ())
                
            seq.reset()
            
    def test_len_1(self):
        seq = Sequence([Command(function_1), Command(function_1)])
        assert len(seq) == 2
        
    def test_len_2(self):
        com_a_1 = Command(function_3)
        com_a_2 = Command(function_1)
        
        com_b_1 = Command(function_3)
        com_b_2 = Command(function_2)
        
        seq_1 = Sequence([com_a_1, com_a_2])
        seq_2 = Sequence([com_b_1, com_b_2])
        ao = AnyOrder([seq_1, seq_2])
        
        seq = Sequence([Command(function_1), ao])
        assert len(seq) == 5
        
    def test_len_3(self):
        com_a_1 = Command(function_3)
        com_a_2 = Command(function_1)
        
        com_b_1 = Command(function_3)
        com_b_2 = Command(function_2)
        
        seq_1 = Sequence([com_a_1, com_a_2])
        seq_2 = Sequence([com_b_1, com_b_2])
        
        seq = Sequence([seq_1, seq_2])
        assert len(seq) == 4
        
    def test_add_command(self):
        s = Sequence()
        assert len(s) == 0
        
        add_command_check_return(s, function_1, (1, 2, 3))
        assert len(s) == 1
        
        add_command_check_return(s, function_1, (1, 2, 3))
        assert len(s) == 2
        
    def test_add_error(self):
        s = Sequence()
        assert len(s) == 0
        
        s.add_error(function_1, (1, 2, 3), MemoryError)
        assert len(s) == 1
        
        s.add_error(function_1, (1, 2, 3), MemoryError)
        assert len(s) == 2
        
    def test_add_sequence_no_states(self):
        s = Sequence()
        assert len(s) == 0
        
        new_s = s.add_sequence()
        add_command_check_return(new_s, function_1, (1, 2, 3))
        
        assert len(new_s) == 1
        assert len(s) == 1
        
    def test_add_sequence_with_states(self):
        s = Sequence()
        assert len(s) == 0
        
        c1 = check_command(function_1, (1, 2, 3))
        c2 = check_command(function_2, (1, 2, 3))
        
        s.add_sequence([c1, c2])
        
        assert len(s) == 2
        
    def test_add_sequence_bad_state(self):
        s = Sequence()
        assert len(s) == 0
        
        c1 = check_command(function_1, (1, 2, 3))
        c2 = 5 # Oops
        
        try:
            s.add_sequence([c1, c2])
        except TypeError:
            pass
        else:
            raise AssertionError("Failed to raise TypeError")
            
        assert len(s) == 0
        
    def test_add_any_order_no_states(self):
        s = Sequence()
        assert len(s) == 0
        
        ao = s.add_any_order()
        add_command_check_return(ao, function_1, (1, 2, 3))
        
        assert len(ao) == 1
        assert len(s) == 1
        
    def test_add_any_order_with_states(self):
        s = Sequence()
        assert len(s) == 0
        
        c1 = check_command(function_1, (1, 2, 3))
        c2 = check_command(function_2, (1, 2, 3))
        
        s.add_any_order([c1, c2])
        
        assert len(s) == 2
        
    def test_add_anyorder_bad_state(self):
        s = Sequence()
        assert len(s) == 0
        
        c1 = check_command(function_1, (1, 2, 3))
        c2 = 5 # Oops
        
        try:
            s.add_any_order([c1, c2])
        except TypeError:
            pass
        else:
            raise AssertionError("Failed to raise TypeError")
            
        assert len(s) == 0
        
    def test_freeze_thaw(self):
        seq = Sequence([check_command(function_1, (1, 2, 3))])
        f_seq = seq.freeze()

        assert f_seq == seq.freeze()
        assert seq == f_seq.thaw()

class Test_MockSession(MockTest):
    def test_init_sets_active_session(self):
        s = MockSession()
        s.make_active()
        assert s is mock.active_session
        
        MockSession()
        assert s is mock.active_session
        
    def test_validate_empty_session(self):
        try:
            MockSession()("foo", [5, 6])
        except MockError, e:
            assert e.error_code == "empty session"
        else:
            raise AssertionError("Failed to raise MockError")
            
    def test_out_of_calls(self):
        s = MockSession()
        s.make_active()
        s.add_command(function_1)
        
        function_1()
    
        try:
            function_2()
        except MockError, e:
            assert e.error_code == "out of commands"
        else:
            raise AssertionError("Failed to raise MockError")
            
    def test_validate_success(self):
        ses = MockSession()
        ses.make_active()
        
        # Create testing environment
        pool = add_and_validate(ses, function_1, [None])
        scratch_pool = add_and_validate(ses, function_1, [pool])
        
        # Test
        apr_pool = function_1(None)
        apr_scratch = function_1(apr_pool)
        
        assert apr_pool == pool
        assert apr_scratch == scratch_pool
        
    def test_validate_success_wo_args(self):
        ses = MockSession()
        ses.make_active()
        
        # Create environment
        ret_val = add_and_validate(ses, function_3)
        
        # Test
        assert function_3() == ret_val
        
    def test_validate_fail_intentional(self):
        ses = MockSession()
        ses.make_active()
        
        # Create environment
        pool = ses.add_command(function_1, [None])
        ses.add_error(function_2, [pool], NotImplementedError)
        
        # Test
        apr_pool = function_1(None)
        assert apr_pool == pool
        try:
            function_2(apr_pool)
        except NotImplementedError:
            pass
        else:
            raise AssertionError("Failed to raise NotImplementedError")
            
    def test_validate_fail_bad_func(self):
        ses = MockSession()
        ses.make_active()
        
        # Create environment
        pool = ses.add_command(function_1, [None])
        ses.add_command(function_2, [pool])
        
        # Test
        apr_pool = function_1(None)
        assert apr_pool == pool
        try:
            function_1(apr_pool)
        except MockError, e:
            assert e.error_code == 'bad func'
        else:
            raise AssertionError("Failed to raise MockError")
            
    def test_validate_fail_bad_args_1(self):
        ses = MockSession()
        ses.make_active()
        
        # Create environment
        pool = ses.add_command(function_1, [None])
        ses.add_command(function_1, [pool])
        
        # Test
        apr_pool = function_1(None)
        assert apr_pool == pool 
        try:
            function_1(None)
        except MockError, e:
            assert e.error_code == 'bad args'
        else:
            raise AssertionError("Failed to raise MockError")
            
    def test_validate_fail_bad_args_2(self):
        ses = MockSession()
        ses.make_active()
        
        # Create environment
        pool_1 = add_and_validate(ses, function_1, [None])
        pool_2 = add_and_validate(ses, function_1, [pool_1])
        add_and_validate(ses, function_1, [pool_1])
        
        # Test
        apr_pool_1 = function_1(None)
        assert apr_pool_1 == pool_1
        apr_pool_2 = function_1(apr_pool_1)
        assert apr_pool_2 == pool_2
        try:
            # The correct pool would have been apr_pool_1
            assert function_1(apr_pool_2)
        except MockError, e:
            assert e.error_code == 'bad args'
        else:
            raise AssertionError("Failed to raise MockError")
            
    def test_validate_fail_bad_args_3(self):
        ses = MockSession()
        ses.make_active()
        
        # Create environment
        add_and_validate(ses, function_3)
        
        # Test
        try:
            # Correct: no arguments
            function_3(4, 5)
        except MockError, e:
            assert e.error_code == 'bad args'
        else:
            raise AssertionError("Failed to raise MockError")
            
    def test_add_any_order_pass(self):
        arg_tuples = [([5, 6, [7]], [7, 6, [5]]), ([5, 6, [7]], [7, 6, [5]])]
    
        for (args1, args2) in arg_tuples:
            ses = mock.MockSession()
            ses.make_active()
            
            com_1 = check_command(function_3, [5, 6, [7]])
            com_2 = check_command(function_3, [7, 6, [5]])
            ses.add_any_order([com_1, com_2])

            assert function_3(*args1) == com_1.return_val
            assert function_3(*args2) == com_2.return_val

            mock.active_session = None
            
    def test_add_any_order_fail(self):
        ses = mock.MockSession()
        ses.make_active()
        
        com_1 = Command(function_3, [5, 6, [7]])
        com_2 = Command(function_3, [7, 6, [5]])
        ses.add_any_order([com_1, com_2])

        assert function_3(5, 6, [7]) == com_1.return_val
        try:
            assert function_3(5, 6, 7)
        except MockError, e:
            assert e.error_code == 'bad call'
        else:
            raise AssertionError("Failed to raise MockError")
            
    def test_add_any_order_no_args(self):
        ses = mock.MockSession()
        
        add_any_order = ses.add_any_order()
        
        assert len(add_any_order) == 0
            
    def test_add_any_order_and_seq(self):
        # Taken from cypress's test_storage_svn_local
        # for part of our regression test
        
        ### Set up test environment
        #################################################
        from svnmock import repos
        
        session = mock.MockSession()
        session.make_active()
        
        self.repo_path = '/var/svn/repo';
        
        session.add_command(core.apr_initialize)
        self.pool = add_and_validate(session, core.svn_pool_create, [None])
        self.scratch = add_and_validate(session, core.svn_pool_create, [self.pool])

        self.repo = add_and_validate(session, repos.svn_repos_open, [self.repo_path, self.pool])
        self.fs = add_and_validate(session, repos.svn_repos_fs, [self.repo])
        
        self.youngest_rev = session.add_command(fs.youngest_rev, [self.fs, self.pool], 7)
        assert self.youngest_rev == 7
        
        self.head_root = add_and_validate(session, fs.revision_root, [self.fs, self.youngest_rev, self.pool])
        
        seq = []
        for path in ['foo/bar.py', 'bar/baz.py']:
            com_1 = Command(fs.node_history, [self.head_root, path, self.pool])
            check_return(com_1.return_val, fs.node_history, [self.head_root, path, self.pool])
            
            com_2 = Command(fs.history_prev, [com_1.return_val, 0, self.pool])
            check_return(com_2.return_val, fs.history_prev, [com_1.return_val, 0, self.pool])
            
            com_3 = Command(fs.history_location, [com_2.return_val, self.pool], (None, 5))
            assert com_3.return_val == (None, 5)
            
            seq.append([com_1, com_2, com_3])
            
        session.add_any_order([Sequence(s) for s in seq])
        #################################################
        
        ### The code to be tested
        #################################################
        core.apr_initialize()

        apr_pool = run_and_validate(core.svn_pool_create, (None,))
        
        apr_scratch_pool = run_and_validate(core.svn_pool_create, (apr_pool,))

        repo = run_and_validate(repos.svn_repos_open, (self.repo_path, apr_pool))
        
        repo_fs = run_and_validate(repos.svn_repos_fs, (repo,))
        
        youngest_rev = fs.youngest_rev(repo_fs, apr_pool)
        assert isinstance(youngest_rev, int)
        
        new_root = run_and_validate(fs.revision_root, (repo_fs, youngest_rev, apr_pool))
        
        for path in ['foo/bar.py', 'bar/baz.py']:
            history = run_and_validate(fs.node_history, (new_root, path, apr_pool))
            history = run_and_validate(fs.history_prev, (history, 0, apr_pool))
            
            _, rev = fs.history_location(history, apr_pool)
            assert rev == 5
            
    def test_add_sequence_no_states(self):
        ses = MockSession()
        assert len(ses) == 0
        
        new_seq = ses.add_sequence()
        add_command_check_return(new_seq, function_1, (1, 2, 3))
        
        assert len(new_seq) == 1
        assert len(ses) == 1
        
    def test_add_sequence_with_states(self):
        ses = MockSession()
        assert len(ses) == 0
        
        c1 = check_command(function_1, (1, 2, 3))
        c2 = check_command(function_2, (1, 2, 3))
        
        ses.add_sequence([c1, c2])
        
        assert len(ses) == 2
        
    def test_add_sequence_bad_state(self):
        ses = MockSession()
        assert len(ses) == 0
        
        c1 = check_command(function_1, (1, 2, 3))
        c2 = 5 # Oops
        
        try:
            ses.add_sequence([c1, c2])
        except TypeError:
            pass
        else:
            raise AssertionError("Failed to raise TypeError")
            
        assert len(ses) == 0

    def test_make_active(self):
        ses = MockSession()
        ses.make_active()

        assert mock.active_session is ses

        new_ses = MockSession()

        assert mock.active_session is ses
        assert ses is new_ses.make_active()
        assert mock.active_session is new_ses
            
    def tearDown(self):
        super(Test_MockSession, self).tearDown()
    
        mock.active_session = None

class Test_module(MockTest):
    def setUp(self):
        mock.active_session = MockSession()
        
    def tearDown(self):
        mock.active_session = None

    def test_empty_validate(self):
        mock.active_session = None
    
        try:
            mock.validate(None, "foo", [5, 6])
        except MockError, e:
            assert e.error_code == "no active session"
        else:
            raise AssertionError("Failed to raise ValueError")

    def test_add_command(self):
        mock.add_command(function_1)
        
        assert len(mock.active_session) == 1
        
    def test_add_sequence(self):
        seq = mock.add_sequence()
        
        seq.add_command(function_1)
        
        assert len(mock.active_session) == 1
        
    def test_add_any_order(self):
        ao = mock.add_any_order()
        
        ao.add_command(function_1)
        
        assert len(mock.active_session) == 1
        
    def test_add_error(self):
        mock.add_error(function_1, (), RuntimeError)
        
        assert len(mock.active_session) == 1
        
### Bookkeeping ###
if __name__ == '__main__':
    import __main__
    support.run_all_tests(__main__)
