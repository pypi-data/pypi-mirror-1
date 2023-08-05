import HTMLParser, urllib, urllib2, re

def default(value, default):
	if value == None:
		return default
	else:
		return value

def urlencode(body, encode):
	if body == None:
		return None
	elif encode:
		return urllib.urlencode(body)
	else:
		return body
		
class Request:
	def __init__(self, url=None, body=None, headers={"user-agent" : "PyderWeb/0.0.1"}, get=True, encode=True):
		self.url = url
		self.__body = urlencode(body, encode)
		self.headers = headers
		self.get = get
		self.encode = encode
		
	def setBody(self, body, encode=True):
		self.__body = urlencode(body, encode)
		
	def getResponse(self, url=None, body=None, headers={}, get=None, encode=None):
		url = default(url, self.url)
		get = default(get, self.get)
		encode = default(encode, self.encode)
		body = default(urlencode(body, encode), self.__body)
						
		headers.update(self.headers)
		
		if get and body:
			url += "?" + body
			body = None
		
		req = urllib2.Request(url, body, headers)
		f = urllib2.urlopen(req)
		return Response(f)
	
class Response:
	def __init__(self, f):
		self.f = f
		self.body = f.read()
		
	def links(self):
		p = Parser()
		p.feed(self.body)
		p.close()
		return p.a

class Parser(HTMLParser.HTMLParser):
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		self.a = []
		self.starttag = True
		
	def handle_starttag(self, tag, attrs):
		if tag == "a":
			self.a.append( [dict(attrs), ""] )
			self.starttag = True

	def handle_endtag(self, tag):
		self.starttag = False
			
	def handle_data(self, data):
		if self.starttag and len(self.a) > 0:
			self.a[-1][1] += data

def main():
	req = Request(get=False)
	req.setBody({"q":"11"})
	res = req.getResponse("http://localhost:8000/test")
	print res.body
	print res.links()
	
if __name__ == "__main__":
	main()
