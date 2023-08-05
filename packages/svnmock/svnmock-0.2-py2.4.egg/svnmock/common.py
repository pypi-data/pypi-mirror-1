dispatcher = None

def dispatch(module, api_func, args):
    if dispatcher is None:
        raise RuntimeError("No dispatcher set")
    return dispatcher(module, api_func, args)

# This is used to build svnmock.{fs,core,repos,...}
def __build_mock_api(mod_name, globals_dict):
    module = globals_dict[mod_name]
    template = """def %s(*args): return __common.dispatch(%s, %s, args)"""

    for (name, obj) in module.__dict__.items():
        if callable(obj):
            try:
                exec (template % (name, mod_name, name)) in globals_dict
            except:
                pass
        else:
            globals_dict[name] = obj
