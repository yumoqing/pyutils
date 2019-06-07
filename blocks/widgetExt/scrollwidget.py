from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Ellipse,Rectangle

class ScrollWidget(ScrollView):
	def __init__(self,**kw):
		"""
		with self.canvas:
			c = Color(1,0,0,1)
			Rectangle(pos=self.pos, size=self.size)
		"""
		super(ScrollWidget,self).__init__(**kw)
		self._inner_layout = GridLayout(cols=1, padding=2, spacing=2,size_hint=(None, None))
		self._inner_layout.bind(minimum_height=self._inner_layout.setter('height'))
		self._inner_layout.bind(minimum_width=self._inner_layout.setter('width'))
		super(ScrollWidget,self).add_widget(self._inner_layout)
	
	def add_widget(self,w,**kw):
		return self._inner_layout.add_widget(w,**kw)
	
	def clear_widget(self,w,**kw):
		return self._inner_layout.clear_widget(w,**kw)
	
	def remove_widget(self,w,**kw):
		return self._inner_layout.remove_widget(w,**kw)

if __name__ == '__main__':
	from kivy.app import App
	from kivy.uix.label import Label
	from kivy.uix.button import Button
	import codecs
	
	class MyApp(App):
		def build(self):
			root = ScrollWidget(size=(400,400),pos_hint={'center_x': .5, 'center_y': .5},do_scroll_x=True,do_scroll_y=True)
			with codecs.open(__file__,'r','utf-8') as f:
				txt = f.read()
				lines = txt.split('\n')
				for l in lines:
					root.add_widget(Label(text=l,color=(1,1,1,1),size_hint=(None,None),size=(1200,40)))
			return root

	MyApp().run()
