import pygtk
pygtk.require('2.0')
import gtk

import pango
from generic import *
from generic_gtk import *
from instrumentWidget import InstrumentWidget

######## main application window #######################################
class ParamWidget:
	"""This is the ParamWidget application"""

	def __init__(self,paramNames,paramTypes,paramDefaultValues,frameLabel=None):
		self.vbox= gtk.VBox(homogeneous=False, spacing=0)
		self.table = gtk.Table(2,2,False)

		self.objectList = []
		for x,y,z in zip(paramNames,paramTypes,paramDefaultValues):
			self.addObject(self.table,x,y,z)

		self.frame=gtk.Frame(label=frameLabel)
		self.frame.add(self.vbox)

		self.hbox = gtk.HBox(homogeneous=False, spacing=0)
		self.vbox.pack_start(self.hbox     ,expand=False, fill=True)
		self.vbox.pack_start(self.table)


	def addObject(self,table,labelStr,widgetType,defaultValue):
		newLabel  = gtk.Label(labelStr)
#		self.hbox.pack_start(newLabel,expand=False, fill=False)
		nrows=table.get_property('n-rows')
		table.attach(newLabel, 0, 1, nrows, nrows+1)

		if widgetType=='en':
			newObject = gtk.Entry(max=0)
			newObject.set_text(str(defaultValue))

		elif widgetType=='text':
			sw = gtk.ScrolledWindow()
			sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
			textview = gtk.TextView()
			newObject = textview.get_buffer()
			sw.add(textview)
			newObject.set_text(str(defaultValue))
			textview.set_wrap_mode(gtk.WRAP_WORD)

		elif widgetType=='spn':
#			adj = gtk.Adjustment(value, lower, upper, step_increment, page_increment, page_size)
		        adj = gtk.Adjustment(defaultValue, 0, 10000, 1, 5, 0.0)
		        newObject = gtk.SpinButton(adj, 0, 0)
		elif widgetType=='cmb':
			newObject = gtk.combo_box_new_text()
			for x in defaultValue:
				newObject.append_text(str(x))
			newObject.set_active(0)
		elif widgetType=='title':
			newLabel.modify_font(pango.FontDescription("sans 16"))
			newObject = gtk.ToggleButton('')
			newObject.set_active(True)
			iconw = gtk.Image() # icon widget
			iconw.set_from_stock(gtk.STOCK_GO_UP,gtk.ICON_SIZE_LARGE_TOOLBAR)
			newObject.set_image(iconw)	
		elif widgetType=='btn':
			newObject = gtk.Button(stock=defaultValue)
		elif widgetType=='iconbtn':
			newObject = IconButton(label=labelStr,icon=defaultValue)
		elif widgetType=='imagebtn':
			newObject = IconButton(label=None,icon=defaultValue,iconSize=gtk.ICON_SIZE_LARGE_TOOLBAR)
		elif widgetType=='lbl':
			newObject = gtk.Label(defaultValue)
			newObject.set_use_markup(True)
		elif widgetType=='chk':
			newObject = gtk.CheckButton(label=None, use_underline=True)
			newObject.set_active(int(defaultValue))
		elif widgetType=='chkEntry':   # chk box then an entry box
			newObject = CheckEntryWidget(initialParams=defaultValue,horizontal='True')
		elif widgetType=='radio':
			newObject = RadioWidget(defaultValue)
		elif widgetType == 'prog':			# progress bar
			newObject = gtk.ProgressBar(adjustment=None)
		elif widgetType == 'hscale':			# progress bar
			newObject = gtk.HScale(adjustment=None)
			newObject.set_digits(3)
			newObject.set_range(0,1)
			newObject.set_value(defaultValue)
		elif widgetType=='inst':
			newObject = InstrumentWidget(defaultValue,'')   # defaultValue = self.prm
		elif widgetType=='instS':
			newObject = InstrumentWidget(defaultValue,'',setCommands=True)   # defaultValue = self.prm
		elif widgetType=='instE':
			newObject = InstrumentWidget(defaultValue,'',entry=1)   # defaultValue = self.prm

		if (widgetType =='inst')|(widgetType =='instS')|(widgetType =='instE')|(widgetType == 'radio')|(widgetType == 'chkEntry'):
#			self.hbox.pack_start(newObject.hbox,expand=False, fill=False)
			table.attach(newObject.hbox, 1, 2, nrows, nrows+1)
		elif (widgetType =='text'):
#			self.hbox.pack_start(newObject.hbox,expand=False, fill=False)
			table.attach(sw, 1, 2, nrows, nrows+1)
		else:
#			self.hbox.pack_start(newObject,expand=False, fill=False)
			table.attach(newObject, 1, 2, nrows, nrows+1)


		self.objectList.append(newObject)


	def printValue(self,widget):
		result = getWidgetValue(widget)
		print result


