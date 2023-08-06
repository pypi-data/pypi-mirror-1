import types
def get_methods(module_items):
    '''
    e.g. call with locals()
    '''
    inspect.getmembers(object, inspect.isfunction or inspect.ismethod)
    # methods = [ name for name,method module_items if isinstance(method, types.FunctionType) ]
    methods.sort()

inspect.getmembers
inspect.isfunction
inspect.ismethod
