### -*- coding: utf-8 -*- ############################################
### Author: Ilshad Habibullin, 2008 <astoon.net@gmail.com> ###########
######################################################################

__license__ = "GPL v.3"

from StringIO import StringIO
from zope.interface import implements
from zope.tales.expressions import StringExpr
from zope.component import queryUtility, getMultiAdapter
from interfaces import ITALESAdverletExpression, IAdverlet

class TALESAdverletExpression(StringExpr):
    implements(ITALESAdverletExpression)
    
    def __call__(self, econtext):
        name = super(TALESAdverletExpression, self).__call__(econtext)
        adverlet = queryUtility(IAdverlet, name)

        if not adverlet:
            return None

        source = adverlet.source

        if source:
            return not adverlet.newlines and source or ''.join(
                ['%s <br />' % s for s in StringIO(source).readlines()])

        default = adverlet.default

        if not default:
            return None

        view = getMultiAdapter(
            (econtext.vars['context'], econtext.vars['request']),
            name=default)

        return view()
