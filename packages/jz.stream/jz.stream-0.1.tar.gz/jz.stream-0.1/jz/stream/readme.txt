jz.stream:

Tools to easily handle data streams.

Features:
	- Send a properly formatted file name to the browser. File name is created from the object's name and the extension is given according to the content using mime magic data.


Available views:
	@@download : Download content.


Examples:

create some sample content:

	>>> from jz.stream.tests.sample import StreamContent
	>>> stream = StreamContent()

get the data stream headers:

	>>> from jz.stream.browser import StreamView
	>>> page = StreamView(stream, TestRequest())
	>>> output = page()
	>>> page.request.response.getHeaders()
	[...('Content-Length', '31'), ('Content-Disposition', 'inline; filename=content.plain'), ('Expires', '...'), ('Last-Modified', '...'), ('Cache-Control', 'public,max-age=86400'), ('Content-Type', 'text/plain')]

and the data stream itself:

	>>> output
	'I am a sample stream of content'