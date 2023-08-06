r"""Sample data for tests."""

# zope modules
from zope.interface import implements
from zope.annotation.interfaces import IAttributeAnnotatable

# jz modules
from jz.stream.interfaces import IStream
from jz.filerepresentation.interfaces import IFileName


class StreamContent(object):
	"""Stream read from file."""

	implements(IStream, IFileName, IAttributeAnnotatable)

	@property
	def data(self):
		return "I am a sample stream of content"

	name = "content"