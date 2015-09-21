import gtk
import gtk.glade


######## main application window #######################################
class MyToolbar:
	"""This is the toolbar class"""

	def __init__(self,vbox):

		self.vbox= vbox

		self.toolbar  = self.initToolbar()
		self.btnTypeList  = []		
		self.btnList  = []


	def initToolbar(self):
#		handlebox = gtk.HandleBox()
#		self.vbox.pack_start(handlebox, False, False, 5)

		toolbar = gtk.Toolbar()
		toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
		toolbar.set_style(gtk.TOOLBAR_BOTH)
		toolbar.set_border_width(5)
		self.vbox.pack_start(toolbar,False,False)

		return toolbar


	def addToToolbar(self,toolbar,btnType,btnLabel='',icon=gtk.STOCK_ADD):

		if btnType == 'Add':
			iconw = gtk.Image() # icon widget
			iconw.set_from_stock(gtk.STOCK_ADD,gtk.ICON_SIZE_LARGE_TOOLBAR)
			item = toolbar.append_item(
			    "Add",           # button label
			    "Add", # this button's tooltip
			    "Private",         # tooltip private info
			    iconw,             # icon widget
			    self.dummy) # a signal
		elif btnType == 'Generic':
			iconw = gtk.Image() # icon widget
			iconw.set_from_stock(icon,gtk.ICON_SIZE_LARGE_TOOLBAR)
			item = toolbar.append_item(
			    btnLabel,           # button label
			    btnLabel, # this button's tooltip
			    "Private",         # tooltip private info
			    iconw,             # icon widget
			    self.dummy) # a signal
		elif btnType == 'Toggle':
			# toggle button
			iconw = gtk.Image() # icon widget
			iconw.set_from_stock(icon,gtk.ICON_SIZE_LARGE_TOOLBAR)
			item = gtk.ToggleButton(label=btnLabel)
			item.set_image(iconw)
			toolbar.append_widget(item,  btnLabel, "Private")
		elif btnType == 'Label':
			item=gtk.Label(btnLabel)
			toolbar.append_widget(item,  btnLabel, "Private")
		elif btnType == 'Filename':
			lblFilename=gtk.Label('Filename:')
			toolbar.append_widget(lblFilename,  "Filename", "Private")
			item=gtk.Entry(max=0)
			toolbar.append_widget(item,  "Enter a settings filename, e.g. IV.set", "Private")
		elif btnType == 'Save':
			# <save> button
			iconw = gtk.Image() # icon widget
			iconw.set_from_stock(gtk.STOCK_SAVE,gtk.ICON_SIZE_LARGE_TOOLBAR)
			item = toolbar.append_item(
			    "Save",           # button label
			    "Save file", # this button's tooltip
			    "Private",         # tooltip private info
			    iconw,             # icon widget
			    self.dummy) # a signal
		elif btnType == 'Load':
			# <save> button
			iconw = gtk.Image() # icon widget
			iconw.set_from_stock(gtk.STOCK_LOAD,gtk.ICON_SIZE_LARGE_TOOLBAR)
			item = toolbar.append_item(
			    "Load",           # button label
			    "Load file", # this button's tooltip
			    "Private",         # tooltip private info
			    iconw,             # icon widget
			    self.dummy) # a signal
		elif btnType == 'Apply':
			# <apply> button
			iconw = gtk.Image() # icon widget
			iconw.set_from_stock(gtk.STOCK_APPLY,gtk.ICON_SIZE_LARGE_TOOLBAR)
			item = toolbar.append_item(
			    "Apply",           # button label
			    "Apply the settings in the file", # this button's tooltip
			    "Private",         # tooltip private info
			    iconw,             # icon widget
			    self.dummy) # a signal
		elif btnType == 'Close':
			# <close> button
			iconw = gtk.Image() # icon widget
			iconw.set_from_stock(gtk.STOCK_CLOSE,gtk.ICON_SIZE_LARGE_TOOLBAR)
			item = toolbar.append_item(
			    "Close",           # button label
			    "Close this window", # this button's tooltip
			    "Private",         # tooltip private info
			    iconw,             # icon widget
			    self.dummy) # a signal
		elif btnType == 'Progress':
			# progress bar
			item = gtk.ProgressBar(adjustment=None)
			toolbar.append_widget(item,  btnLabel, "Private")
#			item.set_sensitive(0)
		elif btnType == 'Space':
			item=toolbar.append_space() # space after item
		elif btnType == 'FFT':
			# <close> button
			iconw = gtk.Image() # icon widget
			iconw.set_from_stock(gtk.STOCK_SELECT_COLOR,gtk.ICON_SIZE_LARGE_TOOLBAR)
			item = toolbar.append_item(
			    "FFT",           # button label
			    "Fourier transform data", # this button's tooltip
			    "Private",         # tooltip private info
			    iconw,             # icon widget
			    self.dummy) # a signal
		else:
			print 'WARNING:: toolbar.py:: unknown toolbar button type ' + btnType

		self.btnTypeList.append(btnLabel)
		self.btnList.append(item)
		
		return item


	def findBtn(self,btnName):
		result='None'
		for x in range(len(self.btnList)):
			if self.btnTypeList[x]==btnName:
				result = self.btnList[x]
				break

		return result

	def dummy(self, widget):
		return
#		print 'test'
