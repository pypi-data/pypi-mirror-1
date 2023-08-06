"""
PTPathProfiler is a small page template expression profiler that monkey
expression classes to measure the speed of individual expressions

Copyright (c) 2003-2007 Infrae. All rights reserved.
See also LICENSE.txt
Version of this file: $Revision: 1.4 $
Written by Guido Wesdorp and other contributors
E-mail: guido@infrae.com
"""

# import the profiling machinery and monkeypatch the objects
from ProfilerPatch import ExprProfilerPatch, PTProfilerPatch
from ProfilerPatch import ExprProfilerPatchZ3
from ProfilerPatch import log

from Products.PageTemplates.PageTemplate import PageTemplate
from Products.PageTemplates.ZRPythonExpr import PythonExpr
from Products.PageTemplates.Expressions import PathExpr, StringExpr

try:
    from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
    from zope.pagetemplate.pagetemplate import PageTemplate as PageTemplateZ3

    from zope.tales.pythonexpr import PythonExpr as PythonExprZ3
    from zope.tales.expressions import PathExpr as PathExprZ3
    from zope.tales.expressions import StringExpr as StringExprZ3
    HAS_Z3TEMPLATES = True
except ImportError:
    HAS_Z3TEMPLATES = False

import PTProfilerViewer

def initialize(context):
    context.registerClass(
        PTProfilerViewer.PTProfilerViewer,
        constructors=(PTProfilerViewer.manage_addPTProfilerViewerForm,
                      PTProfilerViewer.manage_addPTProfilerViewer),
        icon='www/PTP.gif',
        )

    pt = PageTemplate()
    if isinstance(pt, PageTemplateZ3):
        TEMPLATES_ARE_Z3 = True
    else:
        TEMPLATES_ARE_Z3 = False
    if HAS_Z3TEMPLATES:
        if TEMPLATES_ARE_Z3:
            log('Patching page templates...')
            PTProfilerPatch(PageTemplate)
        else:
            log('Patching Five page templates...')
            PTProfilerPatch(ZopeTwoPageTemplateFile)
        log('Patching Z3 TALES engine...')
        ExprProfilerPatchZ3('python', PythonExprZ3)
        ExprProfilerPatchZ3('path', PathExprZ3)
        ExprProfilerPatchZ3('string', StringExprZ3)
        log('Patched')
    if (not HAS_Z3TEMPLATES) or (not TEMPLATES_ARE_Z3):
        log('Patching page templates...')
        PTProfilerPatch(PageTemplate)
        log('Patching Z2 TALES engine...')
        ExprProfilerPatch('python', PythonExpr)
        ExprProfilerPatch('path', PathExpr)
        ExprProfilerPatch('string', StringExpr)
        log('Patched')
