import aiohttp

RESPONSE_BIN = 0
RESPONSE_TEXT = 1
RESPONSE_JSON = 2
RESPONSE_FILE = 3

class HttpClient:
	def __init__(self,coding='utf-8')
		self.coding = coding
		self.sessions = {}
		self.cookies = {}

	def url2domain(self,url):
		parts = url.split('/')[:3]
		pre = '/'.join(parts)
		return pre
		
	def saveCookies(self,url,cookies):
		name = self.url2domain(url)
		self.cookies[name] = cookies

	def getCookies(self,url):
		name = url2domain(url)
		return self.cookies.get(name)

	def getsession(self,url):
		if url.startswith('http'):
			pre = self.url2domain(url)
			s = self.sessions.get(pre)
			if s is None:
				self.sessions[pre] = aiohttp.ClientSession()
				s = self.sessions.get(pre)
			self.lastSession = s
			return s
		return self.lastSession
				
	async def handleResp(resp,method):
		if resp.cookies is not None:
			self.setCookie(resp.url,resp.cookies)

		if method == RESPONSE_TEXT:
			return await resp.text(self.coding)
		if method == RESPONSE_BIN:
			return await resp.read()
		if method == RESPONSE_JSON:
			return await resp.json()

	async def get(self,url,method="json",
					params={},headers={},method=RESPONSE_TEXT):
		session = self.getsession(url)
		resp = await session.get(url,params=params,headers=headers)
		if resp.status==200:
			return await self.handleResp(resp,method)

	async def post(self,url,method="json",
					data=b'',headers={}):
		session = self.getsession(url)
		resp = await session.post(url,data=data,headers=headers)
		if resp.status==200:
			return await self.handleResp(resp,method)

