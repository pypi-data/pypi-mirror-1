HTML = """\
<html>
<body>
<pre>
client_address: %s
command: %s
path: %s
request_version: %s

<b>HEADERS</b>
%s
<b>CONTENT</b>
%s
</pre>
<a href="http://localhost:8000/one">One</a><br>
<A href="http://localhost:8000/two">Two
</a>
<a href="http://" href="ftp://">One</a><br>
</body>
</html>
"""

import BaseHTTPServer, httplib, SocketServer, urllib

class HTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def doCommon(self):
		contentLength = self.headers.getheader("content-length")
		if contentLength:
			content = self.rfile.read(int(contentLength))
		else:
			content = None

		html = HTML % (str(self.client_address), self.command, self.path,
			self.request_version, str(self.headers), content)	
	
		self.send_response(200)
		self.end_headers()
		self.wfile.write(html)
		
	def do_GET(self):
		self.doCommon()

	def do_POST(self):
		self.doCommon()
	
class ThreadingHTTPServer(SocketServer.ThreadingTCPServer, BaseHTTPServer.HTTPServer):
	pass
		
def test(HandlerClass = HTTPRequestHandler,
		ServerClass = ThreadingHTTPServer):
	BaseHTTPServer.test(HandlerClass, ServerClass)
	
if __name__ == '__main__':
	test()
