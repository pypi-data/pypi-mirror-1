# zope modules
from zope.app.file.interfaces import IFile
from zope.interface import Interface
from zope.schema import Bytes, TextLine
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("jz.stream")


class IStream(Interface):
	"""Interface for a generic data stream."""

	data = Bytes(
		title=_("Data"),
		)


class IStreamView(Interface):
	"""Interface for a stream view."""

	data = Bytes(
		title=_("Data"),
		)

	filename = TextLine(
		title=_("File name"),
		)

	mimetype = TextLine(
		title=_("Mime type"),
		)