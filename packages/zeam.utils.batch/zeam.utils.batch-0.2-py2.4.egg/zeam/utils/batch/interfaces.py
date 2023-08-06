# Copyright Sylvain Viollon 2008 (c)
# $Id: interfaces.py 78 2008-07-31 08:01:54Z sylvain $

from zope.interface.interfaces import Interface
from zope.annotation.interfaces import IAttributeAnnotatable
from zope import schema

class IBatch(Interface):
    """A batch object.
    """

    start = schema.Int(
	title=u"Starting indice over the batch")
    count = schema.Int(
	title=u"Number of element in a batch")
    data = schema.List(
	title=u"Data to be batched")
    name = schema.TextLine(
	title=u"Name of the batch",
	required=False,
	default=u"")

    def __getitem__(index):
	"""Return item at index.
	"""

    def __iter__():
	"""Return an iterator.
	"""

    def all():
	"""Return sequence of all start index.
	"""

    def first():
	"""Return first sequence in batch.
	"""

    def last():
	"""Return last available sequence in batch.
	"""
	

class IBatchView(Interface):
    """Used to render batch.
    """

	
class IBatchedContent(IAttributeAnnotatable):
    """Marker interface for content with batched data.
    """
