# 导入cryptography库的相关模块和函数
import os
import sys
import ujson as json
from appPublic.folderUtils import ProgramPath

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


# 签名函数

def sign(data, private_key_file_name):
    """
    签名函数使用指定的私钥Key对文件进行签名，并将签名结果写入文件中
    :param data_file_name: 待签名的数据文件
    :param signature_file_name: 存放签名结果的文件
    :param private_key_file_name: 用于签名的私钥文件
    :return: 签名数据
    """

    # 从PEM文件中读取私钥数据
    key_file = open(private_key_file_name, 'rb')
    key_data = key_file.read()
    key_file.close()

    # 从PEM文件数据中加载私钥
    private_key = serialization.load_pem_private_key(
        key_data,
        password=None,
        backend=default_backend()
    )

    # 使用私钥对数据进行签名
    # 指定填充方式为PKCS1v15
    # 指定hash方式为sha256
    signature = private_key.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    # 返回签名数据
    return b''.join([ b'%02x' % i for i in signature ])


if __name__ == '__main__':
	if len(sys.argv)<5:
		print('usage\n%s appkey appname email mac' % sys.argv[0],len(sys.argv),sys.argv)
		sys.exit(1)
	appkey = sys.argv[1]
	appname = sys.argv[2]
	email = sys.argv[3]
	mac = sys.argv[4]
	path = os.path.join(ProgramPath(),appkey)
	if not os.path.exists(path):
		os.mkdir(path)
	pkf = os.path.join(path,'Key.pem')
	pubkf = os.path.join(path,'Key_pub.pem')
	pyf = os.path.join(path,'keybytes.py')
	if not os.path.exists(pkf):
		os.system('openssl genrsa -out ' + pkf + ' -f4 2048')
		os.system('openssl rsa -in ' + pkf + ' -pubout -out ' + pubkf)
	if not os.path.exists(pyf):
		f = open(pubkf,'r')
		kd = f.read()
		f.close()
		b = '''keydata=b"""%s"""
appkey="%s"
appname="%s"''' % (kd,appkey,appname)
		f = open(os.path.join(path,'keybytes.py'),'w')
		f.write(b)
		f.close()
	# 签名并返回签名结果
	license={}
	license = {
		'app':appkey,
		'email':email,
		'mac':mac
	}
	b = json.dumps(license).encode('ascii')
	print('b=',b)
	license['rc'] = sign(b, pkf)
	print(json.dumps(license,indent=4))
	sys.exit(0)

