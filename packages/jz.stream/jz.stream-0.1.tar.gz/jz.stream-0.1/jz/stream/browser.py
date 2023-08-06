# zope modules
from zope.interface import implements
from zope.publisher.browser import BrowserView
from zope.component import getUtility
from zope.dublincore.interfaces import IZopeDublinCore
from zope.app.publisher.browser.fileresource import setCacheControl
from zope.datetime import time as timeFromDateTimeString

# jz modules
from jz.magic.interfaces import IFileMagic
from jz.filerepresentation.interfaces import IFileName
from interfaces import IStream, IStreamView
from jz.datetime import timestamp
from jz.common import removeAllAdapters

# python modules
import tempfile, os, datetime

# twisted modules
from twisted.web2.http_headers import generateDateTime


class StreamView(BrowserView):
	"""Provides a generic browser view for a non-html data stream.

	In the default implementation, information about the stream is gathered from adapters and utilities	applied to the object.

	"""

	implements(IStreamView)

	def __init__(self, *args, **kargs):
		BrowserView.__init__(self, *args, **kargs)

	@property
	def mimetype(self):
		"""Return mime type.

		Default implementation uses jz.magic utility.
		"""

		return getUtility(IFileMagic).getMimeType(self.data)

	@property
	def filename(self):
		"""Return file name.

		Default implementation uses context's name and mime-type."""

		basename = IFileName(self.context).name
		extension = getUtility(IFileMagic).getFileExtension(self.data)
		return "%s.%s" % (basename, extension)

	@property
	def disposition(self):
		"""Content disposition (rfc2183).

		Possible values: inline, attachment.
		"""

		return "inline"

	@property
	def data(self):
		"""Return data stream."""

		return IStream(self.context).data

	def __call__(self):
		response = self.request.response
		request = self.request

		# Content:
		response.setHeader('Content-Disposition','%s; filename=%s' % (self.disposition, self.filename))
		response.setHeader('Content-Type', self.mimetype)
		response.setHeader('Content-Length', len(self.data))

		# Modification time:
		dublincore = IZopeDublinCore(removeAllAdapters(self.context))
		last_mod = timestamp(dublincore.modified)

		# Copied from fileresource.py
		header = request.getHeader('If-Modified-Since', None)
		if header is not None:
			header = header.split(';')[0]
			try:
				mod_since=long(timeFromDateTimeString(header))
			except:
				mod_since=None
			#print "MOD: since %s mod %s" % (mod_since, last_mod)
			if mod_since is not None:
				if last_mod > 0 and last_mod <= mod_since:
					response.setStatus(304)
					return ''

		response.setHeader('Last-Modified', generateDateTime(last_mod))

		# Cache (defaults to 86400 seconds/1 day):
		setCacheControl(response)

		# Content data:
		return self.data

		#NOTE: other way of sending data. return a file handle
		#tf = tempfile.TemporaryFile()
		#tf.write(self.data)
		#NOTE: flush() here fixes problem of file not being downloaded completely.
		#tf.flush()
		#return tf