from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from cryptography.exceptions import InvalidSignature
import ujson as json
import io
from appPublic.jsonConfig import getConfig
from appPublic.macAddress import getAllMacAddress


# 验证函数
class LicenseChecker:
	def __init__(self):
		self.keydata = None

	def setkeydata(self,kdata,appkey,appname):
		self.keydata = kdata
		self.appkey = appkey
		self.appname = appname
		self.public_key = serialization.load_pem_public_key(
			self.keydata,
			backend=default_backend()
		)
		
	def getIp(self):
		conf = getConfig()
		macs = [ i for i in getAllMacAddress()]
		for m in macs:
			if m[0] == conf.license.mac:
				return m[1]
		print(conf.license.mac, macs)
		return '0.0.0.0'
		
	def verify(self):
		conf = getConfig()
		license = conf.license
		data = {}
		data.update(license)
		del data['rc']
		data = json.dumps(data).encode('ascii')
		rc = license.rc
		cnt = int(len(rc)/2)
		signature = b''.join([bytes.fromhex(rc[i*2:i*2+2]) for i in range(cnt) ])
		verify_ok = False
		try:
			# 使用公钥对签名数据进行验证
			# 指定填充方式为PKCS1v15
			# 指定hash方式为sha256
			self.public_key.verify(
				signature,
				data,
				padding.PKCS1v15(),
				hashes.SHA256()
			)
		# 签名验证失败会触发名为InvalidSignature的exception
		except InvalidSignature:
			# 打印失败消息
			print('invalid signature!')
		else:
			# 验证通过，设置True
			verify_ok = True

		# 返回验证结果
		return verify_ok		
