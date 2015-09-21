import pygtk
pygtk.require('2.0')
import gtk


######## generic window #######################################
class NewWindow:
	"""NewWindow
	      title='New Window'         title of the window
	      makeHbox=True              true for hbox; false for vbox
	      position=gtk.WIN_POS_NONE  no preferred window position (see gtk class for more)
              mainProg=False             True to run exit() & leave gtk.main(); False to avoid doing this
"""

	def __init__(self,makeHbox=True,title='New Window',position=gtk.WIN_POS_NONE,mainProg=False):
		self.mainProg=mainProg

		self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.win.set_position(position)
		self.deleteHandle = self.win.connect("delete_event", self.OnQuit)

		if makeHbox:
		        self.vbox = gtk.HBox(True, 0)
		else:	# make Vbox
		        self.vbox = gtk.VBox(False, 0)
		self.win.add(self.vbox)

		self.win.set_title(title)

	def addWidgetH(self,widget):
		self.handlebox = gtk.HandleBox()
		self.handlebox.add(widget)
		self.vbox.pack_start(self.handlebox, False, False, 5)
		self.win.show_all()


	def addWidget(self,widget):
		self.vbox.pack_start(widget, False, False, 5)
		self.win.show_all()



	def OnQuit(self, test1='',test2=''):
		try:
			self.win.destroy()
		except AttributeError:
			pass

		if self.mainProg:
			exit(1)



if __name__ == "__main__":
	n=NewWindow(mainProg=True)
	n.win.show_all()
	gtk.main()
