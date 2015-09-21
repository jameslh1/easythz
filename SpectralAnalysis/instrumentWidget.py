try:
	import pygtk
	pygtk.require("2.0")
except:
  	pass
  	
try:
	import gtk
except:
	sys.exit(1)
	
#from generic import *


######## instrument property widget #######################################
class InstrumentWidget:
	"""This is the generic instrument window"""

	def __init__(self, instrumentList, label='M1: ', entry=0, setCommands=False):
		self.instrumentList=instrumentList
		self.entry=entry

		self.hbox = gtk.HBox(homogeneous=False, spacing=0)
		self.createBoxes(label,setCommands)
		self.hbox.show_all()


	def createBoxes(self, label, setCommands):
		lbl   = gtk.Label(label)
		self.cmb1  = gtk.combo_box_new_text()
		self.cmb2  = gtk.combo_box_new_text()

		self.hbox.pack_start(lbl,expand=False, fill=False)
		self.hbox.pack_start(self.cmb1,expand=False, fill=False)
		self.hbox.pack_start(self.cmb2,expand=False, fill=False)

		self.en1 = gtk.Entry()
		if self.entry == 1:
			self.hbox.pack_start(self.en1,expand=False, fill=False)


		self.cmb1.append_text('Select instrument:')
		for x in self.instrumentList:
			if x.comType=='ethernet':
				comID='E'
				addrID=str(x.controllerAddress)+'_'+str(x.instrumentAddress)
			elif x.comType=='rs232':
				comID='S'
				addrID=str(x.controllerAddress)+'_'+str(x.instrumentAddress)
			elif x.comType=='gpib':
				comID='G'
				addrID=str(x.controllerAddress)+'_'+str(x.instrumentAddress)
			else:
				comID='?'
				addrID=''

			self.cmb1.append_text(x.name+' at '+comID+addrID)

		self.cmb1.connect('changed', self.changed_inst, setCommands)
		self.cmb1.set_active(0)

		self.cmb2.append_text('Select command:')
		self.handler_id = self.cmb2.connect('changed', self.changed_cmd)
		self.cmb2.set_active(0)



	def changed_inst(self, combobox, setCommands):
		model = self.cmb1.get_model()
		index = self.cmb1.get_active()

		if index:
			if setCommands:
				commandList = self.instrumentList[index-1].setCommands
			else:
				commandList = self.instrumentList[index-1].getCommands

			model2=self.cmb2.get_model()
			self.cmb2.disconnect(self.handler_id)
			model2.clear()
			self.cmb2.append_text('Select command:')
			self.cmb2.set_active(0)
#			self.enCommand.set_text('')
			self.handler_id = self.cmb2.connect('changed', self.changed_cmd)

#			for x in range(len(self.prm.commandDB.instruments)):	
#				searchtxt = model[index][0].split(' at ')[0]
##				print searchtxt
#				if searchtxt in self.prm.commandDB.instruments[x]:	
#					for y in range(len(self.prm.commandDB.commandStr[x])):
#						#print self.prm.commandDB.commandStr[x][y]
#						self.currCommandId = x
#						self.cmb2.append_text(self.prm.commandDB.commandStr[x][y])
			for x in commandList:
#					self.currCommandId = x
				self.cmb2.append_text(x)

		return


	def changed_cmd(self, combobox):
		model = self.cmb2.get_model()
		index = self.cmb2.get_active()
#		if index:
			#self.enCommand.set_text(self.prm.commandDB.commands[self.currCommandId][index-1])
#			print self.prm.commandDB.commands[self.currCommandId][index-1]
		return

	
