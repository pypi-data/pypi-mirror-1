# this will break in 2.10 and will need rewriting
from Products.PageTemplates.Expressions import getEngine
from StringIO import StringIO
from TAL.TALInterpreter import TALInterpreter

def create_tal_context(view, **kw):
    data = dict(context=view.context,
                here=view.context,
                nothing=None,
                request=view.request,
                view=view)
    data.update(kw)
    return getEngine().getContext(data)

def macro_render(macro, context):
    assert macro, """No macro was provided"""
    buffer = StringIO()
    TALInterpreter(macro, {}, context, buffer)()
    return buffer.getvalue()
