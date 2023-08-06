# Copyright Sylvain Viollon 2008 (c)
# $Id: views.py 85 2008-10-18 00:15:41Z sylvain $

from zope.interface import implements
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.traversing.interfaces import ITraversable
from zope.traversing.browser import absoluteURL

import zope.cachedescriptors.property

from zeam.utils.batch.interfaces import IBatchView

class baseView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

class batchView(baseView):
    """View object on batched elements.
    """

    implements(IBatchView)

    render = ViewPageTemplateFile('templates/batch.pt')

    def __init__(self, context, batch, request):
        super(batchView, self).__init__(context, request)
        self._batch = batch

    @zope.cachedescriptors.property.CachedProperty
    def contextURL(self):
        return absoluteURL(self.context, self.request)

    def _baseLink(self, position):
        if not position:
            return self.contextURL
	if self._batch.name:
	    base = '%s/++batch++%s+%d'
	    return  base % (self.contextURL, self._batch.name, position)
	return '%s/++batch++%d' % (self.contextURL, position)

    @property
    def batch(self):
        end = self._batch.batchLen()
        if end > 1:
            count = 0
            wanted = self._batch.start / self._batch.count
            ldots = False
            for pos, item in self._batch.all():
                if (((count > 2) and (count < (wanted - 3))) or
                    ((count < (end - 3)) and (count > (wanted + 3)))):
                    if not ldots:
                        ldots = True
                        yield dict(name=None, url=None, style=None)

                else:
                    ldots = False
                    url_item = self._baseLink(pos)
                    current_item = (pos == self._batch.start)
                    style = current_item and 'current' or None
                    yield dict(name=item, url=url_item, style=style)
                count += 1

    @property
    def previous(self):
        previous = self._batch.previous
        avail = not (previous is None)
        return avail and self._baseLink(previous) or None

    @property
    def next(self):
        next = self._batch.next
        avail = not (next is None)
        return avail and self._baseLink(next) or None

    def __call__(self):
        return self.render()


class batchNamespace(baseView):
    """Make batch works with namespace.
    """

    implements(ITraversable)

    def traverse(self, name, ignored):
	if '+' in name:
	    key, value = name.split('+')
	    key = 'bstart_' + key
	else:
	    key = 'bstart'
	    value = name
        self.request.form[key] = value
        return self.context
