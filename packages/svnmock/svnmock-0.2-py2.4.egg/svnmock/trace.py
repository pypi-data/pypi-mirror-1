from svnmock import common

active_tracer = None

class Event(object):
    def __eq__(self, other):
        return not self != other
        
    def __ne__(self, other):
        return not self == other

class Returned(Event):
    def __init__(self, api_func, args, returned):
        self.api_func = api_func
        self.args = args
        self.returned = returned
        
    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return False
        return self.api_func == other.api_func \
           and self.args == other.args \
           and self.returned == other.returned
        
    def format(self):
        return (self.api_func.__name__, self.args, \
                "Returned: %s" % self.returned)
        
class Raised(Event):
    def __init__(self, api_func, args, exc):
        self.api_func = api_func
        self.args = args
        self.exc = exc
        
    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return False
        return self.api_func == other.api_func \
           and self.args == other.args \
           and self.exc == other.exc
        
    def format(self):
        return (self.api_func.__name__, self.args, "Raised: %s" % self.exc)

class Tracer(object):
    def __init__(self):
        self.events = []
        
    def trace_call(self, module, api_func, args):
        try:
            returned = getattr(module, api_func.__name__)(*args)
        except Exception, e:
            self.events.append(Raised(api_func, args, e))
            raise
        
        self.events.append(Returned(api_func, args, returned))
        return returned
        
    def get_event(self, event_no):
        return self.events[event_no]
        
    def get_events(self):
        return list(self.events)
        
    def __iter__(self):
        events = iter(self.events)
        while True:
            yield events.next()
            
    def clear(self):
        self.events.clear()
            
    def make_active(self):
        global active_tracer
        old = active_tracer
        active_tracer = self
        return old
        
    def pretty_print(self, start=0, limit=None):
        if limit is None:
            events = self.events[start:]
        else:
            if limit <= 0:
                raise ValueError("invalid literal for limit: %s" % limit)
            events = self.events[start:start + limit]
    
        for i, event in enumerate(events):
            call, args, effect = event.format()
            print "%04d: %s" % (i + start, call)
            print "      +--> Args: %s" % (args,)
            print "      +--> %s" % effect
            print
        
# Create a default instance
active_tracer = Tracer()

def trace_call(module, api_func, args):
    if active_tracer is None:
        raise RuntimeError("No active Tracer instance")
    return active_tracer.trace_call(module, api_func, args)

common.dispatcher = trace_call


# Allow users to call "methods" on the module as if they were calling them
# on the active_tracer
def pretty_print(start=0, limit=None):
    active_tracer.pretty_print(start, limit)
    
def get_event(event_no):
    return active_tracer.get_event(event_no)
    
def get_events():
    return active_tracer.get_events()
