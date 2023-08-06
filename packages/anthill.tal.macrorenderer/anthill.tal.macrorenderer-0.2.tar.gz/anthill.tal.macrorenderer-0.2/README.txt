Introduction
============

This package renders macros from a given page template using pure python.

Sometime you may want to use page templates like code libraries where for each
functionality you have one macro. Calling macros is no problem using ZPT
use-macro but how do you call macros from pure python code and also pass
parameters? Because there do not seems to be an obvious solution for this problem 
(especially the parameters part) this package was created.

Render macro with name ``macroname`` from a given page template::

>>> from anthill.tal.macrorenderer import MacroRenderer
>>> template = ViewPageTemplateFile('template.pt')
>>> renderer = MacroRenderer(template, 'macroname')
>>> print renderer(data={'option1' : 42})

Sometimes you get an exception about not enough context being provided to the
renderer (or for prior versions a TypeError). 

A fix is easy: Simply add a  ``context=self.context`` to the MacroRenderer call::

>>> renderer = MacroRenderer(template, 'macroname', context=self.context)
