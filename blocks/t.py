from widgetExt import PhoneButton

from kivy.app import App

class MyApp(App):
	def build(self):
		return PhoneButton(phone_number='114')

if __name__ == '__main__':
	MyApp().run()
