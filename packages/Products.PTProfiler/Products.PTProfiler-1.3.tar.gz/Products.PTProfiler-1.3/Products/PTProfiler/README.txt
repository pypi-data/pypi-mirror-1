PTProfiler
**********

PTProfiler is a small profiling system for page templates in Zope
2. It times each TAL expression and lists the results in a table
ranked by processing time.

Using PTProfiler
================

Do mind that this product (when enabled, see below) requires some
extra processing time for page templates, so isn't recommended for
production sites.

To enable and view the results, place a *PTProfiler Viewer* object
somewhere in the Zope tree, and press the *Enable* button. After some
page templates are viewed, you will see a list of paths to each of
those page templates (or, in the rare case the path isn't known, the
id). When you click one of the items, you will see a list of all the
expression calls in the template, ordered by total time spent on that
expression.

