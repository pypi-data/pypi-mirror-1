from types import FunctionType

from svnmock import common

_sentinal = object()
active_session = None

_errors = {	"no active session":
				"svnmock.mock.active_session must be a MockSession",
			"out of commands":
				"too many API functions called (last: %s)",
			"bad func":
				"expected function %s, got function %s",
			"bad args":
				"expected function arguments %s, got %s",
			"emulation failure":
				"Failed to emulate function %s.%s",
			"bad call":
				"bad call: function %s, args %s",
			"empty session":
				"the MockSession object is empty",
			"empty container":
				"the %s object is empty",
            "bad subclass":
                "Incomplete %s subclass: %s" }
				
class MockError(Exception):
	def __init__(self, error_code, *args):
		Exception.__init__(self, error_code, *args)
		
		self.message = _errors[error_code] % args
		self.error_code = error_code
		
	def __str__(self):
		return self.message
		
class Return(object):
	def __init__(self, api_func, args):
		self.api_func = api_func
		self.args = args
		
	def __eq__(self, other):
		if self.__class__ is not other.__class__:
			return False
		return self.api_func is other.api_func and self.args == other.args
		
	def __ne__(self, other):
		return not self == other
		
	def __str__(self):
		return "Return<func=%s, args=%s>" % (self.api_func, self.args)
		
	__repr__ = __str__
	
class FrozenState(object):
	def __init__(self, cls, state, thawer=None):
		self._cls = cls
		self._state = state
		self._thawer = thawer
		
	def freeze(self):
		return self
		
	def thaw(self):
		if self._thawer is None:
			return self._cls._thaw(self._state)
		else:
			return self._thawer(self._cls, self._state)
		
	def __hash__(self):
		return hash("%s%s%s" % (self.__class__, self._cls, self._state))

	def __eq__(self, other):
		if self.__class__ is not other.__class__:
			return False
		return self._cls is other._cls and self._state == other._state

	def __ne__(self, other):
		return not self == other
		
class State(object):
	name = "State"

	@classmethod
	def _incomplete(cls):
		raise NotImplementedError(_errors["bad subclass"] % (cls.name, cls))

	def __eq__(self, other):
		return not self != other
		
	def __ne__(self, other):
		return not self == other
		
	def __hash__(self):
		 raise TypeError('States are unhashable')
		
	def clone(self):
		self._incomplete()

	def __len__(self):
		self._incomplete()

	def reset(self):
		self._incomplete()
		
	def freeze(self):
		self._incomplete()
		
	@classmethod
	def _thaw(cls, thaw_state):
		return cls(*thaw_state)
		
class Container(State):
	name = "Container"

	def __eq__(self, other):
		if self.__class__ is not other.__class__:
			return False
		return self._states == other._states
		
	def __len__(self):
		return sum(map(len, self._states))
		
	def clone(self):
		return self.__class__([state.clone() for state in self._states])
		
	def add_command(self, *args, **kwargs):
		self._incomplete()
		
	def add_error(self, *args, **kwargs):
		self._incomplete()
		
	def add_sequence(self, state_list=[]):
		self._incomplete()
		
	def add_any_order(self, state_list=[]):
		self._incomplete()
		
	def next(self):
		self._incomplete()
		
	def __iter__(self):
		for state in self._states:
			yield state
		raise StopIteration
		
class SingleState(State):
	name = "SingleState"

	def __eq__(self, other):
		if self.__class__ is not other.__class__:
			return False
		return self.api_func is other.api_func and self.args == other.args
		
	def __len__(self):
		return 1
		
	def reset(self):
		pass
		
	def __call__(self, container, api_func, args):
		container.next()
	
		# Was the right API function called?
		if self.api_func is not api_func:
			raise MockError("bad func", self.api_func, api_func)

		# With the right params?
		if self.args != args:
			raise MockError("bad args", self.args, args)
		
class Command(SingleState):
	def __init__(self, api_func, args=list(), return_val=_sentinal):
		if not isinstance(args, FunctionType):
			args = tuple(args)

		if return_val is _sentinal:
			return_val = Return(api_func, args)
		
		self.return_val = return_val
		self.args = args
		self.api_func = api_func
		
	def __call__(self, container, api_func, args):
		super(Command, self).__call__(container, api_func, args)

		# What do we do as a finale?
		return self.return_val
		
	def clone(self):
		return Command(self.api_func, self.args, self.return_val)
		
	def freeze(self):
		state = (self.api_func, self.args, self.return_val)
		return FrozenState(self.__class__, state)
		
class Error(SingleState):
	def __init__(self, api_func, args, raise_exc):
		if not isinstance(args, FunctionType):
			args = tuple(args)
			
		self.raise_exc = raise_exc
		self.args = args
		self.api_func = api_func
		
	def __call__(self, container, api_func, args):
		super(Error, self).__call__(container, api_func, args)

		raise self.raise_exc
		
	def clone(self):
		return Error(self.api_func, self.args, self.raise_exc)
		
	def freeze(self):
		state = (self.api_func, self.args, self.raise_exc)
		return FrozenState(self.__class__, state)

class _FakeContainer(object):
	def __init__(self):
		self.next_count = 0
		
	def next(self):
		if self.next_count == 1:
			raise RuntimeError("next has already been called on this")
	
		self.next_count += 1

class AnyOrder(Container):
	def __init__(self, state_list=[]):
		for state in state_list:
			if not isinstance(state, State):
				raise TypeError("All elements in state_list must be states")
	
		self._states = list([state.clone() for state in state_list])		
		self._unused_states = list(self._states)
		self._active_state = None
		
		self._api_call_list = []
	
	def __call__(self, container, api_func, args):
		self._api_call_list.append((api_func, args))
	
		if self._active_state is not None:
			fake_cont = _FakeContainer()
		
			try:
				return_val = self._active_state(fake_cont, api_func, args)
				if fake_cont.next_count == 1:
					self._unused_states.remove(self._active_state)
					self._active_state.reset()
					self._active_state = None
					self._api_call_list = []
					if len(self._unused_states) == 0:
						container.next()
				return return_val
			except MockError:
				self._active_state.reset()
				self._active_state = None
	
		for state in self._unused_states:
			for (api_func, args) in self._api_call_list:
				fake_cont = _FakeContainer()

				try:
					return_val = state(fake_cont, api_func, args)
					if fake_cont.next_count == 1:
						self._unused_states.remove(state)
						self._api_call_list = []
						state.reset()
						if len(self._unused_states) == 0:
							container.next()
						return return_val
				except MockError:
					state.reset()
					break
			else:
				self._active_state = state
				return return_val
		
		if len(self._unused_states) == 1:
			container.next()
		raise MockError("bad call", api_func, args)
		
	def __eq__(self, other):
		if self.__class__ is not other.__class__:
			return False
		if len(self._states) != len(other._states):
			return False
		return self.freeze() == other.freeze()
		
	def next(self):
		pass
		
	def reset(self):
		self._unused_states = list(self._states)
		self._api_call_list = []
		
		for state in self._states:
			state.reset()

	def add_command(self, *args, **kwargs):
		command = Command(*args, **kwargs)
		self._states.append(command)
		return command.return_val
		
	def add_error(self, *args, **kwargs):
		error = Error(*args, **kwargs)
		self._states.append(error)
		return error
		
	def add_any_order(self, state_list=[]):
		if len(state_list):
			for state in state_list:
				if not isinstance(state, State):
					raise TypeError("All elements in state_list must be states")
		
			self._states.extend([state.clone() for state in state_list])
		return self

	def add_sequence(self, state_list=[]):
		seq = Sequence(state_list)
		self._states.append(seq)
		return seq
        
	def freeze(self):
		def freeze_states(state_list):
			states = {}
			for state in state_list:
				frozen_state = state.freeze()
				if frozen_state not in states:
					states[frozen_state] = 1
				else:
					states[frozen_state] += 1
			return states
			
		states = freeze_states(self._states)
		unused = freeze_states(self._unused_states)
		if self._active_state is None:
			active = None
		else:
			active = self._active_state.freeze()
		calls = list(self._api_call_list)

		return FrozenState(self.__class__, (states, unused, active, calls))
		
	@classmethod
	def _thaw(cls, frozen_state):
		def thaw_states(frozen_states):
			thawed_states = []
			for state, count in frozen_states.items():
				thawed = state.thaw()
				for i in range(count):
					thawed_states.append(thawed)
			return thawed_states
			
		thawed = cls()
		thawed._states = thaw_states(frozen_state[0])
		thawed._unused_states = thaw_states(frozen_state[1])
		if frozen_state[2] is None:
			thawed._active_state = None
		else:
			thawed._active_state = frozen_state[2].thaw()
		thawed._api_call_list = list(frozen_state[3])
				
		return thawed
		
class Sequence(Container):
	def __init__(self, state_list=[]):
		self._states = []
		for state in state_list:
			if isinstance(state, self.__class__):
				self._states.extend([s.clone() for s in state._states])
			elif isinstance(state, State):
				self._states.append(state.clone())
			else:
				raise TypeError("Not a State: %s" % state)

		self._index = 0
		
	def __call__(self, container, api_func, args):
		if self._index > len(self._states) - 1:
			if len(self._states) == 0:
				raise MockError("empty container", self)
			raise MockError("out of commands", api_func)
	
		return_val = self._states[self._index](self, api_func, args)
		
		if self._index >= len(self._states):
			container.next()
		return return_val
		
	def next(self):
		self._index += 1
		
	def reset(self):
		self._index = 0
		
		for state in self._states:
			state.reset()
			
	def add_command(self, *args, **kwargs):
		command = Command(*args, **kwargs)
		self._states.append(command)
		return command.return_val
		
	def add_error(self, *args, **kwargs):
		error = Error(*args, **kwargs)
		self._states.append(error)
		return error
		
	def add_sequence(self, state_list=[]):
		if len(state_list):
			for state in state_list:
				if not isinstance(state, State):
					raise TypeError("All elements in 'state_list' must be States")
					
			self._states.extend(state_list)
		return self
			
	def add_any_order(self, state_list=[]):
		ao = AnyOrder(state_list)			
		self._states.append(ao)
		return ao
			
	def freeze(self):
		return FrozenState(self.__class__, [s.freeze() for s in self._states])
		
	@classmethod
	def _thaw(cls, frozen_state):
		return cls([s.thaw() for s in frozen_state])

class MockSession(Sequence):
	def __init__(self):
		global active_session
		if active_session is None:
			active_session = self
			
		super(MockSession, self).__init__()
	
	def __call__(self, api_func, args):
		if self._index > len(self._states) - 1:
			if len(self._states) == 0:
				raise MockError("empty session")
			raise MockError("out of commands", api_func)
			
		return self._states[self._index](self, api_func, args)

	def make_active(self):
		global active_session
		
		old_session = active_session
		active_session = self
		return old_session
		
def validate(module, api_func, args):
	if not isinstance(active_session, MockSession):
		raise MockError("no active session")
	
	return active_session(api_func, args)

common.dispatcher = validate
