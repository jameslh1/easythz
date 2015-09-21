import pygtk
pygtk.require('2.0')
import gtk

#from src.plotWidget import CreatePlotWindow
import gobject
from sys import exit

from pylab import figure, plot, xlabel, ylabel, pi, exp
from numpy import array, fft, zeros

from plotsetup import *
from plotWidget2 import *

from transSpectraAnalysis import TransSpectraAnalysis

import os

import time

class SpectAnalysisGUI:

	# TARGETS are for drag and drop interface
	TARGETS = [
	    ('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),
	    ('text/plain', 0, 1),
	    ('TEXT', 0, 2),
	    ('STRING', 0, 3),
	    ]

	def __init__(self):

		# Get current date and time
		self.ascTime = time.asctime(time.localtime(time.time()))

		# Create new window
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

		self.window.set_title("Spectral Analysis 1.0")

		self.screenWidth = gtk.gdk.screen_width()
		self.screenHeight = gtk.gdk.screen_height()
		self.window.set_size_request(self.screenWidth/2, (9*self.screenHeight)/10)

		self.window.set_border_width(10)

		self.window.connect("delete_event", self.delete_event)

		# Create table to place widgets in
		table = gtk.Table(rows=10, columns=1, homogeneous=True)

		self.window.add(table)

		# Initialise the event log
		logTable = gtk.Table(rows=7, columns=10, homogeneous=True)

		# Add label for event log
		logLabel = gtk.Label(str='<b>Event Log</b>')
		logLabel.set_use_markup(True)
		logTable.attach(logLabel, 0, 1, 0, 1)

		# Set up display for event log text
		textview = gtk.TextView()
		textview.set_editable(False)
		textview.set_cursor_visible(False)
		textview.set_wrap_mode(gtk.WRAP_WORD)
		textview.set_justification(gtk.JUSTIFY_LEFT)

		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.add(textview)
		
		logTable.attach(sw, 0, 10, 1, 6)

		# Allow user to output or refresh the event log
		self.outputButton = gtk.Button(label='Output Log', stock=None)
		self.outputButton.connect('clicked', self.outputLog, 'Output Log')
		
		self.refreshButton = gtk.Button('Refresh Log', stock=None)
		self.refreshButton.connect('clicked', self.refreshLog, 'Refresh Log')

		logTable.attach(self.outputButton, 6, 8, 6, 7)
		logTable.attach(self.refreshButton, 8, 10, 6, 7)

		table.attach(logTable, 0, 1, 8, 10)

		# Start the log by printing the current time
		self.log = textview.get_buffer()
		self.log.set_text('Log started '+self.ascTime+'\n')

		# Start settting up data file dialogue
		self.fileTable = gtk.Table(rows = 21, columns=10, homogeneous=True)

		# Create a scrolled window to display added file's information
		self.fileSW = gtk.ScrolledWindow()
		self.fileSW.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.fileTable.attach(self.fileSW, 0, 10, 2, 21)

		style = self.fileSW.get_style()
		self.fileSW.modify_bg(gtk.STATE_NORMAL, style.white)

		# Default files window to displaying the message "No Files Added" in a white window
		noFilesLabel = gtk.Label(str='No Files Added')
		hbox = gtk.HBox()
		hbox.add(noFilesLabel)
		eb = gtk.EventBox()     
		eb.add(hbox)
		eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(65535, 65535, 65535))
		self.fileSW.add_with_viewport(eb)

		self.noFilesFlag = True
		
		# Add label
		fileTableLabel = gtk.Label(str='<b>Data Files</b>')
		fileTableLabel.set_use_markup(True)
		self.fileTable.attach(fileTableLabel, 0, 1, 0, 2)

		# Add Add File button
		self.getFileButton = gtk.Button('Add File')
		self.getFileButton.connect('clicked', self.getFile, 'Add File')

		self.fileTable.attach(self.getFileButton, 6, 8, 0, 2)

		# Add Remove All button
		self.removeAllButton = gtk.Button('Remove All')
		self.removeAllButton.connect('clicked', self.removeAllFiles, 'Remove All')

		self.fileTable.attach(self.removeAllButton, 8, 10, 0, 2)

		self.numFiles = 0    # Set up counter that will be used to label files when they are added
		self.files = []      # Stores sets of data loaded from files
	
		table.attach(self.fileTable, 0, 1, 0, 3)

		# Start settting up data file dialogue
		self.analysisTable = gtk.Table(rows = 35, columns=10, homogeneous=True)

		# Create a scrolled window to display added file's information
		self.analysisSW = gtk.ScrolledWindow()
		self.analysisSW.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.analysisTable.attach(self.analysisSW, 0, 10, 3, 34)

		style = self.analysisSW.get_style()
		self.analysisSW.modify_bg(gtk.STATE_NORMAL, style.white)

		# Default files window to displaying the message "No Files Added" in a white window
		noResultsLabel = gtk.Label(str='No Results Yet')
		hbox = gtk.HBox()
		hbox.add(noResultsLabel)
		eb = gtk.EventBox()     
		eb.add(hbox)
		eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(65535, 65535, 65535))
		self.analysisSW.add_with_viewport(eb)

		self.results = []   # Stores sets of results
		
		# Add label
		analysisTableLabel = gtk.Label(str='<b>Results</b>')
		analysisTableLabel.set_use_markup(True)
		self.analysisTable.attach(analysisTableLabel, 0, 1, 1, 3)

		# Add Do Analysis button
		self.doAnalysisButton = gtk.Button('Do Analysis')
		self.doAnalysisButton.connect('clicked', self.doAnalysis, 'Do Analysis')

		self.analysisTable.attach(self.doAnalysisButton, 4, 6, 1, 3)

		# Add Save All button.
		self.saveAllButton = gtk.Button('Output All')
		self.saveAllButton.connect('clicked', self.saveAll, 'Output All')

		self.analysisTable.attach(self.saveAllButton, 6, 8, 1, 3)

		# Add Remove All button
		self.removeAllButton2 = gtk.Button('Remove All')
		self.removeAllButton2.connect('clicked', self.removeAllAnalysis, 'Remove All')

		self.analysisTable.attach(self.removeAllButton2, 8, 10, 1, 3)

		self.results = []      # Stores results of analysis as tuples such that:
		                       # (description, plotting type, data1, data2, ..., (single-value quantities), ..., data1 descriptor, data2 descriptor, ...)
	
		table.attach(self.analysisTable, 0, 1, 3, 8)

		self.window.show_all()


	# Close the main window and quit
	def delete_event(self, widget, event, data=None):
		self.window.destroy()

		return False


	# Close the analysis window 
	def delete_event2(self, widget, event, data=None):
		self.analysisWin.destroy()

		return False

	# Outputs event log to the specified file. Uses a default file name otherwise.
	def outputLog(self, widget, event, data=None):

		# Allow user to choose file save location
		chooser = gtk.FileChooserDialog("Save data",
                                None,
                                  gtk.FILE_CHOOSER_ACTION_SAVE,
                                 (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                  gtk.STOCK_SAVE, gtk.RESPONSE_OK))
		chooser.set_default_response(gtk.RESPONSE_OK)
		chooser.set_select_multiple(False)

		# Suggest a file name to save as to the user
		chooser.set_current_name('Log_'+self.ascTime.replace(' ', '_')+'.txt')

		response = chooser.run()

		# Save current working directory to revert back to it afterwards
		cwd = os.getcwd()

		# Get the location and name of the data file
		fileName = ''
		location = ''
		if response == gtk.RESPONSE_OK:
			fileName = chooser.get_filename()
			location = chooser.get_current_folder()
			chooser.destroy()

			# Write data to the file at the specified location
			os.chdir(location)
			f = open(fileName, 'w')
			f.write(self.log.get_text(self.log.get_start_iter(), self.log.get_end_iter()))
			f.close()

			# Go back to the previous working directory
			os.chdir(cwd)

			# Update Log
			self.log.set_text(self.log.get_text(self.log.get_start_iter(), self.log.get_end_iter()) +
		           	                                              '\n'+'Log outputted to ' + location)
	
		elif response == gtk.RESPONSE_CANCEL:
			chooser.destroy()


	# Clears the event log and starts a new one. Does not save existing log
	def refreshLog(self, widget, event, data=None):

		self.ascTime = time.asctime(time.localtime(time.time()))

		self.log.set_text('Log started '+self.ascTime+'\n')


	# Allows user to add a file via a dialogue
	def getFile(self, widget, event, data=None):

		# Set up the file chooser dialog
		chooser = gtk.FileChooserDialog("Add data File",
                                None,
                                  gtk.FILE_CHOOSER_ACTION_OPEN,
                                 (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                  gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		chooser.set_default_response(gtk.RESPONSE_OK)
		chooser.set_select_multiple(False)

		response = chooser.run()

		# Get the location and name of the data file
		fileName = ''
		location = ''
		if response == gtk.RESPONSE_OK:
			fileName = chooser.get_filename()
			location = chooser.get_current_folder()
			chooser.destroy()

			# Implement the "Data" class to load and store the data in the file
			self.numFiles += 1
			label = self.numFiles
			data = Data(fileName, location, label)

			self.files.append(data)
			self.updateFilesTable()

			self.log.set_text(self.log.get_text(self.log.get_start_iter(), self.log.get_end_iter()) + 
				          '\n' + 'File ' + data.fileName + ' loaded from ' + data.location +
				          '. Label: f' + str(data.fileLabel) + ', Columns: ' + str(data.numCols) + '.')

		elif response == gtk.RESPONSE_CANCEL:
			chooser.destroy()

		

	# Sets the files dialogue to containing the message 'No files Added' and clears it
	def dispNoFilesLabel(self):

		self.fileSW.remove(self.fileSW.get_child())

		noFilesLabel = gtk.Label(str='No Files Added')
		hbox = gtk.HBox()
		hbox.add(noFilesLabel)
		eb = gtk.EventBox()     
		eb.add(hbox)
		eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(65535, 65535, 65535))

		self.fileSW.add_with_viewport(eb)
		self.noFilesFlag = True

		self.window.show_all()

		# Update log
		self.log.set_text(self.log.get_text(self.log.get_start_iter(), self.log.get_end_iter()) + 
		                  '\n' + 'Data Files table cleared')


	def updateFilesTable(self):
		
		self.fileSW.remove(self.fileSW.get_child())

		numFiles = len(self.files)

		if numFiles < 7:
			numRows = 8
		else:
			numRows = numFiles + 1

		fileTable = gtk.Table(rows=numRows, columns=5, homogeneous=True)
		fileTable.set_row_spacings(2)

		Shade = 50000    # Shade of grey for title boxes
		# Title box for 'File' column
		title1 = gtk.Label(str='File Name')
		hbox = gtk.HBox()
		hbox.add(title1)
		eb1 = gtk.EventBox()     
		eb1.add(hbox)
		eb1.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(Shade, Shade, Shade))

		# Title box for 'File Label' column
		title2 = gtk.Label(str='File Label')
		hbox = gtk.HBox()
		hbox.add(title2)
		eb2 = gtk.EventBox()     
		eb2.add(hbox)
		eb2.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(Shade, Shade, Shade))

		# Title box for 'Num Columns' column
		title3 = gtk.Label(str='Num Columns')
		hbox = gtk.HBox()
		hbox.add(title3)
		eb3 = gtk.EventBox()     
		eb3.add(hbox)
		eb3.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(Shade, Shade, Shade))

		# Title box for 'Remove' column
		title4 = gtk.Label(str='Remove')
		hbox = gtk.HBox()
		hbox.add(title4)
		eb4 = gtk.EventBox()     
		eb4.add(hbox)
		eb4.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(Shade, Shade, Shade))
	
		fileTable.attach(eb1, 0, 2, 0, 1)
		fileTable.attach(eb2, 2, 3, 0, 1)
		fileTable.attach(eb3, 3, 4, 0, 1)
		fileTable.attach(eb4, 4, 5, 0, 1)

		# Add each data file loaded to the table
		counter = 1
		for data in self.files:
			# File Name column
			fileName = gtk.Label(str=data.fileName)
			fileTable.attach(fileName, 0, 2, counter, counter+1)

			# File Label column
			fileLabel = gtk.Label(str='f'+str(data.fileLabel))
			fileTable.attach(fileLabel, 2, 3, counter, counter+1)

			# Num Columns column
			numCols = gtk.Label(str=str(data.numCols))
			fileTable.attach(numCols, 3, 4, counter, counter+1)

			# Remove buttons column
			removeButton = gtk.Button('Remove', stock=None)
			removeButton.connect('clicked', self.removeFile, 'Remove', counter-1)
			fileTable.attach(removeButton, 4, 5, counter, counter+1)

			counter += 1


		self.fileSW.add_with_viewport(fileTable)
		self.window.show_all()


	# Removes a file from the Data Files table
	def removeFile(self, widget, event, filePos):
		
		fileName = self.files[filePos].fileName	

		self.files.pop(filePos)
		self.updateFilesTable()

		self.log.set_text(self.log.get_text(self.log.get_start_iter(), self.log.get_end_iter()) + 
		                  '\n' + 'File ' + fileName + ' removed from the Data Files list.')


	# Removes all files from the Data Files table
	def removeAllFiles(self, widget, event, data=None):
		
		self.files = []
		self.dispNoFilesLabel()


	# Brings up the analysis window for the user to specify what results they want
	def doAnalysis(self, widget, event, data=None):

		# Create a new analysis window if one does not already exist
		if not hasattr(self, 'analysisWin'):
			self.analysisWin = gtk.Window(gtk.WINDOW_TOPLEVEL)

			self.analysisWin.set_title("Do Analysis")
			self.analysisWin.set_size_request(self.screenWidth/4, (3*self.screenHeight)/10)
			self.analysisWin.set_border_width(10)

			self.analysisWin.connect("delete_event", self.delete_doAnalysis)

			# Create table to place widgets in
			self.analysisTable2 = gtk.Table(rows=10, columns=5, homogeneous=True)
			self.analysisWin.add(self.analysisTable2)

			# Title for column indicationg possible types of analysis
			self.analysisLabel = gtk.Label(str='<b>Analysis</b>')
			self.analysisLabel.set_use_markup(True)
			self.analysisTable2.attach(self.analysisLabel, 0, 3, 0, 1)

			# Add labels to the column
			justPlotLabel = gtk.Label(str='Just Plot!')
			self.analysisTable2.attach(justPlotLabel, 0, 3, 1, 2)

			fourierLabel = gtk.Label(str='Fourier transform')
			self.analysisTable2.attach(fourierLabel, 0, 3, 2, 3)

			gaborLabel = gtk.Label(str='Gabor transform')
			self.analysisTable2.attach(gaborLabel, 0, 3, 3, 4)

			simTransLabel = gtk.Label(str='Simulate Transmission')
			self.analysisTable2.attach(simTransLabel, 0, 3, 4, 5)	

			transLabel = gtk.Label(str='Transmission/Refractive Index')
			self.analysisTable2.attach(transLabel, 0, 3, 5, 6)	

			# Add 'add' buttons
			self.justPlotAddButton = gtk.Button('Add')
			self.justPlotAddButton.connect('clicked', self.justPlotAdd, 'Add')
			self.analysisTable2.attach(self.justPlotAddButton, 3, 5, 1, 2)

			self.fourierAddButton = gtk.Button('Add')
			self.fourierAddButton.connect('clicked', self.fourierAdd, 'Add')
			self.analysisTable2.attach(self.fourierAddButton, 3, 5, 2, 3)

			self.gaborAddButton = gtk.Button('Add')
			self.gaborAddButton.connect('clicked', self.gaborAdd, 'Add')
			self.analysisTable2.attach(self.gaborAddButton, 3, 5, 3, 4)

			self.simTransAddButton = gtk.Button('Add')
			self.simTransAddButton.connect('clicked', self.simTransAdd, 'Add')
			self.analysisTable2.attach(self.simTransAddButton, 3, 5, 4, 5)

			self.transAddButton = gtk.Button('Add')
			self.transAddButton.connect('clicked', self.transAdd, 'Add')
			self.analysisTable2.attach(self.transAddButton, 3, 5, 5, 6)

			self.analysisWin.show_all()

	def delete_doAnalysis(self, widget, event, data=None):
		self.analysisWin.destroy()

		return False
		

	# Saves all the files to a folder under default names
	def saveAll(self, widget, event, data=None):

		# Allow user to choose file save location
		chooser = gtk.FileChooserDialog("Save data",
                                None,
                                  gtk.FILE_CHOOSER_ACTION_SAVE,
                                 (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                  gtk.STOCK_SAVE, gtk.RESPONSE_OK))
		chooser.set_default_response(gtk.RESPONSE_OK)
		chooser.set_select_multiple(False)

		# Suggest a file name to save as to the user
		chooser.set_current_name('Spectral Analysis Output')

		response = chooser.run()

		# Save current working directory to revert back to it afterwards
		cwd = os.getcwd()

		# Get the location and name of the data file
		fileName = ''
		location = ''
		if response == gtk.RESPONSE_OK:
			folderName = chooser.get_filename()
			location = chooser.get_current_folder()
			chooser.destroy()

			# Make folder to output analysis to
			folderLocation = location + '/' + folderName.replace(location + '/', '')
			os.makedirs(folderLocation)

			# Write data files to the specified location
			os.chdir(folderLocation)

			for result in self.results:
				# Create file to output results to
				f = open(result[0].replace(' ', '_') + '.txt', 'w')

				# Calculate number of columns in output file from length of results tuple
				numCols = len(result)/2 - 1

				# Use first line of file for column labels
				labels = result[-1]
				j = 1
				while j < numCols:
					j += 1
					labels = result[-j] + ', ' + labels

				# Stick with convention of expecting a % at the start of comment lines
				labels = '% ' + labels
		
				f.write(labels)

				# Write data to the file
				j = 0
				rows = len(result[2])   # Use length of first data set to deduce number of rows
				while j < rows:
					row = '\n'
					for data in result[2:numCols+2]:
						if row == '\n':
							row += str(data[j])
						else:
							row += '\t' + str(data[j])

					j += 1
					f.write(row)

				f.close()
		
				self.log.set_text(self.log.get_text(self.log.get_start_iter(), self.log.get_end_iter()) + 
						  '\n' + 'Result' + result[0] + ' saved to ' + folderLocation + ' as ' + 
					          result[0].replace(' ', '_') + '.txt.')

		elif response == gtk.RESPONSE_CANCEL:
			chooser.destroy()

		# Go back to the previous working directory
		os.chdir(cwd)


	# Removes all analysis produced from the Results table
	def removeAllAnalysis(self):

		# Delete all results held in the self.results array
		self.results = []

		# Default files window to displaying the message "No Files Added" in a white window
		noResultsLabel = gtk.Label(str='No Results Yet')
		hbox = gtk.HBox()
		hbox.add(noResultsLabel)
		eb = gtk.EventBox()     
		eb.add(hbox)
		eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(65535, 65535, 65535))

		self.analysisSW.remove(self.analysisSW.get_child())
		self.analysisSW.add_with_viewport(eb)

		self.window.show_all()


	# Opens plotting dialogue that allows the user to plot multiple data sets on the same axis
	def justPlotAdd(self, widget, event, data=None):
		print 'gggds'

	# Data entry fields to idicate data to be Fourier transformed
	def fourierAdd(self, widget, event, data=None):
		
		self.fourierAddWin = gtk.Window(gtk.WINDOW_TOPLEVEL)

		self.fourierAddWin.set_title("Fourier Transform data")
		self.fourierAddWin.set_size_request(self.screenWidth/3, self.screenHeight/5)
		self.fourierAddWin.set_border_width(10)

		self.fourierAddWin.connect("delete_event", self.delete_fourierAdd)

		# Create table to place widgets in
		self.fourierAddTable = gtk.Table(rows=6, columns=4, homogeneous=True)
		self.fourierAddWin.add(self.fourierAddTable)

		# Add comboBox
		self.fourierCB = gtk.combo_box_new_text()
		self.fourierCB.append_text('Fourier transform')
		self.fourierCB.append_text('Inverse Fourier transform')
		self.fourierCB.set_active(0)
		self.fourierCB.connect('changed', self.fourierCBChanged)
		self.fourierAddTable.attach(self.fourierCB, 0, 2, 1, 2)

		# Add labels
		xDataLabel = gtk.Label(str='x data:')
		self.fourierAddTable.attach(xDataLabel, 0, 1, 2, 3)

		yDataLabel = gtk.Label(str='y data:')
		self.fourierAddTable.attach(yDataLabel, 0, 1, 3, 4)

		xScaleLabel = gtk.Label(str='Scale data by:')
		self.fourierAddTable.attach(xScaleLabel, 2, 3, 2, 3)

		yScaleLabel = gtk.Label(str='Scale data by:')
		self.fourierAddTable.attach(yScaleLabel, 2, 3, 3, 4)

		# Add entry fields for user input
		self.fourierXDataEntry = gtk.Entry(max=0)
		self.fourierXDataEntry.set_text('')
		self.fourierAddTable.attach(self.fourierXDataEntry, 1, 2, 2, 3)

		self.fourierYDataEntry = gtk.Entry(max=0)
		self.fourierYDataEntry.set_text('')
		self.fourierAddTable.attach(self.fourierYDataEntry, 1, 2, 3, 4)

		self.fourierScaleXEntry = gtk.Entry(max=0)
		self.fourierScaleXEntry.set_text('1')
		self.fourierAddTable.attach(self.fourierScaleXEntry, 3, 4, 2, 3)

		self.fourierScaleYEntry = gtk.Entry(max=0)
		self.fourierScaleYEntry.set_text('1')
		self.fourierAddTable.attach(self.fourierScaleYEntry, 3, 4, 3, 4)

		# Add 'Cancel' button
		self.fourierCancelButton = gtk.Button('Cancel')
		self.fourierCancelButton.connect('clicked', self.fourierCancel, 'Cancel')
		self.fourierAddTable.attach(self.fourierCancelButton, 0, 2, 5, 6)

		# Add 'Add' button
		self.fourierDoneButton = gtk.Button('Done')
		self.fourierDoneButton.connect('clicked', self.fourierDone, 'Done')
		self.fourierAddTable.attach(self.fourierDoneButton, 2, 4, 5, 6)

		self.fourierAddWin.show_all()


	# Dialogue window to enter info necessary to perform Gabor transformations
	def gaborAdd(self, widget, event, data=None):
		
		self.gaborAddWin = gtk.Window(gtk.WINDOW_TOPLEVEL)

		self.gaborAddWin.set_title("Gabor Tranform data")
		self.gaborAddWin.set_size_request(self.screenWidth/3, self.screenHeight/5)
		self.gaborAddWin.set_border_width(10)

		self.gaborAddWin.connect("delete_event", self.delete_gaborAdd)

		# Create table to place widgets in
		self.gaborAddTable = gtk.Table(rows=6, columns=4, homogeneous=True)
		self.gaborAddWin.add(self.gaborAddTable)
		
		# Add labels
		timeDataLabel = gtk.Label(str='Time data:')
		self.gaborAddTable.attach(timeDataLabel, 0, 1, 1, 2)

		signalDataLabel = gtk.Label(str='Signal data:')
		self.gaborAddTable.attach(signalDataLabel, 0, 1, 2, 3)

		timeScaleLabel = gtk.Label(str='Scale data by:')
		self.gaborAddTable.attach(timeScaleLabel, 2, 3, 1, 2)

		signalScaleLabel = gtk.Label(str='Scale data by:')
		self.gaborAddTable.attach(signalScaleLabel, 2, 3, 2, 3)

		gaborStdDevLabel = gtk.Label(str='Std dev:')
		self.gaborAddTable.attach(gaborStdDevLabel, 0, 1, 3, 4)

		gaborTimeOffsetLabel = gtk.Label(str='Time offset:')
		self.gaborAddTable.attach(gaborTimeOffsetLabel, 2, 3, 3, 4)

		# Add entry fields for user input
		self.gaborTimeDataEntry = gtk.Entry(max=0)
		self.gaborTimeDataEntry.set_text('')
		self.gaborAddTable.attach(self.gaborTimeDataEntry, 1, 2, 1, 2)

		self.gaborSignalDataEntry = gtk.Entry(max=0)
		self.gaborSignalDataEntry.set_text('')
		self.gaborAddTable.attach(self.gaborSignalDataEntry, 1, 2, 2, 3)

		self.gaborScaleTimeEntry = gtk.Entry(max=0)
		self.gaborScaleTimeEntry.set_text('1')
		self.gaborAddTable.attach(self.gaborScaleTimeEntry, 3, 4, 1, 2)

		self.gaborScaleSignalEntry = gtk.Entry(max=0)
		self.gaborScaleSignalEntry.set_text('1')
		self.gaborAddTable.attach(self.gaborScaleSignalEntry, 3, 4, 2, 3)

		self.gaborStdDevEntry = gtk.Entry(max=0)
		self.gaborStdDevEntry.set_text('1')
		self.gaborAddTable.attach(self.gaborStdDevEntry, 1, 2, 3, 4)

		self.gaborTimeOffsetEntry = gtk.Entry(max=0)
		self.gaborTimeOffsetEntry.set_text('0')
		self.gaborAddTable.attach(self.gaborTimeOffsetEntry, 3, 4, 3, 4)

		# Add 'Cancel' button
		self.gaborCancelButton = gtk.Button('Cancel')
		self.gaborCancelButton.connect('clicked', self.gaborCancel, 'Cancel')
		self.gaborAddTable.attach(self.gaborCancelButton, 0, 2, 5, 6)

		# Add 'Add' button
		self.gaborDoneButton = gtk.Button('Done')
		self.gaborDoneButton.connect('clicked', self.gaborDone, 'Done')
		self.gaborAddTable.attach(self.gaborDoneButton, 2, 4, 5, 6)

		self.gaborAddWin.show_all()

###############################################################################################

	# Creates dialogue window where data can be inputted to calculate the transmission 
	# spectrum of a single-layer material. Can then estimate other material properties
	# such as the frequecy dependence of its refractive index and its thickness
	def simTransAdd(self, widget, event, data=None):

		self.simTransAddWin = gtk.Window(gtk.WINDOW_TOPLEVEL)

		self.simTransAddWin.set_title("Simulate Transmission")
		self.simTransAddWin.set_size_request((2*self.screenWidth)/3, (13*self.screenHeight)/30)
		self.simTransAddWin.set_border_width(10)

		self.simTransAddWin.connect("delete_event", self.delete_simTransAdd)

		# Create table to place widgets in
		self.simTransAddTable = gtk.Table(rows=14, columns=8, homogeneous=True)
		self.simTransAddWin.add(self.simTransAddTable)

		# Create a list to store layers
		self.layers = []

		# Create a scrolled window to display added layers' information
		self.layerSW = gtk.ScrolledWindow()
		self.layerSW.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.simTransAddTable.attach(self.layerSW, 4, 8, 1, 12)

		style = self.layerSW.get_style()
		self.layerSW.modify_bg(gtk.STATE_NORMAL, style.white)

		# Default layers scroll window to displaying the message "No Files Added" in a white window
		noLayersLabel = gtk.Label(str='No Layers Added')
		hbox = gtk.HBox()
		hbox.add(noLayersLabel)
		eb = gtk.EventBox()     
		eb.add(hbox)
		eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(65535, 65535, 65535))
		self.layerSW.add_with_viewport(eb)

		# Add choose material comboBox. Default to custom material.
		self.simTransMaterialCB = gtk.combo_box_new_text()
		self.simTransMaterialCB.append_text('Custom')
		self.simTransMaterialCB.set_active(0)
		self.simTransMaterialCB.connect('changed', self.simTransMaterialCBChanged)
		self.simTransAddTable.attach(self.simTransMaterialCB, 1, 3, 1, 2)

		# Add labels
		chooseMaterialLabel = gtk.Label(str='Material:')
		self.simTransAddTable.attach(chooseMaterialLabel, 0, 1, 1, 2)

		nameLabel = gtk.Label(str='Layer name:')
		self.simTransAddTable.attach(nameLabel, 0, 1, 3, 4)
		
		modelLabel = gtk.Label(str='Model:')
		self.simTransAddTable.attach(modelLabel, 0, 1, 4, 5)

		# Add text entry for layer name
		self.simTransLayerNameEntry = gtk.Entry(max=0)
		self.simTransLayerNameEntry.set_text('Layer' + str(len(self.layers)+1))
		self.simTransAddTable.attach(self.simTransLayerNameEntry, 1, 3, 3, 4)

		# Creat comboBox defaulting to 'custom' layer interface
		self.simTransLayerCB = gtk.combo_box_new_text()
		self.simTransLayerCB.append_text('Custom')
		self.simTransLayerCB.set_active(0)
		self.simTransLayerCB.connect('changed', self.simTransLayerCBChanged)
		self.simTransAddTable.attach(self.simTransLayerCB, 1, 3, 4, 5)

		# Get real and imaginary parts of the refractive index:
		# Add labels
		realLabel = gtk.Label(str='Real refrac idx:')
		self.simTransAddTable.attach(realLabel, 0, 1, 6, 7)

		imagLabel = gtk.Label(str='Imag refrac idx:')
		self.simTransAddTable.attach(imagLabel, 0, 1, 7, 8)

		realScaleLabel = gtk.Label(str='Scale data by:')
		self.simTransAddTable.attach(realScaleLabel, 2, 3, 6, 7)

		imagScaleLabel = gtk.Label(str='Scale data by:')
		self.simTransAddTable.attach(imagScaleLabel, 2, 3, 7, 8)

		# Add entry fields for user input
		self.simTransRealDataEntry = gtk.Entry(max=0)
		self.simTransRealDataEntry.set_text('')
		self.simTransAddTable.attach(self.simTransRealDataEntry, 1, 2, 6, 7)

		self.simTransImagDataEntry = gtk.Entry(max=0)
		self.simTransImagDataEntry.set_text('')
		self.simTransAddTable.attach(self.simTransImagDataEntry, 1, 2, 7, 8)

		self.simTransScaleRealEntry = gtk.Entry(max=0)
		self.simTransScaleRealEntry.set_text('1')
		self.simTransAddTable.attach(self.simTransScaleRealEntry, 3, 4, 6, 7)

		self.simTransScaleImagEntry = gtk.Entry(max=0)
		self.simTransScaleImagEntry.set_text('1')
		self.simTransAddTable.attach(self.simTransScaleImagEntry, 3, 4, 7, 8)

		# Add Labels for other input


		# Add entry fields for other input

		# Add 'Add Layer' button
		self.simTransAddLayerButton = gtk.Button('Add Layer')
		self.simTransAddLayerButton.connect('clicked', self.simTransAddLayer, 'Add Layer')
		self.simTransAddTable.attach(self.simTransAddLayerButton, 0, 4, 11, 12)

		# Add 'Add Material' button, label and comboBox
		self.simTransAddMaterialButton = gtk.Button('Add Material')
		self.simTransAddMaterialButton.connect('clicked', self.simTransAddMaterial, 'Add Material')
		self.simTransAddTable.attach(self.simTransAddMaterialButton, 3, 4, 12, 13)
		
		addMaterialLabel = gtk.Label(str='Select Material:')
		self.simTransAddTable.attach(addMaterialLabel, 0, 1, 12, 13)

		self.simTransAddMaterialCB = gtk.combo_box_new_text()
		self.simTransAddMaterialCB.append_text('safdsdsafdsa')   #FLAG
		self.simTransAddMaterialCB.set_active(0)
		self.simTransAddTable.attach(self.simTransAddMaterialCB, 1, 3, 12, 13)

		# Add 'Choose model' comboBox and label
		chooseModelLabel = gtk.Label(str='Choose Model:')
		self.simTransAddTable.attach(chooseModelLabel, 0, 1, 13, 14)

		self.simTransChooseModelCB = gtk.combo_box_new_text()
		self.simTransChooseModelCB.append_text('simTrans Thin')
		self.simTransChooseModelCB.append_text('simTrans Thick')
		self.simTransChooseModelCB.set_active(0)
		self.simTransAddTable.attach(self.simTransChooseModelCB, 1, 3, 13, 14)

		# Add 'Cancel' button
		self.simTransCancelButton = gtk.Button('Cancel')
		self.simTransCancelButton.connect('clicked', self.simTransCancel, 'Cancel')
		self.simTransAddTable.attach(self.simTransCancelButton, 4, 6, 13, 14)

		# Add 'Add' button
		self.simTransDoneButton = gtk.Button('Done')
		self.simTransDoneButton.connect('clicked', self.simTransDone, 'Done')
		self.simTransAddTable.attach(self.simTransDoneButton, 6, 8, 13, 14)

		self.simTransAddWin.show_all()

############################################################################################

	# Creates dialogue window where data can be inputted to calculate the transmission 
	# spectrum of a single-layer material. Can then estimate other material properties
	# such as the frequecy dependence of its refractive index and its thickness
	def transAdd(self, widget, event, data=None):

		self.transAddWin = gtk.Window(gtk.WINDOW_TOPLEVEL)

		self.transAddWin.set_title("Transmission/Refractive Index spectra")
		self.transAddWin.set_size_request(self.screenWidth/3, (4*self.screenHeight)/15)
		self.transAddWin.set_border_width(10)

		self.transAddWin.connect("delete_event", self.delete_transAdd)

		# Create table to place widgets in
		self.transAddTable = gtk.Table(rows=8, columns=4, homogeneous=True)
		self.transAddWin.add(self.transAddTable)

		# Add comboBox for user to choose model from
		self.transCB = gtk.combo_box_new_text()
		self.transCB.append_text('Thin film')
		self.transCB.append_text('Thick film')
		self.transCB.append_text('Both Models')
		self.transCB.set_active(2)
		self.transCB.connect('changed', self.transCBChanged)
		self.transAddTable.attach(self.transCB, 0, 2, 1, 2)

		# Add tickbox to give user option of thickness being calculated
		self.transTickButton = gtk.CheckButton(label='Estimate thickness')
		self.transTickButton.set_active(True)
		hBox = gtk.HBox()
		hBox.pack_end(self.transTickButton, fill=False)
		self.transAddTable.attach(hBox, 2, 4, 1, 2)

		# Add labels
		xDataLabel = gtk.Label(str='Time data:')
		self.transAddTable.attach(xDataLabel, 0, 1, 2, 3)

		yDataLabel = gtk.Label(str='Signal data:')
		self.transAddTable.attach(yDataLabel, 0, 1, 3, 4)

		xScaleLabel = gtk.Label(str='Scale data by:')
		self.transAddTable.attach(xScaleLabel, 2, 3, 2, 3)

		yScaleLabel = gtk.Label(str='Scale data by:')
		self.transAddTable.attach(yScaleLabel, 2, 3, 3, 4)

		refXDataLabel = gtk.Label(str='Ref. Time data:')
		self.transAddTable.attach(refXDataLabel, 0, 1, 4, 5)

		refYDataLabel = gtk.Label(str='Ref. Signal data:')
		self.transAddTable.attach(refYDataLabel, 0, 1, 5, 6)

		refXScaleLabel = gtk.Label(str='Scale data by:')
		self.transAddTable.attach(refXScaleLabel, 2, 3, 4, 5)

		refYScaleLabel = gtk.Label(str='Scale data by:')
		self.transAddTable.attach(refYScaleLabel, 2, 3, 5, 6)

		# Add entry fields for user input
		self.transXDataEntry = gtk.Entry(max=0)
		self.transXDataEntry.set_text('')
		self.transAddTable.attach(self.transXDataEntry, 1, 2, 2, 3)

		self.transYDataEntry = gtk.Entry(max=0)
		self.transYDataEntry.set_text('')
		self.transAddTable.attach(self.transYDataEntry, 1, 2, 3, 4)

		self.transScaleXEntry = gtk.Entry(max=0)
		self.transScaleXEntry.set_text('1')
		self.transAddTable.attach(self.transScaleXEntry, 3, 4, 2, 3)

		self.transScaleYEntry = gtk.Entry(max=0)
		self.transScaleYEntry.set_text('1')
		self.transAddTable.attach(self.transScaleYEntry, 3, 4, 3, 4)

		self.refTransXDataEntry = gtk.Entry(max=0)
		self.refTransXDataEntry.set_text('')
		self.transAddTable.attach(self.refTransXDataEntry, 1, 2, 4, 5)

		self.refTransYDataEntry = gtk.Entry(max=0)
		self.refTransYDataEntry.set_text('')
		self.transAddTable.attach(self.refTransYDataEntry, 1, 2, 5, 6)

		self.refTransScaleXEntry = gtk.Entry(max=0)
		self.refTransScaleXEntry.set_text('1')
		self.transAddTable.attach(self.refTransScaleXEntry, 3, 4, 4, 5)

		self.refTransScaleYEntry = gtk.Entry(max=0)
		self.refTransScaleYEntry.set_text('1')
		self.transAddTable.attach(self.refTransScaleYEntry, 3, 4, 5, 6)

		# Add 'Cancel' button
		self.transCancelButton = gtk.Button('Cancel')
		self.transCancelButton.connect('clicked', self.transCancel, 'Cancel')
		self.transAddTable.attach(self.transCancelButton, 0, 2, 7, 8)

		# Add 'Add' button
		self.transDoneButton = gtk.Button('Done')
		self.transDoneButton.connect('clicked', self.transDone, 'Done')
		self.transAddTable.attach(self.transDoneButton, 2, 4, 7, 8)

		self.transAddWin.show_all()


	def delete_fourierAdd(self, widget, event, data=None):
		self.fourierAddWin.destroy()

		return False


	def delete_gaborAdd(self, widget, event, data=None):
		self.gaborAddWin.destroy()

		return False


	def delete_transAdd(self, widget, event, data=None):
		self.transAddWin.destroy()

		return False


	def delete_simTransAdd(self, widget, event, data=None):
		self.simTransAddWin.destroy()

		return False


	# Closes the Fourier transformation data entry window
	def fourierCancel(self, widget, event, data=None):

		self.fourierAddWin.destroy()


	# Closes the Gabor transformation data entry window
	def gaborCancel(self, widget, event, data=None):

		self.gaborAddWin.destroy()


	# Closes the transmission spectra data entry window
	def transCancel(self, widget, event, data=None):

		self.transAddWin.destroy()


	# Closes the transmission simulation data entry window
	def simTransCancel(self, widget, event, data=None):

		self.simTransAddWin.destroy()


	# Dummy method
	def fourierCBChanged(self, widget, data=None):

		return


	# Dummy method
	def transCBChanged(self, widget, data=None):

		return


	# Changes transmission simulation GUI interface depending on material selected
	def simTransMaterialCBChanged(self, widget, data=None):
		print 'FLAG FLAG FLAG'

		return


	# Changes transmission simulation GUI interface depending on layer selected
	def simTransLayerCBChanged(self, widget, data=None):
		print 'FLAG FLAG FLAG'

		return

	
	# Adds layer to the layer list and resets GUI ready for addition of next layer
	def simTransAddLayer(self, widget, data=None):
		print 'FLAG FLAG FLAG'

	# Adds layers of one of the default materials to the layer list and resets GUI ready for addition of next layer
	def simTransAddMaterial(self, widget, data=None):
		print 'FLAG FLAG FLAG'


	# Fourier transforms supplied data and adds it to the results dialogue
	# it then closes the data entry window
	# Note that what is labelled as an FFT is an IFFT according to numpy and vice versa
	def fourierDone(self, widget, event, data=None):

		# Get the x data
		xDataStr = self.fourierXDataEntry.get_text()
		cLoc = xDataStr.find('c')
		fLoc = xDataStr.find('f')
		fileNum = int(xDataStr[fLoc+1:cLoc])
		colNum = int(xDataStr[cLoc+1:])

		j = 0
		while self.files[j].fileLabel != fileNum:
			j += 1

		xData = self.files[j].data[colNum-1]

		# Flip data set if commanded
		if xDataStr.find('FLIP') != -1:
			xData = xData[::-1]

		# Get the y data
		yDataStr = self.fourierYDataEntry.get_text()
		cLoc = yDataStr.find('c')
		fLoc = yDataStr.find('f')
		fileNum2 = int(yDataStr[fLoc+1:cLoc])
		colNum2 = int(yDataStr[cLoc+1:])

		j = 0
		while self.files[j].fileLabel != fileNum2:
			j += 1

		y = self.files[j].data[colNum2-1]

		# Flip data set if commanded
		if yDataStr.find('FLIP') != -1:
			y = y[::-1]

		# Scale the data sets
		yScale = float(self.fourierScaleYEntry.get_text())
		ydata = zeros(len(y))
		for j in range(len(y)):
			ydata[j] = float(y[j]) * yScale

		xScale = float(self.fourierScaleXEntry.get_text())
		xdata = zeros(len(xData))
		for j in range(len(y)):
			xdata[j] = float(xData[j]) * xScale

		# Decide whether to perform FFT or inverse FFT
		if self.fourierCB.get_active() == 0:
			fftdata = ifft(ydata)
			fftlen = len(fftdata)

			fftData = fftdata[0:(fftlen/2+1)]

			timestep = abs(xdata[fftlen-1]-xdata[0])/(fftlen-1)
			frequency = array(range(fftlen/2+1))/timestep/fftlen

			description = 'Fourier Transformation: f'+str(fileNum)+'c'+str(colNum)+', f'+str(fileNum2)+'c'+str(colNum2)
			self.results.append((description, 0, frequency, abs(fftData), 'Frequency', 'Fourier Transform'))

			# Update Event Log
			self.log.set_text(self.log.get_text(self.log.get_start_iter(), self.log.get_end_iter()) +
			                  '\n' + description + ' added to results table.')
		
		else:
			ifftdata = fft.fft(ydata)
			ifftlen = len(ifftdata)

			ifftData = ifftdata[0:(ifftlen/2+1)]

			timestep = abs(xdata[ifftlen-1]-xdata[0])/(ifftlen-1)
			frequency = array(range(ifftlen/2+1))/timestep/ifftlen

			description = 'Inv. Fourier Transformation: f'+str(fileNum)+'c'+str(colNum)+', f'+str(fileNum2)+'c'+str(colNum2)
			self.results.append((description, 0, frequency, abs(ifftData), 'Frequency', 'Inv. Fourier transform'))

			# Update Event Log
			self.log.set_text(self.log.get_text(self.log.get_start_iter(), self.log.get_end_iter()) +
			                  '\n' + description + ' added to results table.')		

		# Add results to results table and close the fourierAdd window
		self.updateResultsTable()

		self.fourierAddWin.destroy()


	# Gabor transforms supplied data and adds it to the results dialogue
	# it then closes the data entry window
	def gaborDone(self, widget, event, data=None):

		# Get parameters for Gaussian envelope
		sigma = float(self.gaborStdDevEntry.get_text())
		t0 = float(self.gaborTimeOffsetEntry.get_text())

		# Get the time data
		timeDataStr = self.gaborTimeDataEntry.get_text()
		cLoc = timeDataStr.find('c')
		fLoc = timeDataStr.find('f')
		fileNum = int(timeDataStr[fLoc+1:cLoc])
		colNum = int(timeDataStr[cLoc+1:])

		j = 0
		while self.files[j].fileLabel != fileNum:
			j += 1

		timeData = self.files[j].data[colNum-1]

		# Flip data set if commanded
		if timeDataStr.find('FLIP') != -1:
			timeData = timeData[::-1]

		# Get the signal data
		signalDataStr = self.gaborSignalDataEntry.get_text()
		cLoc = signalDataStr.find('c')
		fLoc = signalDataStr.find('f')
		fileNum2 = int(signalDataStr[fLoc+1:cLoc])
		colNum2 = int(signalDataStr[cLoc+1:])

		j = 0
		while self.files[j].fileLabel != fileNum2:
			j += 1

		signal = self.files[j].data[colNum2-1]

		# Flip data set if commanded
		if signalDataStr.find('FLIP') != -1:
			signal = signal[::-1]

		# Scale the data sets
		yScale = float(self.gaborScaleSignalEntry.get_text())
		ydata = zeros(len(signal))
		for j in range(len(signal)):
			ydata[j] = float(signal[j]) * yScale

		xScale = float(self.gaborScaleTimeEntry.get_text())
		xdata = zeros(len(timeData))
		for j in range(len(signal)):
			xdata[j] = float(timeData[j]) * xScale

		# Gabor transform the data
		gaborTransData = ydata/(sigma**(1/2)*pi**(1/4))*exp(-0.5*((xdata-t0)/sigma)**2)

		fftdata = ifft(gaborTransData)
		fftlen = len(fftdata)

		timeFreqDecomp = fftdata[0:(fftlen/2+1)]

		timestep = abs(xdata[fftlen-1]-xdata[0])/(fftlen-1)
		frequency = array(range(fftlen/2+1))/timestep/fftlen

		description = 'Gabor Transformation: f'+str(fileNum)+'c'+str(colNum)+', f'+str(fileNum2)+'c'+str(colNum2)
		self.results.append((description, 0, frequency, abs(timeFreqDecomp), 'Frequency', 'Gabor Transform'))

		# Update Event Log
		self.log.set_text(self.log.get_text(self.log.get_start_iter(), self.log.get_end_iter()) +
		                  '\n' + description + ' added to results table.')
		
		# Add results to results table and close the gaborAdd window
		self.updateResultsTable()

		self.gaborAddWin.destroy()

	
	# Simulates the transmission of light through heterostructures
	# Also outputs freq. dep. of refractive index if it had to be modelled
	def simTransDone(self, widget, event, data=None):
		print 'dasd'

	# Calculates transmission spectrum as well as - optionally - material thickness
	def transDone(self, widget, event, data=None):
		
		# Get the time data
		xDataStr = self.transXDataEntry.get_text()
		cLoc = xDataStr.find('c')
		fLoc = xDataStr.find('f')
		fileNum1 = int(xDataStr[fLoc+1:cLoc])
		colNum1 = int(xDataStr[cLoc+1:])

		j = 0
		while self.files[j].fileLabel != fileNum1:
			j += 1

		xData = self.files[j].data[colNum1-1]

		# Flip data set if commanded
		if xDataStr.find('FLIP') != -1:
			xData = xData[::-1]

		# Get the signal data
		yDataStr = self.transYDataEntry.get_text()
		cLoc = yDataStr.find('c')
		fLoc = yDataStr.find('f')
		fileNum2 = int(yDataStr[fLoc+1:cLoc])
		colNum2 = int(yDataStr[cLoc+1:])

		j = 0
		while self.files[j].fileLabel != fileNum2:
			j += 1

		yData = self.files[j].data[colNum2-1]

		# Flip data set if commanded
		if yDataStr.find('FLIP') != -1:
			yData = yData[::-1]

		# Get the ref time data
		refXDataStr = self.refTransXDataEntry.get_text()
		cLoc = refXDataStr.find('c')
		floc = refXDataStr.find('f')
		fileNum3 = int(refXDataStr[fLoc+1:cLoc])
		colNum3 = int(refXDataStr[cLoc+1:])

		j = 0
		while self.files[j].fileLabel != fileNum3:
			j += 1

		refXData = self.files[j].data[colNum3-1]

		# Flip data set if commanded
		if refXDataStr.find('FLIP') != -1:
			refXData = refXData[::-1]

		# Get the ref signal data
		refYDataStr = self.refTransYDataEntry.get_text()
		cLoc = refYDataStr.find('c')
		fLoc = refYDataStr.find('f')
		fileNum4 = int(refYDataStr[fLoc+1:cLoc])
		colNum4 = int(refYDataStr[cLoc+1:])

		j = 0
		while self.files[j].fileLabel != fileNum4:
			j += 1

		refYData = self.files[j].data[colNum4-1]

		# Flip data set if commanded
		if refYDataStr.find('FLIP') != -1:
			refYData = refYData[::-1]

		# Scale the data sets
		yScale = float(self.transScaleYEntry.get_text())
		ydata = zeros(len(yData))
		for j in range(len(yData)):
			ydata[j] = float(yData[j]) * yScale

		xScale = float(self.transScaleXEntry.get_text())
		xdata = zeros(len(xData))
		for j in range(len(yData)):
			xdata[j] = float(xData[j]) * xScale

		refYScale = float(self.refTransScaleYEntry.get_text())
		refYdata = zeros(len(refYData))
		for j in range(len(refYData)):
			refYdata[j] = float(refYData[j]) * refYScale

		refXScale = float(self.refTransScaleXEntry.get_text())
		refXdata = zeros(len(refXData))
		for j in range(len(refYData)):
			refXdata[j] = float(refXData[j]) * refXScale

		# Get user's modelling choice
		doRefracIndexThin = False
		doRefracIndexThick = False
		if self.transCB.get_active() in [0, 2]:
			doRefracIndexThin = True
		if self.transCB.get_active() in [1, 2]:
			doRefracIndexThick = True
	
		transAnalysis = TransSpectraAnalysis(xdata, ydata, refXdata, refYdata,
		                                     doRefracIndexThin, doRefracIndexThick)

		# Find out if user wants an estimate of the material thickness
		doThickness = self.transTickButton.get_active()

		# Output transmission spectrum, appending thickness estimate if it was requested	
		description = 'Transmission spectrum: f' +str(fileNum1)+'c'+str(colNum1)+', f'+str(fileNum2)+'c' + \
		               str(colNum2) +', f' + str(fileNum3)+'c'+str(colNum3)+', f'+str(fileNum4)+'c'+str(colNum4)
		if doThickness:
			self.results.append((description, 0, transAnalysis.freq, transAnalysis.absTransSpectrum, 
			           (transAnalysis.thickness, 'Thickness'), 'Frequency', 'Transmission Spectrum'))

			if doRefracIndexThin:
				description = 'Refractive Index Thin: f' +str(fileNum1)+'c'+str(colNum1)+', f'+str(fileNum2)+'c' + \
				               str(colNum2) +', f' + str(fileNum3)+'c'+str(colNum3)+', f'+str(fileNum4)+'c'+str(colNum4)
				self.results.append((description, 0, transAnalysis.freq, transAnalysis.refIndexThin, 'Frequency', 'Refractive Index'))

			if doRefracIndexThin:
				description = 'Refractive Index Thick: f' +str(fileNum1)+'c'+str(colNum1)+', f'+str(fileNum2)+'c' + \
				               str(colNum2) +', f' + str(fileNum3)+'c'+str(colNum3)+', f'+str(fileNum4)+'c'+str(colNum4)
				self.results.append((description, 0, transAnalysis.freq, transAnalysis.refIndexThick, 'Frequency', 'Refractive Index'))

		# Add results to results table and close the fourierAdd window
		self.updateResultsTable()

		self.transAddWin.destroy()


	def updateResultsTable(self):
		
		self.analysisSW.remove(self.analysisSW.get_child())

		numResults = len(self.results)

		# Try to keep button sizes consistent with rest of interface
		if numResults < 12:
			numRows = 13
		else:
			numRows = numResults + 1

		resultTable = gtk.Table(rows=numRows, columns=5, homogeneous=True)
		resultTable.set_row_spacings(2)

		Shade = 50000    # Shade of grey for title boxes
		# Title box for 'File' column
		title1 = gtk.Label(str='Description')
		hbox = gtk.HBox()
		hbox.add(title1)
		eb1 = gtk.EventBox()     
		eb1.add(hbox)
		eb1.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(Shade, Shade, Shade))

		# Title box for 'File Label' column
		title2 = gtk.Label(str='Plot')
		hbox = gtk.HBox()
		hbox.add(title2)
		eb2 = gtk.EventBox()     
		eb2.add(hbox)
		eb2.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(Shade, Shade, Shade))

		# Title box for 'Num Columns' column
		title3 = gtk.Label(str='Output')
		hbox = gtk.HBox()
		hbox.add(title3)
		eb3 = gtk.EventBox()     
		eb3.add(hbox)
		eb3.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(Shade, Shade, Shade))

		# Title box for 'Remove' column
		title4 = gtk.Label(str='Remove')
		hbox = gtk.HBox()
		hbox.add(title4)
		eb4 = gtk.EventBox()     
		eb4.add(hbox)
		eb4.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(Shade, Shade, Shade))
	
		resultTable.attach(eb1, 0, 2, 0, 1)
		resultTable.attach(eb2, 2, 3, 0, 1)
		resultTable.attach(eb3, 3, 4, 0, 1)
		resultTable.attach(eb4, 4, 5, 0, 1)

		# Add each set of results to the table
		counter = 1
		for result in self.results:
			# Description column
			description = gtk.Label(str=result[0])
			resultTable.attach(description, 0, 2, counter, counter+1)

			# Plot buttons column
			plotButton = gtk.Button('Plot', stock=None)
			plotButton.connect('clicked', self.plotResult, 'Plot', counter-1)
			resultTable.attach(plotButton, 2, 3, counter, counter+1)

			# Output buttons column
			outputButton = gtk.Button('Output', stock=None)
			outputButton.connect('clicked', self.outputResult, 'Output', counter-1)
			resultTable.attach(outputButton, 3, 4, counter, counter+1)

			# Remove buttons column
			removeButton = gtk.Button('Remove', stock=None)
			removeButton.connect('clicked', self.removeResult, 'Remove', counter-1)
			resultTable.attach(removeButton, 4, 5, counter, counter+1)

			counter += 1

		self.analysisSW.add_with_viewport(resultTable)
		self.window.show_all()


	# Plot a set of results from the results table
	def plotResult(self, widget, event, resultPos):
		
		result = self.results[resultPos]

		# Have multiple possible plot types indicated by integer at second position in results aray
		# only one type added so far...
		# 0 - standard 2D plot
		if result[1] == 0:

			# Create plot
			p=PlotWidget2(title=result[0], mainProg=False, showRect=True, figHeight=300)	# Create the plot window + widget

			k = 0
			if len(result)%2 != 0:
				k = 1

			# Hand over data sets to plotWidget2 class
			p.xDataStore.append(result[2])
			p.yDataStore.append(result[3])
			p.axLabels.append([result[4+k], result[5+k]])

			p.plotData(p.axis,p.xDataStore[-1],p.yDataStore[-1],xlabel=p.axLabels[0][0],ylabel=p.axLabels[0][1])
			p.axLabel(p.axis,p.axLabels[-1][0],p.axLabels[-1][1])

			# This part is needed to resize the green bounding box (for the windowed FFT) after the data has been plotted
			currLim = getAxisLimits(p.axis)		
			resizeRect(p.axis.r1,currLim,p.canvas)

			self.log.set_text(self.log.get_text(self.log.get_start_iter(), self.log.get_end_iter()) + 
				          '\n' + 'Plotted ' + result[0] + ' data as a 2D plot.')


	# Allows user to save data sets to a specified location
	def outputResult(self, widget, event, resultPos):

		# Aquire result
		result = self.results[resultPos]

		# Calculate number of columns in output file from length of results tuple
		numCols = len(result)/2 - 1			 

		# Allow user to choose file save location
		chooser = gtk.FileChooserDialog("Save data",
                                None,
                                  gtk.FILE_CHOOSER_ACTION_SAVE,
                                 (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                  gtk.STOCK_SAVE, gtk.RESPONSE_OK))
		chooser.set_default_response(gtk.RESPONSE_OK)
		chooser.set_select_multiple(False)

		# Suggest a file name to save as to the user
		chooser.set_current_name(result[0].replace(' ', '_') + '.txt')

		response = chooser.run()

		# Save current working directory to revert back to it afterwards
		cwd = os.getcwd()

		# Get the location and name of the data file
		fileName = ''
		location = ''
		if response == gtk.RESPONSE_OK:
			fileName = chooser.get_filename()
			location = chooser.get_current_folder()
			chooser.destroy()

			# Write data to the file at the specified location
			os.chdir(location)
			f = open(fileName, 'w')

			# Use first line of file for column labels
			labels = result[-1]
			j = 1
			while j < numCols:
				j += 1
				labels = result[-j] + ', ' + labels

			# Stick with convention of expecting a % at the start of comment lines
			labels = '% ' + labels
		
			f.write(labels)

			# Check for tuple containing non-array type results in center of results list
			if len(result)%2 != 0:
				singleResults = result[2+numCols]

				# Write single results on second comment line
				numSingle = len(singleResults)/2
				single = '\n% ' + singleResults[numSingle] + ': ' + str(singleResults[0])
				k = 1
				while k < numSingle:
					single += ', ' + singleResults[k+numSingle] + ': ' + str(singleResults[k])
					k += 1

				f.write(single)

			# Write data to the file
			j = 0
			rows = len(result[2])   # Use length of first data set to deduce number of rows
			while j < rows:
				row = '\n'
				for data in result[2:numCols+2]:
					if row == '\n':
						row += str(data[j])
					else:
						row += '\t' + str(data[j])

				j += 1
				f.write(row)

			f.close()

			# Go back to the previous working directory
			os.chdir(cwd)
		
			self.log.set_text(self.log.get_text(self.log.get_start_iter(), self.log.get_end_iter()) + 
				          '\n' + 'Result' + result[0] + ' saved to ' + location + ' as ' + 
			                  fileName.replace(location + '/', '') +  '.')

			# Add the file to the data files table
			self.numFiles += 1
			label = self.numFiles
			data = Data(fileName, location, label)   # Implement the "Data" class to load and store the data in the file

			self.files.append(data)
			self.updateFilesTable()

			self.log.set_text(self.log.get_text(self.log.get_start_iter(), self.log.get_end_iter()) + 
				          '\n' + 'File ' + data.fileName + ' automatically loaded from ' + data.location +
				          '. Label: f' + str(data.fileLabel) + ', Columns: ' + str(data.numCols) + '.')
			
		elif response == gtk.RESPONSE_CANCEL:
			chooser.destroy()


	def removeResult(self, widget, event, resultPos):
		
		description = self.results[resultPos][0]

		self.results.pop(resultPos)

		if len(self.results) == 0:
			# Default files window to displaying the message "No Files Added" in a white window
			noResultsLabel = gtk.Label(str='No Results Yet')
			hbox = gtk.HBox()
			hbox.add(noResultsLabel)
			eb = gtk.EventBox()     
			eb.add(hbox)
			eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(65535, 65535, 65535))

			self.analysisSW.remove(self.analysisSW.get_child())
			self.analysisSW.add_with_viewport(eb)

			self.window.show_all()

		else:
			self.updateResultsTable()

		# Update the Event Log
		self.log.set_text(self.log.get_text(self.log.get_start_iter(), self.log.get_end_iter()) + 
		                  '\n' + 'Result ' + description + ' removed from the Results list.')


# Class designed to retrieve and store data from files for the SpectAnalysisGUI class
class Data():

	def __init__(self, filePos, location, label):
		
		self.filePos = filePos
		self.location = location
		
		self.fileName = self.filePos.replace(self.location+'/', '')

		self.fileLabel = label

		# Read data and format it into columns
		data = self.readBadData(fileName=self.fileName, location=self.location)

		self.data = []
		for j in range(len(data[0])):
			temp = []
			for row in data:
				temp.append(row[j])
			self.data.append(temp)

		self.numCols = len(data[0])


	# Read data from "badly-formatted" data file i.e. one containing multiple different delimiters
	def readBadData(self, fileName='', location='', delimiters=['\t', ' '], comment='% '):

		# Save current working directory to revert back to it afterwards
		cwd = os.getcwd()

		os.chdir(location)
		f = open(fileName, 'r')

		i = 0    # Row
		datum = ''   # Necessary to rcord last datum in file
		data = []

		for line in f:
			if not comment in line:    # Skips lines with comments in them

				data.append([])
				datum = ''
				for char in line:
					if char in delimiters:
						if len(datum) > 0:   # Deals with multiple successive delimiters case
							data[i].append(datum)
							datum = ''
					elif char == '\n':
						data[i].append(datum)
					else:
						datum += char
				i += 1

		data[i-1].append(datum)   # Last datum in file

		f.close()

		# Go back to the previous working directory
		os.chdir(cwd)

		return data
		

def main():
	gtk.main()

if __name__ == "__main__":
	SpectAnalysisGUI()
	main()
