import doctest
import sys

def install_option(option, after_unload=None):
    if isinstance(option, basestring):
        if option not in doctest.OPTIONFLAGS_BY_NAME:
            raise ValueError(
                "Unknown option: %r" % option)
        option = doctest.OPTIONFLAGS_BY_NAME[option]
    frame = _find_doctest_frame()
    test = frame.f_locals['test']
    dt_self = frame.f_locals['self']
    for example in test.examples:
        example.options.setdefault(option, 1)
    if after_unload:
        _add_after_unload(dt_self, after_unload)

def _find_doctest_frame():
    import sys
    frame = sys._getframe(1)
    while frame:
        l = frame.f_locals
        if 'BOOM' in l:
            # Sign of doctest
            return frame
        frame = frame.f_back
    raise LookupError(
        "Could not find doctest (only use this function *inside* a doctest)")
    
def _add_after_unload(dt_self, after_unload):
    def finish():
        _del_module(after_unload)
    _add_doctest_finish(dt_self, finish)

def _del_module(name):
    import sys
    del sys.modules[name]
    if '.' not in name:
        return
    package, module = name.rsplit('.', 1)
    package_mod = sys.modules[package]
    delattr(package_mod, module)

class _add_doctest_finish(object):
    def __init__(self, dt_self, finish_func):
        self.dt_self = dt_self
        self.prev_func = dt_self._DocTestRunner__record_outcome
        dt_self._DocTestRunner__record_outcome = self
        self.finish_func = finish_func
    def __call__(self, *args, **kw):
        self.finish_func()
        self.dt_self._DocTestRunner__record_outcome = self.prev_func
        return self.prev_func(*args, **kw)        
