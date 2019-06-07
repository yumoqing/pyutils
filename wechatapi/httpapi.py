
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import json
import logging
import traceback

def _get(url: object, api: object = None, timeout: object = None) -> object:
	request = urllib.request.Request(url=url)
	request.add_header('Referer', 'https://wx.qq.com/')
	if api in [ 'webwxgetvoice', 'webwxgetvideo' ]:
		request.add_header('Range', 'bytes=0-')
	try:
		response = urllib.request.urlopen(request, timeout=timeout) if timeout else urllib.request.urlopen(request)
		if api == 'webwxgetvoice' or api == 'webwxgetvideo':
			data = response.read()
		else:
			data = response.read().decode('utf-8')
		logging.debug(url)
		return data
	except urllib.error.HTTPError as e:
		logging.error('HTTPError = ' + str(e.code))
	except urllib.error.URLError as e:
		logging.error('URLError = ' + str(e.reason))
	except http.client.HTTPException as e:
		logging.error('HTTPException')
	except timeout_error as e:
		pass
	except ssl.CertificateError as e:
		pass
	except Exception:
		import traceback
		logging.error('generic exception: ' + traceback.format_exc())
	return ''

def _post(url: object, params: object, jsonfmt: object = True) -> object:
	if jsonfmt:
		data = (json.dumps(params)).encode()
		
		request = urllib.request.Request(url=url, data=data)
		request.add_header(
			'ContentType', 'application/json; charset=UTF-8')
	else:
		request = urllib.request.Request(url=url, data=urllib.parse.urlencode(params).encode(encoding='utf-8'))


	try:
		response = urllib.request.urlopen(request)
		data = response.read()
		if jsonfmt:
			return json.loads(data.decode('utf-8') )#object_hook=_decode_dict)
		return data
	except urllib.error.HTTPError as e:
		logging.error('HTTPError = ' + str(e.code))
	except urllib.error.URLError as e:
		logging.error('URLError = ' + str(e.reason))
	except http.client.HTTPException as e:
		logging.error('HTTPException')
	except Exception:
		logging.error('generic exception: ' + traceback.format_exc())

	return ''

