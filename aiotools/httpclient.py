import asyncio
import aiohttp

RESPONSE_BIN = 0
RESPONSE_TEXT = 1
RESPONSE_JSON = 2
RESPONSE_FILE = 3

class HttpClient:
	def __init__(self,coding='utf-8'):
		self.coding = coding
		self.sessions = {}
		self.cookies = {}

	async def close(self):
		for k,v in self.sessions.items():
			await v.close()
		self.sessions = {}

	def url2domain(self,url):
		parts = url.split('/')[:3]
		pre = '/'.join(parts)
		return pre
		
	def setCookie(self,url,cookies):
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
				jar = aiohttp.CookieJar(unsafe=True)
				self.sessions[pre] = aiohttp.ClientSession(cookie_jar=jar)
				s = self.sessions.get(pre)
			self.lastSession = s
			return s
		return self.lastSession
				
	async def handleResp(self,url,resp,resp_type):
		if resp.cookies is not None:
			self.setCookie(url,resp.cookies)

		if resp_type == RESPONSE_TEXT:
			return await resp.text(self.coding)
		if resp_type == RESPONSE_BIN:
			return await resp.read()
		if resp_type == RESPONSE_JSON:
			return await resp.json()

	async def get(self,url,
					params={},headers={},resp_type=RESPONSE_TEXT):
		session = self.getsession(url)
		resp = await session.get(url,params=params,headers=headers)
		if resp.status==200:
			return await self.handleResp(url,resp,resp_type)
		return None

	async def post(self,url,
					data=b'',headers={},resp_type=RESPONSE_TEXT):
		session = self.getsession(url)
		resp = await session.post(url,data=data,headers=headers)
		if resp.status==200:
			return await self.handleResp(resp,resp_type)
		return None

if __name__ == '__main__':
	async def gbaidu(hc):
		r = await hc.get('https://www.baidu.com')
		print(r)
		await hc.close()
	loop = asyncio.get_event_loop()
	hc = HttpClient()
	loop.run_until_complete(gbaidu(hc))

