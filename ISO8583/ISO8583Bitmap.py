# 8583 bitmap class
class ISO8583Bitmap :
	"""
	8583 Bitmap class support set bitmap,unset bitmap and check bitmap
	"""
	def __init__(self) :
		self.bitmap = '\0' * 16

	def encode(self) :
		"""
		encode bitmap to iso 8583 transition bitmap text
		"""
		if self.bitmap[8:]== '\0' * 8 :
			self.unsetBitmap(1)
			return self.bitmap[:8]
		self.setBitmap(1)
		return self.bitmap
		
	def decode(self,s) :
		"""
		decode bitmap text from iso 8583 package
		"""

		self.bitmap = s[:16]
		if self.chkBitmap(1) :
			return 16
		self.bitmap = s[:8] + '\0' * 8
		return 8

	def bitStream(self) :
		r  = [ self.chkBitmap(i) and '1' or '0' for i in range(1,129) ]
		return ''.join(r)

	def setBitmap(self,pos) :
		"""
		set bitmap at pos, pos from 1 to 128
		"""
		if pos>128 or pos < 1 :
			return
		pos -= 1
		i,j = divmod(pos,8)
		k = ord(self.bitmap[i])
		k |= 1 << (7-j)
		m = [ j for j in self.bitmap]
		m[i] = chr(k)
		self.bitmap = ''.join(m)

	def unsetBitmap(self,pos) :
		"""
		unset bitmap at pos, pos from 1 to 128
		"""
		if pos>128 or pos < 1 :
			return
		pos -= 1
		i,j = divmod(pos,8)
		k = ord(self.bitmap[i])
		k ^= 1 << (7-j)
		m = [ j for j in self.bitmap]
		m[i] = chr(k)
		self.bitmap = ''.join(m)

	def chkBitmap(self,pos) :
		"""
		check bitmap at pos, pos from 1 to 128
		"""

		if pos>128 or pos < 1 :
			return False
		pos -= 1
		i,j = divmod(pos,8)
		k = ord(self.bitmap[i])
		if k & (1 << (7-j)) > 0 :
			return True
		return False

if __name__=='__main__' :
	b = ISO8583Bitmap()
	b.setBitmap(128)
	print(b.chkBitmap(128))

	b.unsetBitmap(128)
	print(b.chkBitmap(128))
	
	b.setBitmap(1)
	print(b.chkBitmap(1))
	
