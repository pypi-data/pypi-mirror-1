"""The code used for monkeypatching and time measurement
"""

from zLOG import LOG, INFO
from ProfileContainer import profile_container
import time
import os

# This variable is used to disable or enable profiling
enabled = 0

def log(msg):
    LOG('PTProfiler', INFO, msg)

#-----------------------------------------------------------------------------
# Expressions
#-----------------------------------------------------------------------------

def __patched_call__(self, econtext):
    """The patched method for expressions
    """
    global enabled
    
    name = self._patching_class._get_name(econtext)
    if enabled and name and not name.find(os.path.dirname(__file__)) > -1:
        expr = self._patching_class._get_expr(self)
        starttime = time.clock()
        ret = self._patching_class._org_method(self, econtext)
        profile_container.expr_hit(name, expr, time.clock() - starttime)
    else:
        # not a pagetemplate or one of the profiler's pts, or profiling is disabled, so don't time
        ret = self._patching_class._org_method(self, econtext)

    return ret

class ExprProfilerPatch:
    """A generic class to hook into expression objects
    """
    def __init__(self, type, class_to_patch):
        self._type = type
        self._org_method = class_to_patch.__call__
        class_to_patch.__call__ = __patched_call__
        class_to_patch._patching_class = self
        log('patch TALES __call__ of expression %s' % type)

    def _get_name(self, econtext):
        name = None
        if econtext.contexts.has_key('template'):
            name = getattr(econtext.contexts['template'], '_filepath', None) or getattr(econtext.contexts['template'], 'filename', None) or getattr(econtext.contexts['template'], 'id')
        return name

    def _get_expr(self, obj):
        if self._type == 'python':
            return 'python: %s' % obj.expr
        else:
            return '%s: %s' % (self._type, obj._s)

class ExprProfilerPatchZ3(ExprProfilerPatch):
    
    def _get_expr(self, obj):
        if self._type == 'python':
            return 'python: %s' % obj.text
        else:
            return '%s: %s' % (self._type, obj._s)


#-----------------------------------------------------------------------------
# PageTemplates
#-----------------------------------------------------------------------------

def __patched_render__(self, source=0, extra_context={}):
    global enabled
    
    name = self._patching_class._get_name(self)
    # don't profile if profiling is disabled and don't profile our own pts
    if enabled and not name.find(os.path.dirname(__file__)) > -1:
        starttime = time.clock()
        try:
            ret = self._patching_class._org_method(self, source, extra_context)
        finally:
            profile_container.pt_hit(name, time.clock() - starttime)
    else:
        ret = self._patching_class._org_method(self, source, extra_context)

    return ret

class PTProfilerPatch:
    """A class to hook into PageTemplates
    """
    def __init__(self, class_to_patch):
        self._org_method = class_to_patch.pt_render
        class_to_patch.pt_render = __patched_render__
        class_to_patch._patching_class = self
        log('patch Page Templates pt_render')

    def _get_name(self, object):
        return (getattr(object, '_filepath', None) or 
                    getattr(object, 'filename', None) or 
                    getattr(object, 'id'))

