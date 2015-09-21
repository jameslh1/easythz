#!/usr/bin/env python

# example notebook.py

import pygtk
pygtk.require('2.0')
import gtk



class TabbedContainer:
	def __init__(self,tabs=['Test 1','Test 2'],vboxList=[]):

#		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
#		window.connect("delete_event", self.delete)
#		window.set_border_width(10)

		table = gtk.Table(3,6,False)
#		window.add(table)

		# Create a new notebook, place the position of the tabs
		notebook = gtk.Notebook()
		notebook.set_tab_pos(gtk.POS_TOP)
		table.attach(notebook, 0,6,0,1)
		notebook.show()
		self.show_tabs = True
		self.show_border = True

		# Let's append a bunch of pages to the notebook
		for i in range(len(tabs)):
			if len(vboxList)==len(tabs):
				label = gtk.Label(tabs[i])
				notebook.append_page(vboxList[i], label)
			else:
				vbox=gtk.VBox()
				vbox.show()

				label = gtk.Label(tabs[i])
				notebook.append_page(vbox, label)

		# Set what page to start at (page 0)
		notebook.set_current_page(0)
#		notebook.connect("switch-page", self.pageChanged)

		# Create a bunch of buttons
		if 0:
			button = gtk.Button(stock=gtk.STOCK_CLOSE)
			button.connect("clicked", self.delete)
			table.attach(button, 0,1,1,2)
			button.show()

			button = gtk.Button("tab position")
			button.connect("clicked", self.rotate_book, notebook)
			table.attach(button, 3,4,1,2)
			button.show()

		table.show()
		self.notebook=notebook
		self.table=table
#		window.show()


	def append_page(self,vbox,label='New page'):
		labelWidget = gtk.Label(label)
		self.notebook.append_page(vbox, labelWidget)


	# This method rotates the position of the tabs
	def rotate_book(self, button, notebook):
		notebook.set_tab_pos((notebook.get_tab_pos()+1) %4)

	# Add/Remove the page tabs and the borders
	def tabsborder_book(self, button, notebook):
		tval = False
		bval = False
		if self.show_tabs == False:
			tval = True 
		if self.show_border == False:
			bval = True

		notebook.set_show_tabs(tval)
		self.show_tabs = tval
		notebook.set_show_border(bval)
		self.show_border = bval

	# Remove a page from the notebook
	def remove_book(self, button, notebook):
		page = notebook.get_current_page()
		notebook.remove_page(page)
		# Need to refresh the widget -- 
		# This forces the widget to redraw itself.
		notebook.queue_draw_area(0,0,-1,-1)

	def delete(self, widget, event=None):
		gtk.main_quit()
		return False

	def pageChanged(self, widget, page, page_num):
		self.currentPageNumber=page_num



def main():
	gtk.main()
	return 0



if __name__ == "__main__":

#	HOMEPATH='/home/james/'
	HOMEPATH='/home/lloydhughes/'
	import sys
	sys.path.append(HOMEPATH+'THz/code')		# necessary to import my libraries

	from src.paramWidget import *
	from src.generic_gtk import getWidgetValue, getParamValue


	####################################################################################
	#### example usage of TabbedContainer class: make a tabbed dialog (using NewDialog)

	result=0
	resultDict={}


	paramNames = ['Legend position','Transparency','Box','Shadow']
	paramTypes = ['cmb','en','chk','chk']
	paramDefaultValues = [['right','left'],'test',0,1]

	paramBoxes = ParamWidget(paramNames,paramTypes,paramDefaultValues)
	paramBoxes.vbox.show_all()

	# add all the default parameters to the results list
	for widget, name in zip(paramBoxes.objectList, paramNames):
		result = getWidgetValue(widget)
		resultDict[name]=result

	for x in range(len(paramBoxes.objectList)):
		if paramTypes[x]=='cmb':
			paramBoxes.objectList[x].connect("changed",getParamValue,paramNames[x],resultDict)
		elif paramTypes[x]=='chk':
			paramBoxes.objectList[x].connect("toggled",getParamValue,paramNames[x],resultDict)
		elif paramTypes[x]=='en':
			paramBoxes.objectList[x].connect("changed",getParamValue,paramNames[x],resultDict)


	paramNames2 = ['x label','show x=0']
	paramTypes2 = ['en','chk']
	paramDefaultValues2 = ['time',1]

	paramBoxes2 = ParamWidget(paramNames2,paramTypes2,paramDefaultValues2)
	paramBoxes2.vbox.show_all()

	# add all the default parameters to the results list
	for widget, name in zip(paramBoxes2.objectList, paramNames2):
		result = getWidgetValue(widget)
		resultDict[name]=result

	for x in range(len(paramBoxes2.objectList)):
		if paramTypes2[x]=='cmb':
			paramBoxes2.objectList[x].connect("changed",getParamValue,paramNames2[x],resultDict)
		elif paramTypes2[x]=='chk':
			paramBoxes2.objectList[x].connect("toggled",getParamValue,paramNames2[x],resultDict)
		elif paramTypes2[x]=='en':
			paramBoxes2.objectList[x].connect("changed",getParamValue,paramNames2[x],resultDict)



	t=TabbedContainer(tabs=['Legend','Axes'],vboxList=[paramBoxes.frame,paramBoxes2.frame])
	t.table.show_all()

	newDlg=NewDialog(None)
	newDlg.add(t.table)

	result=newDlg.run()

	print result, resultDict

	main()

