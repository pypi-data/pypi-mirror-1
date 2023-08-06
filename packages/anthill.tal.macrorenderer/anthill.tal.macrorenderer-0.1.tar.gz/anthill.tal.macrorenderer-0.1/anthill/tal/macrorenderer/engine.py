from StringIO import StringIO
from zope.tal.talinterpreter import TALInterpreter

class MacroRenderer(object):
    """ This engine makes it possible to render single macros
        from a page template using pure python code. """

    def __init__(self, pagetemplate, macroname):
        pagetemplate._cook()
        self.pt = pagetemplate
        self.mn = macroname

        try:
            self.m_program = self.pt.macros[self.mn]
        except KeyError:
            raise Exception, 'Did not find macro named %s' % self.mn

    def __call__(self, **kw):
        """ Returns rendered macro data. You can pass options. """

        output = StringIO(u'')
        context = self.pt.pt_getContext()
        context['options'] = kw

        TALInterpreter(self.m_program, None, self.pt.pt_getEngineContext(context), output)()
        return output.getvalue()
