import sys
from kivy.uix.button import Button
from kivy.uix.accordion import Accordion,AccordionItem
from kivy.uix.label import Label
from kivy.uix.actionbar import ActionBar,ActionView,ActionPrevious,ActionItem,ActionButton
from kivy.uix.actionbar import ActionToggleButton, ActionCheck,ActionSeparator,ActionGroup

from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout

from kivy.uix.checkbox import CheckBox
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.tabbedpanel import TabbedPanel,TabbedPanelContent,TabbedPanelHeader,TabbedPanelItem
from kivy.uix.treeview import TreeView
from kivy.uix.image import AsyncImage,Image
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.splitter import Splitter
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider

from kivy.uix.screenmanager import ScreenManager
from kivy.uix.sandbox import Sandbox
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.uix.filechooser import FileChooser
from kivy.uix.effectwidget import EffectWidget
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.carousel import Carousel
from kivy.uix.camera import Camera
from kivy.uix.bubble import Bubble
from kivy.uix.codeinput import CodeInput

from widgetExt import BinStateImage
from widgetExt import JsonCodeInput
from widgetExt import FloatInput
from widgetExt import IntegerInput
from widgetExt import StrInput
from widgetExt import SelectInput
from widgetExt import JsonCodeInput
from widgetExt import ScrollWidget
from widgetExt import PhoneButton

#from widgetExt import AWebView
from KivyCalendar import DatePicker

baseWidgets = {
	"AsyncImage":AsyncImage,
	"Image":Image,
	"Button":Button,
	"Accordion":Accordion,
	"AccordionItem":AccordionItem,
	"Label":Label,
	"ActionBar":ActionBar,
	#"ActionOverflow":ActionOverflow,
	"ActionView":ActionView,
	#"ContextualActionViews":ContextualActionViews,
	"ActionPrevious":ActionPrevious,
	"ActionItem":ActionItem,
	"ActionButton":ActionButton,
	"ActionToggleButton":ActionToggleButton,
	"ActionCheck":ActionCheck,
	"ActionSeparator":ActionSeparator,
	"ActionGroup":ActionGroup,
	"AnchorLayout":AnchorLayout,
	"BoxLayout":BoxLayout,
	"FloatLayout":FloatLayout,
	"GridLayout":GridLayout,
	"PageLayout":PageLayout,
	"ScatterLayout":ScatterLayout,
	"RecycleBoxLayout":RecycleBoxLayout,
	"RelativeLayout":RelativeLayout,
	"StackLayout":StackLayout,
	"CheckBox":CheckBox,
	"Switch":Switch,
	"TextInput":TextInput,
	"ToggleButton":ToggleButton,
	"DropDown":DropDown,
	"TabbedPanel":TabbedPanel,
	"TabbedPanelContent":TabbedPanelContent,
	"TabbedPanelHeader":TabbedPanelHeader,
	"TabbedPanelItem":TabbedPanelItem,
	"TreeView":TreeView,
	"Splitter":Splitter,
	"Spinner":Spinner,
	"Slider":Slider,
	"ScreenManager":ScreenManager,
	"Sandbox":Sandbox,
	"ProgressBar":ProgressBar,
	"Popup":Popup,
	"ModalView":ModalView,
	"FileChooser":FileChooser,
	"EffectWidget":EffectWidget,
	"ColorPicker":ColorPicker,
	"Carousel":Carousel,
	"Camera":Camera,
	"Bubble":Bubble,
	"CodeInput":CodeInput,
	"ScrollView":ScrollView,
	# from widgetExt
	"BinStateImage":BinStateImage,
	"JsonCodeInput":JsonCodeInput,
	'FloatInput':FloatInput,
	'IntegerInput':IntegerInput,
	'StrInput':StrInput,
	'SelectInput':SelectInput,
	'ScrollWidget':ScrollWidget,
	#"AWebView":AWebView,
	'DatePicker':DatePicker,
	"PhoneButton":PhoneButton,
}


