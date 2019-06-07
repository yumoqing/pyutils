import re
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.metrics import sp,dp
from kivy.network.urlrequest import UrlRequest

class SelectItem(Button):
	def __init__(self,dropdown,**kw):
		if kw is None:
			kw = {}
		a = {
			"size_hint":[None,None],
			"width":dp(150),
			"height":dp(32)
		}
		a.update(kw)
		super(SelectItem,self).__init__(**a)
		#self.bind(on_release,lambda btn: dropdown.select(btn.text))

class StrInput(TextInput):
	def __init__(self,**kv):
		if kv is None:
			kv = {}
		a = {
			"multiline":False,
			"size_hint":[None,None],
			"width":dp(120),
			"height":dp(32)
		}
		a.update(kv)
		super(StrInput,self).__init__(**a)
		
class IntegerInput(StrInput):
	pat = re.compile('[^0-9]')
	def insert_text(self, substring, from_undo=False):
		pat = self.pat
		s = re.sub(pat, '', substring)
		return super(IntegerInput, self).insert_text(s, from_undo=from_undo)
	
class FloatInput(StrInput):
	pat = re.compile('[^0-9]')
	def insert_text(self, substring, from_undo=False):
		pat = self.pat
		if '.' in self.text:
			s = re.sub(pat, '', substring)
		else:
			s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
		return super(IntegerInput, self).insert_text(s, from_undo=from_undo)

class MyDropDown(DropDown):
	def __init__(self,**kw):
		super(MyDropDown,self).__init__()
		self.options = kw
		self.textField = kw.get('textField',None)
		self.valueField = kw.get('valueField',None)
		if kw.get('url') is not None:
			self.url = kw.get('url')
			self.setDataByUrl(self.url)
		else:
			self.si_data = kw.get('data')
			self.setData(self.si_data)
		self.bind(on_select=lambda instance, x: self.selectfunc(x))

	def selectfunc(self,v):
		f = self.options.get('on_select')
		if f is not None:
			return f(v)
			
	def getTextByValue(self,v):
		for d in self.si_data:
			if d[self.valueField] == v:
				return d[self.textField]
		return str(v)
		
	def getValueByText(self,v):
		for d in self.si_data:
			if d[self.textField]  == v:
				return d[self.valueField]
		return ''
		
	def setData(self,data):
		self.si_data = data
		self.clear_widgets()
		for d in data:
			dd = (d[self.valueField],d[self.textField])
			b = Button(text=d[self.textField],
				size_hint_y=None, 
				height=dp(30))
			setattr(b,'kw_data',dd)
			b.bind(on_release=lambda btn: self.select(btn.kw_data))
			self.add_widget(b)
			#print(dd)
			
	def setDataByUrl(self,url):
		UrlRequest(url,self.setData)
			
	def showme(self,w):
		#print('show it ',w)
		self.target = w
		self.open(w)
		
class SelectInput(BoxLayout):
	def __init__(self,**kw):
		super(SelectInput,self).__init__(orientation='horizontal',						size_hint_y=None,height=dp(32))
		self.tinp = StrInput()
		self.tinp.readonly = True
		self.img = Image(source='./images/bullet_arrow_down.png',
				size_hint=(None,None),
				width=dp(16),height=dp(16))
		self.img.bind(on_touch_down=self.showDropdown)
		newkw = {}
		newkw.update(kw)
		newkw.update({'on_select':self.setData})
		self.dropdown = MyDropDown(**newkw)
		if kw.get('value'):
			self.si_data = kw.get('value')
			self.text = self.dropdown.getTextByValue(self.si_data)
		else:
			self.si_data = ''
			self.text = ''
		self.add_widget(self.tinp)
		self.add_widget(self.img)
		
	def showDropdown(self,instance,touch):
		if self.collide_point(*touch.pos):
			self.dropdown.showme(instance)
		
	def setData(self,d):
		self.tinp.si_data = d[0]
		self.tinp.text = d[1]

	def setValue(self,v):
		self.tinp.si_value = v
		self.tinp.text = self.dropdown.getTextByValue(v)
		
	def getValue(self):
		return self.tinp.si_value
		
if __name__ == '__main__':
	from kivy.app import App
	from kivy.uix.boxlayout import BoxLayout
	class MyApp(App):
		def build(self):
			root = BoxLayout(orientation='vertical')
			x = SelectInput(width=40,value='1',data=[{'value':'1','text':'ban'},{'value':'0','text':'nu'}],textField='text',valueField='value')
			root.add_widget(x)
			b = Button(text='drop', size_hint=(None, None))
			root.add_widget(b)
			dd = MyDropDown(width=40,value='1',data=[{'value':'1','text':'nan'},{'value':'0','text':'nu'}],textField='text',valueField='value',on_select=x.setData)
			b.bind(on_release=dd.showme)
			return root
	MyApp().run()
			
		
