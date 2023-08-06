# zope modules
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# custom modules
from interfaces import IStream


class Stream(object):
	__doc__ = IStream.__doc__

	implements(IStream)

	data = FieldProperty(IStream['data'])