import os

try:
	import pygtk
	pygtk.require("2.0")
except:
  	pass
  	
try:
	import gtk
except:
	sys.exit(1)

#from paramWidget import *
from fileIO import getColumnDelim, loadClass, saveClass
import time
from generic import dummyClass


class IconButton(gtk.Button):
	def __init__(self,label='Test',icon=gtk.STOCK_APPLY,iconSize=gtk.ICON_SIZE_BUTTON):
		gtk.Button.__init__(self)

		hBtn = gtk.HBox(False,0)
		lbl=gtk.Label(label)
		img=gtk.Image()
		img.set_from_stock(icon,iconSize)
		hBtn.pack_start(img)
		if not (label == None):
			hBtn.pack_start(lbl)

		self.add(hBtn)


class ArrowButton(gtk.Button):
	def __init__(self,orientation='right'):
		gtk.Button.__init__(self)

		hBtn = gtk.HBox(False,0)
		if orientation=='right':
			arr=gtk.Arrow(gtk.ARROW_RIGHT, gtk.SHADOW_IN)
		elif orientation=='left':
			arr=gtk.Arrow(gtk.ARROW_LEFT, gtk.SHADOW_IN)
		elif orientation=='up':
			arr=gtk.Arrow(gtk.ARROW_UP, gtk.SHADOW_IN)
		elif orientation=='down':
			arr=gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_IN)

		hBtn.pack_start(arr)
		self.add(hBtn)


##### GENERIC GTK HELPER FUNCTIONS
def add_icon_to_button(button,buttonType=gtk.STOCK_CLOSE):
	"Fonction pour ajouter un bouton fermer"
	iconBox = gtk.HBox(False, 0)
	image = gtk.Image()
	image.set_from_stock(buttonType,gtk.ICON_SIZE_MENU)
	gtk.Button.set_relief(button,gtk.RELIEF_NONE)
	settings = gtk.Widget.get_settings(button)
	(w,h) = gtk.icon_size_lookup_for_settings(settings,gtk.ICON_SIZE_MENU)
	gtk.Widget.set_size_request(button, w + 12, h + 12)
	image.show()
	iconBox.pack_start(image, True, False, 0)
	button.add(iconBox)
	iconBox.show()
	return


#### comboBoxes	
def get_active_text(combobox):
	""" Get the active text of a combo box """
	model = combobox.get_model()
	active = combobox.get_active()
	if active < 0:
		return 'None'
	return model[active][0]


def set_cmb_text(cmbBox,setText):
	setSuccessfully=0		

	cmbBoxModel=cmbBox.get_model()
	for x in range(len(cmbBoxModel)):
		for y in range(len(cmbBoxModel[x])):
			if cmbBoxModel[x][y]==setText:
				try:
					cmbBox.set_active(x)
					setSuccessfully=1
					break
				except:
					pass

	if setSuccessfully==0:
		print 'set_cmb_text::Warning:: could not set combo box to: ', setText

	return setSuccessfully



def fileDialog(dialog_action, file_name="", file_filter_name="", file_filter="", currentDir="", title_string="Select File", extraWidget=None):
	""" dialog_action = open, save or choose"""

	if (dialog_action=='open'):
		command = gtk.FILE_CHOOSER_ACTION_OPEN
		dialog_buttons = (gtk.STOCK_CANCEL
							, gtk.RESPONSE_CANCEL
							, gtk.STOCK_OPEN
							, gtk.RESPONSE_OK)
	elif (dialog_action=='save'):
		command = gtk.FILE_CHOOSER_ACTION_SAVE
		dialog_buttons = (gtk.STOCK_CANCEL
							, gtk.RESPONSE_CANCEL
							, gtk.STOCK_SAVE
							, gtk.RESPONSE_OK)
	elif (dialog_action=='choose'):
		command = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER
		dialog_buttons = (gtk.STOCK_CANCEL
							, gtk.RESPONSE_CANCEL
							, gtk.STOCK_OPEN
							, gtk.RESPONSE_OK)
	else:
		print 'fileDialog::Error:: Invalid fileDialog action:' + dialog_action

	file_dialog = gtk.FileChooserDialog(title=title_string
				, action=command
				, buttons=dialog_buttons)
#	"""set the filename if we are saving"""
	""" set the filename if it's provided """
	if (dialog_action=='save'):
		if not file_name=='':
			file_dialog.set_current_name(file_name)
	else:
		if not file_name=='':
			file_dialog.set_filename(file_name)


	if not len(file_filter)==0:
		"""Create and add the filter"""
		filter = gtk.FileFilter()
		filter.set_name(file_filter_name)
		filter.add_pattern("*." + file_filter)
		file_dialog.add_filter(filter)

	"""Create and add the 'all files' filter"""
	filter = gtk.FileFilter()
	filter.set_name("All files")
	filter.add_pattern("*")
	file_dialog.add_filter(filter)

	if not extraWidget==None:
		file_dialog.set_extra_widget(extraWidget)

	if not currentDir=="":
		oldDir=os.getcwd()  # get current directory (location of control.py)
#		print oldDir
		os.chdir(currentDir)
		file_dialog.set_current_folder(currentDir)

#	preview = gtk.Image()
#	preview = gtk.Label('Test')
#	file_dialog.set_preview_widget(preview)
#	file_dialog.connect("update-preview", update_preview_cb, preview)


	"""Init the return value"""
	result = ""
	if file_dialog.run() == gtk.RESPONSE_OK:
		result = file_dialog.get_filename()
		file_dialog.destroy()
	else:
		file_dialog.destroy()
		return result

#	print 'result=' + str(result) + 'length:' + str(len(result))
	if not currentDir=="":
		os.chdir(oldDir)    # return to location of control.py

	return result	
	

#def update_preview_cb(file_chooser, preview):
#	print 'here'
#	filename = file_chooser.get_preview_filename()
#	try:
#		pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename, 128, 128)
#		preview.set_from_pixbuf(pixbuf)
#		have_preview = True
#	except:
#		have_preview = False
#		file_chooser.set_preview_widget_active(have_preview)
#	return


	
def do_gui(fn,*args,**kw):
	def idle_func():
		#print "idle"
		gtk.gdk.threads_enter()
		try:
			fn(*args,**kw)
		finally:
			gtk.gdk.threads_leave()
	gobject.idle_add(idle_func)


def getWidgetValue(widget):

	try:
		result = widget.get_active()
		return result
	except:
		pass

	try:
		result = widget.get_text()
		return result
	except:
		pass

	try:
		result = widget.get_value()
		return result
	except:
		pass


def getParamValue(widget, name, resultDict):
	result = getWidgetValue(widget)
	resultDict[name]=result



######## Widget with group of radio buttons #######################################
class RadioWidget:
	"""This is the generic instrument window"""

	def __init__(self,buttonLabels,horizontal=True):
		self.hbox = gtk.HBox(homogeneous=False, spacing=0)
		self.horizontal = horizontal

		self.createButtons(buttonLabels)

		self.hbox.show_all()


	def createButtons(self,buttonLabels):
		self.buttons=[]

		if self.horizontal:
			for m in range(len(buttonLabels)):
				if m==0:
					newObject = gtk.RadioButton(None, buttonLabels[0])
				else:
					newObject = gtk.RadioButton(newObject, buttonLabels[m])

				self.hbox.pack_start(newObject,expand=False, fill=False)	
				self.buttons.append(newObject)
		else:
			print 'generic_gtk.py::RadioWidget::vertical'



######## Widget with a tick then an entry #######################################
class CheckEntryWidget:
	"""Widget made up of a check box then and entry box"""

	def __init__(self,initialParams=[False,'1.0'],horizontal=True):
		self.hbox = gtk.HBox(homogeneous=False, spacing=0)
		self.horizontal = horizontal

		self.createWidgets(initialParams)

		self.hbox.show_all()


	def createWidgets(self,params):
		if self.horizontal:
			self.chk = gtk.CheckButton(label=None, use_underline=True)
			self.chk.set_active(params[0])
			self.entry = gtk.Entry(max=0)
			self.entry.set_text(str(params[1]))

			self.hbox.pack_start(self.chk,expand=False, fill=False)
			self.hbox.pack_start(self.entry,expand=False, fill=False)

		else:
			print 'generic_gtk.py::RadioWidget::vertical'




##### WRAPPER WIDGET FOR CREATING AN EXPANDABLE CONTAINER
class ExpanderWidget:
	def __init__(self, widget, lbl=' Test', btn=gtk.STOCK_INDEX, setExpanded=True, parentWin=None):
		expander = gtk.Expander(None)
		hbox = gtk.HBox()
		image = gtk.Image()
		image.set_from_stock(btn, gtk.ICON_SIZE_BUTTON)
		label = gtk.Label(lbl)
		label.set_use_markup(True)
		hbox.pack_start(image)
		hbox.pack_start(label)

		expander.set_label_widget(hbox)
		self.expander=expander
		self.widget=widget
		self.parentWin=parentWin
		expander.add(self.widget)
		expander.set_expanded(setExpanded)

		expander.connect('notify::expanded', self.expanded_cb)

		return


#	def expanded_cb(self, expander, params, widget, parent):
#		if expander.get_expanded():
#			widget.show()
#			expander.add(widget)
#		else:
#			expander.remove(expander.child)
#			try:
#				parent.resize(100,100)
#			except:
#				pass
#		return


	def expanded_cb(self, expander, params):
		if expander.get_expanded():
			try:
				widget.show()
			except:
				pass
		else:
			try:
				widget.hide()
			except:
				pass

			self.parentWin.resize(300,300)

		return



##### WRAPPER WIDGET TO CREATE A TOOLBAR BUTTON WITH AN ASSOCIATED MENU
class MenuToolButtonWidget:
	"""This is a helper widget that creates a gtk.MenuToolButton widget populated 
           by menu items from a list. mnuBtn = MenuToolButtonWidget(menuList, icon=gtk.STOCK_OPEN)"""
	def __init__(self, menuList, icon=gtk.STOCK_OPEN, label=''):

		iconWid = gtk.image_new_from_stock(icon,gtk.ICON_SIZE_SMALL_TOOLBAR)

		self.btn=gtk.MenuToolButton(iconWid,label)
		self.menu=gtk.Menu()

		self.menuItems = []
		for x in menuList:
			self.menuItems.append(gtk.MenuItem(x))

		for x in self.menuItems:
			x.show()
			self.menu.append(x)

#		menuToolBtn.connect("clicked",printInfo,'FFT')
#		menuItem.connect("activate",printInfo,'FFT with phase')

		self.btn.set_menu(self.menu)
		self.menu.show()
		self.btn.show()



class NewDialog():
	"""Generic dialog class, used to show PlotDlg"""
	
	def __init__(self,parent,title='Select'):

		# make the dialog
		self.dlg = gtk.Dialog(title=title,parent=parent,flags=0,buttons=())
		self.dlg.set_position(gtk.WIN_POS_MOUSE)

		self.btnCancel = self.dlg.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
  		self.btnOk = self.dlg.add_button(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)
		self.btnOk.grab_default()

		self.vbox=gtk.VBox(homogeneous=False, spacing=0)
		self.dlg.get_content_area().pack_start(self.vbox)
		self.vbox.show()

	def add(self, widget):
		self.vbox.pack_start(widget,False,False)
		widget.show()

	def run(self):
		"""This function will show the dialog"""	
	
		#run the dialog and store the response		
		self.result = self.dlg.run()

		#we are done with the dialog, destroy it
		self.dlg.destroy()

		#return the result and the data
		if self.result == gtk.RESPONSE_ACCEPT:
			return 1
		else:
			return 0




######## generic toolbar class #######################################
class Toolbar:
	"""This is the toolbar class"""

	def __init__(self):

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
