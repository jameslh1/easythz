import string
import gtk
import gtk.glade
##### Use Matplotlib for the plotting routines.
import matplotlib
#### choose matplotlib backend: 'GTK' has ylabel bug, 'GTKAgg' is slower and gives Xlib async errors
#from matplotlib.backends.backend_gtk import FigureCanvasGTK as FigureCanvas
#from matplotlib.backends.backend_gtk import NavigationToolbar2GTK as NavigationToolbar2
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar2

from matplotlib.figure import *
from matplotlib.axes import *
from matplotlib.artist import getp, setp
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, MaxNLocator, AutoMinorLocator, LogLocator
from matplotlib.ticker import LogFormatterMathtext as LogFormat
from matplotlib.widgets import Cursor
from matplotlib.colors import colorConverter

from numpy import array, log, log10, angle, unwrap, real, imag, max, pi, loadtxt, polyfit, poly1d, linspace, logspace, savetxt

from os import getcwd

import pickle

############### IMPORT MY CODE LIBRARIES:     
from generic_gtk import *
from fileIO import *
from mathsRoutines import *
from newWindow import NewWindow
from paramWidget import *

from toolbars import *
from tabbed import TabbedContainer

#from simLattice import SimLattice



######## main application window #######################################
class PlotWidget2(NewWindow):
	"""PlotWidget2(NewWindow)
	     numSubplots=[2,3]      makes a 2x3 array of plots (default: [1,1])
	     figWidth, figHeight    figure size (pixels)
	     makeTB=True	    make the toolbar
             showRect=False         choose whether to show green boxing window
             plotPolar=False        polar plots (r,theta) need a different axis
             **kwargs               all other arguments passed to NewWindow.__init__
"""

	ALLOWED_LINESTYLES=['-','--','-.',':','None']
	STYLES=['Solid, -','Dashed, --','Dotted, :','Dash-dotted, -.']

	FIGBGCOLOUR=(0.937,0.922,0.906)
	AXISCOLOUR='w'

	AXIS_TEXT_SIZE=24
	AXIS_LABEL_DICT={'fontweight':'bold','fontsize':20}   # x and y axis font dictionary

	titleLabelDict={'fontweight':'bold','fontsize':24}   # x and y axis font dictionary

	PLOT_POSITION = [0.15,0.15,0.8,0.8]


	def __init__(self,numSubplots=[1,1],figWidth=700,figHeight=500,makeTB=True,showRect=False,plotPolar=False,**kwargs):
		NewWindow.__init__(self, makeHbox=False,**kwargs)
		self.lineColour=['b','r','g','y','m','b','r','g','y','m']

		self.makeTB = makeTB
		self.showRect = showRect
		self.plotPolar = plotPolar

		self.numFFTsubplots=[1,1]
		self.createFigure(numSubplots,figWidth,figHeight)

		self.currentLegPos=1
		self.currentLegTrans=0.4

		self.fftWinList=[]
		self.xDataStore=[]
		self.yDataStore=[]
		self.axLabels=[]
		self.lineStore=[]

		self.vbox.show_all()
		self.clickMode = 0     # defaults to left click doing nothing. See "button_callback"
		self.win.show_all()

	def createFigure(self,numSubplots,figWidth,figHeight):
		"""Called to initialise each page (and data array for each page)"""

		self.axisList=[]
		self.axis=None
		# define handles to widgets

		############## FIGURE
		self.figure = Figure(dpi=60)		
		self.figure.set_facecolor(self.FIGBGCOLOUR)
		self.figure.set_edgecolor(self.FIGBGCOLOUR)


		self.canvas = FigureCanvas(self.figure)
		self.canvas.set_size_request(figWidth,figHeight)
		self.canvas.show()
		self.buttonCallback=self.canvas.mpl_connect('button_press_event', self.OnPress)
#		self.canvas.mpl_connect('resize_event', onAutoScale, None, self.axis, self.canvas)

 
		############## AXIS
		#self.axis=self.figure.add_axes(plotPosition,axisbg=axisColour)
		subplotList=[]
		for m in range(numSubplots[0]*numSubplots[1]):
			subplotList.append(numSubplots[0]*100 + numSubplots[1] * 10 + m+1)

		if len(subplotList)==1:
			self.axisList.append(self.figure.add_subplot(111,axisbg=self.AXISCOLOUR,polar=self.plotPolar))
			self.axisList[0].set_position(self.PLOT_POSITION)
		else:
			for x in subplotList:
				self.axisList.append(self.figure.add_subplot(x,axisbg=self.AXISCOLOUR))

		self.axis=self.axisList[0]

		# format each axis correctly
		for axis in self.axisList:
	#		self.axis.grid(True,which='major')
			axis.grid(True)
	#		self.axis.grid(True,which='minor',color='r', linestyle='-', linewidth=2)
	#		self.axis.set_position(plotPosition)

			xax=axis.get_xticklabels()
			yax=axis.get_yticklabels()

			for tick in xax:
				tick.set_fontsize(self.AXIS_TEXT_SIZE)

			for tick in yax:
				tick.set_fontsize(self.AXIS_TEXT_SIZE)		

		
		self.legendStr=[]
		self.gaList=[]

		## add cursor function to axis when mouse is over it
#		self.cursor = Cursor(self.axis, useblit=True, color='red', linewidth=1)

		self.canvas.draw()

		# plot a transparent rectangle just on axis 1
		currXlim=self.axis.get_xlim()
		dx=abs(currXlim[1]-currXlim[0])
		x0=currXlim[0]
		currYlim=self.axis.get_ylim()
		dy=abs(currYlim[1]-currYlim[0])
		y0=currYlim[0]

		self.axis.r1=plotRect(self.axis,self.canvas,(x0,y0),dx,dy,showRect=self.showRect)

		#self.axis.cla()

		
		############## TOOLBAR
		# use a custom version of the matplotlib toolbar
#		toolbar = NavigationToolbar2(self.canvas, self.win)
		self.toolbar = PlotToolbar(self.canvas,self.win,self.axis)
		zoomtoolbar = PlotZoomToolbar(self.canvas,self.win,self.axis,)

		# make a TB menu
		menuList=['|FFT|','Normalised |FFT|','|FFT| & arg(FFT)','|T| & <T','Re & Im (T)','Re & Im (1/T - 1)','n & alpha']
		mnuBtn = MenuToolButtonWidget(menuList, icon=gtk.STOCK_SELECT_COLOR, label='FFT')
		mnuBtn.btn.connect("clicked",self.newFFTwin2,0)
		for m in range(len(menuList)):
			mnuBtn.menuItems[m].connect("activate",self.newFFTwin,m)

		mnuBtn.btn.set_tooltip_text('Take windowed FFT of ALL lines.')
		self.toolbar.add(mnuBtn.btn)



		sep=gtk.SeparatorToolItem()
		self.toolbar.insert(sep,1)


		btn6=gtk.ToolButton(gtk.STOCK_CLEAR)
		btn6.connect("clicked",self.OnClear)
		btn6.set_label('Clear')
		btn6.set_tooltip_text('Clear the axis.')
		self.toolbar.insert(btn6,1)

		btn0=gtk.ToolButton(gtk.STOCK_SAVE_AS)
		btn0.connect("clicked",self.OnExport)
		btn0.set_label('Export')
		btn0.set_tooltip_text('Export data from a curve.')
		self.toolbar.insert(btn0,1)


		# make a TB menu
		fitMenuList=['Linear','Polynomial','Exp decay','Subtract exp']
		fitmnuBtn = MenuToolButtonWidget(fitMenuList, icon=gtk.STOCK_ABOUT, label='Fit')
		fitmnuBtn.btn.connect("clicked",self.fitPolynomial,0)
		for m in range(len(fitMenuList)):
			fitmnuBtn.menuItems[m].connect("activate",self.fitPolynomial,m)

		fitmnuBtn.btn.set_tooltip_text('Fits a polynomial to data (default is a linear fit).')
		self.toolbar.add(fitmnuBtn.btn)


		btn7=gtk.ToolButton(gtk.STOCK_CONVERT)
		btn7.connect("clicked",self.getBeamWidth)
		btn7.set_label('Beamwidth')
		btn7.set_tooltip_text('Get the beamwidth (fits Gaussian to dy/dx).')
		self.toolbar.add(btn7)

		btn8=gtk.ToolButton(gtk.STOCK_EDIT)
		btn8.connect("clicked",self.editPlotParams)
		btn8.set_label('Axes')
		btn8.set_tooltip_text('Edit plot parameters.')
		self.toolbar.add(btn8)

		btn9=gtk.ToolButton(gtk.STOCK_PROPERTIES)
		btn9.connect("clicked", self.editLegend)
		btn9.set_label('Legend')
		btn9.set_tooltip_text('Edit legend.')
		self.toolbar.add(btn9)

		btn10=gtk.ToolButton(gtk.STOCK_ADD)
		btn10.connect("clicked", self.addData)
		btn10.set_label('Add')
		btn10.set_tooltip_text('Add data set.')
		self.toolbar.add(btn10)

#		self.toolbar.set_style(gtk.TOOLBAR_BOTH)   # make toolbar icons and labels visible

		if self.makeTB:
			self.vbox.pack_start(self.toolbar,False,False)

		self.vbox.pack_start(self.canvas,True,True)
		self.vbox.pack_start(zoomtoolbar,False,False)

		####### Line selector/axis alteration toolbar
		hbox=gtk.HBox(homogeneous=False, spacing=0)

		paramNames         = ['Line:']
		paramTypes         = ['cmb']
		paramDefaultValues = [[]]

		paramBox = ParamWidget(paramNames,paramTypes,paramDefaultValues)
		self.cmbBox = paramBox.objectList[0]
#		self.cmbBox.connect('changed',self.line_changed)

		self.hideBtn = gtk.ToggleToolButton(gtk.STOCK_NO)
		self.hideBtn.set_tooltip_text('Hide')
		self.hideBtn.connect('clicked',self.toggle_line)
		paramBox.table.attach(self.hideBtn,0,1,0,1,xoptions=gtk.EXPAND,yoptions=gtk.EXPAND)
		
		self.colourBtn = gtk.ToolButton(gtk.STOCK_COLOR_PICKER)
		self.colourBtn.set_tooltip_text('Colour')
		self.colourBtn.connect('clicked',self.change_colour)
		self.color=gtk.gdk.Color(red=0,green=0,blue=1)

		paramBox.table.attach(self.colourBtn,1,2,0,1,xoptions=gtk.EXPAND,yoptions=gtk.EXPAND)
		
		self.cmbStyle = gtk.combo_box_new_text()

		for style in self.STYLES:
			self.cmbStyle.append_text(style)
		self.cmbStyle.set_active(0)
#		self.style.set_tooltip_text('Line style')
		self.cmbStyle.connect('changed',self.change_style)

		paramBox.table.attach(self.cmbStyle,2,3,0,1,xoptions=gtk.EXPAND,yoptions=gtk.EXPAND)

		self.removeBtn = gtk.ToolButton(gtk.STOCK_DELETE)
		self.removeBtn.set_tooltip_text('Remove')
		self.removeBtn.connect('clicked',self.remove_line)

		paramBox.table.attach(self.removeBtn,3,4,0,1,xoptions=gtk.EXPAND,yoptions=gtk.EXPAND)


		hbox.pack_start(paramBox.frame,False,False)

		paramNames         = ['Axis:','Left-click sets:']
		paramTypes         = ['lbl','cmb']
		paramDefaultValues = ['',['Nothing','Window left','Window right','Axis left','Axis right','Plots point']]

		paramBox = ParamWidget(paramNames,paramTypes,paramDefaultValues)
		hbox.pack_start(paramBox.frame,False,False)
		
		self.cmbBtn = paramBox.objectList[1]
		self.cmbBtn.set_active(0)
		self.cmbBtn.connect("changed", self.onModeChanged)

		hbox.show_all()

#		self.canvas.mpl_connect('axes_enter_event', self.enter_axes)
#		self.canvas.mpl_connect('axes_leave_event', self.leave_axes)

		if self.makeTB:
#			self.connectToolbar()
			self.vbox.pack_start(hbox,False,False)


	def onModeChanged(self,widget=None):
		self.clickMode = self.cmbBtn.get_active()


	def numDataSets(self):
#		nx=len(self.xDataStore)
		ny=len(self.yDataStore)
		print 'Number of data sets = ',ny
		return ny


	def getData(self, filename='',xIndex=0,yIndex=1):
		numPlots = 0

		if not filename=='':
			tokens = string.split(filename,'/')
			shortfilename=tokens[len(tokens)-1]

			fileLocation=''
			for m in range(len(tokens)-1):
				fileLocation=fileLocation+tokens[m]+'/'
							
			delim, numCols, axLabels = getColumnDelim(filename)   # get the column delimiter and info


			# choose which axes to plot
			self.axLabelStore = gtk.ListStore(str)

			for x in range(len(axLabels)):
				if string.find(axLabels[x],'Nothing')==-1:
					self.axLabelStore.append([axLabels[x]])


			if not xIndex==-1:
				if delim=='xml':
					xdata, ydata = getXMLdata(filename)
				else:
					xdata, ydata = loadData(filename, delim, xIndex, yIndex)

				if len(xdata)==0:
					return 0

				self.xDataStore.append(xdata)
				self.yDataStore.append(ydata)

				self.axLabels.append([axLabels[xIndex],axLabels[yIndex]])

		return 1



	def axLabel(self, axis=None, xlabel='', ylabel=''):
		if axis==None:
			axis=self.axis
		xlbl=axis.set_xlabel(xlabel,fontdict=self.AXIS_LABEL_DICT)
		ylbl=axis.set_ylabel(ylabel,fontdict=self.AXIS_LABEL_DICT)
		self.canvas.draw()


	def plotData(self, axis, xdata, ydata, xlabel='', ylabel='', lineprops=dict(color='b', linewidth=2,linestyle='-'),addToList=True,labelStr='',reDraw=True):

		p1, = axis.plot(xdata,ydata,label=labelStr,**lineprops)

		if reDraw:
			self.canvas.draw()

		if addToList:
			self.appendToList(p1,xlabel,ylabel)

		return p1


	def plotAll(self,**kwargs):
		for m in range(len(self.yDataStore)):
			self.plotData(self.axis,self.xDataStore[m],self.yDataStore[m],xlabel=self.axLabels[0][0],ylabel=self.axLabels[0][1],lineprops=dict(color=self.lineColour[0], linewidth=2,linestyle='-'),**kwargs)
			iter_list_items(self.lineColour)

		self.axLabel(self.axis,self.axLabels[-1][0],self.axLabels[-1][1])

		# this part is needed to resize the green bounding box (for the windowed FFT) after the data has been plotted
		currLim=getAxisLimits(self.axis)		
		resizeRect(self.axis.r1,currLim,self.canvas)


	def plotBar(self, axis, xdata, ydata, xlabel='', ylabel='', xmin=0, xmax=10, width=0.8,addToList=True, lineprops=dict(color='r', linewidth=2,linestyle='-')):
		if ydata==0.0:
			ydata=1

		p1, = axis.bar(xdata,ydata,**lineprops)
		#self.axLabel(axis,xlabel,ylabel)
		axis.set_xlim(xmin,xmax)
		self.canvas.draw()
		if addToList:
			self.appendToList(p1,xlabel,ylabel)


		
	def plotFFT(self, axis, xdata, ydata, xunit='s', lineprops=dict(color='b', linewidth=2,linestyle='-'), xlabel='Hz', ylabel='', mode=0):
		self.freq , self.cfield, xlabel  = takeFFT(xdata, ydata, xunit)
		self.ampField=abs(self.cfield)

		if (mode==0) or (mode==2):
			self.plotData(axis, self.freq,self.ampField, xlabel, ylabel, lineprops, labelStr='FFT')
		elif mode == 1:
			self.plotData(axis, self.freq,self.ampField/max(self.ampField), xlabel, ylabel, lineprops, labelStr='FFT')

		self.axLabel(axis,xlabel,ylabel)

		if mode==2:
			self.plotData(self.axisList[1], self.freq,unwrap(angle(self.cfield)), xlabel, ylabel, lineprops, labelStr='FFT')
			self.axLabel(self.axisList[1],xlabel,ylabel)
		
		self.canvas.draw()


	def plotContour(self, axis, dataArray, numContours=50, xax=None, yax=None):
		if (xax==None) and (yax==None):
			axis.contourf(dataArray,numContours)
		elif (xax==None) or (yax==None):
			print 'PlotWidget2.plotContour():: warning:: specified either x or y but not both'
			return
		else:
			axis.contourf(xax,yax,dataArray,numContours)
			axis.contour(xax,yax,dataArray,numContours)

		self.canvas.draw()
		return
	

	def getParamValue(self, widget, name, resultDict):
		result = getWidgetValue(widget)
		resultDict[name]=result
#		print self.resultDict
		return 


	def getColour(self, widget, name, resultDict, currentColour):
		colorseldlg = gtk.ColorSelectionDialog("Select new colour")

		# Get the ColorSelection widget
		colorsel = colorseldlg.colorsel

#		currentColour='k'
		col=colorConverter.to_rgb(currentColour)

		colorsel.set_previous_color(gtk.gdk.Color(red=col[0],green=col[1],blue=col[2]))
		colorsel.set_current_color(gtk.gdk.Color(red=col[0],green=col[1],blue=col[2]))
		colorsel.set_has_palette(True)

		# Connect to the "color_changed" signal
#		colorsel.connect("color_changed", self.color_changed_cb)
		# Show the dialog
		response = colorseldlg.run()
		colorseldlg.hide()

		if response == gtk.RESPONSE_OK:
			color = colorsel.get_current_color()
		else:
			return 0
#			self.drawingarea.modify_bg(gtk.STATE_NORMAL, self.color)
		
		colorstr=color.to_string()
		
		red=int(colorstr[1:5],16)/65535.0
		green=int(colorstr[5:9],16)/65535.0
		blue=int(colorstr[9:13],16)/65535.0

#		col=colorConverter.to_rgb(tuple([red,green,blue]))
		newColour=gtk.gdk.Color(red=int(round(65535*red)),green=int(round(65535*green)),blue=int(round(65535*blue)))

		widget.modify_bg(gtk.STATE_NORMAL, newColour)

#		print colorstr
		resultDict[name]=[red,green,blue]
#		print resultDict[name]

		return


	def OnExport(self, widget):

		lines=self.axisList[0].get_lines()
		lineLabels=[]		
		for l in range(len(lines)):
			lineLabels.append(lines[l].get_label()+' (Line '+str(l)+')')


		paramNames = ['Line']
		paramTypes = ['cmb']
		paramDefaultValues = [lineLabels]

		paramBoxes = ParamWidget(paramNames,paramTypes,paramDefaultValues)
		paramBoxes.vbox.show_all()

		optionsWidget=paramBoxes.frame


		newfile = fileDialog('save', file_name="new.txt", file_filter_name="Data files", file_filter=[], currentDir=getcwd(), title_string="Choose file",extraWidget=optionsWidget)

		if not newfile=="":
			l=paramBoxes.objectList[0].get_active()
			print 'Saved x & y data from Line ',str(l),' to ', newfile

			data= lines[l].get_xydata()
			savetxt(newfile,data,delimiter='\t')

		return

	# routine to make a new FFT window from the time-windowed data selected
	def newFFTwin(self, widget, mode=0):
		self.lastFFTsubplots = self.numFFTsubplots

		# mode = 0: amplitude only
		# mode = 1: normalised amplitude
		# mode = 2: amplitude and phase
		# mode = 3: abs and phase of (T)
		# mode = 4: real and imag parts of (T)
		# mode = 5: real and imag parts of (1/T - 1)
		# mode = 6: refractive index determination
		if (mode == 0) or (mode == 1):
			self.numFFTsubplots=[1,1]
		elif (mode > 1):
			self.numFFTsubplots = [2,1]

		if mode==5:   # only run fftoptions dialog if doing refractive index calc
			fftOptions,fftOptResult=self.getFFToptions(mode)
			print fftOptions, fftOptResult
		else:
			fftOptions={}
			fftOptResult=1


		if not fftOptResult:
			print 'PlotWidget2.newFFTwin()::getFFToptions dialog was cancelled'
			return

		if not self.lastFFTsubplots == self.numFFTsubplots:
			newWin = 1
		else:
			newWin = 0
#		print newWin

		lineNum=self.cmbBox.get_active()
#		print lineNum

		xmin=self.axis.r1._x
		xmax=xmin + self.axis.r1._width

		l=self.axis.get_lines()
#		if len(l)>=3:
#			lines=l[2:]
#		else:
		lines=l
		xdata=getp(lines[lineNum],'xdata')
		ydata=getp(lines[lineNum],'ydata')
		col=getp(lines[lineNum],'color')
		lwidth=getp(lines[lineNum],'linewidth')
		lstyle=getp(lines[lineNum],'linestyle')

		lineProps=dict(color=col,linewidth=lwidth,linestyle=lstyle)

		firstPoint=0
		lastPoint=len(xdata)-1

		for m in range(len(xdata)):
			if xdata[m]>xmin:
				firstPoint=m
				break

		for m in range(len(xdata)):
			if xdata[m]>xmax:
				lastPoint=m
				break

		xlabel = self.axis.get_xlabel()
		if '(mm)' in xlabel:
			xunit = 'mm'
		elif '(ps)' in xlabel:
			xunit = 'ps'
		else:
			xunit = 's'

		if (len(self.fftWinList)==0) or (newWin==1):
			titstr = 'FFT window ' + str(len(self.fftWinList)+1)
#			win = NewWindow(title=titstr)
			newplot=PlotWidget2(numSubplots=self.numFFTsubplots,makeTB=True)
#			win.addWidget(newplot.vbox)
#			win.win.connect('destroy',self.fftWinList.remove,len(self.fftWinList)+1)


			if not xdata == None:
				if mode < 3:
					newplot.plotFFT(newplot.axis, xdata[firstPoint:lastPoint],ydata[firstPoint:lastPoint], xunit=xunit, lineprops=lineProps, mode=mode)

				elif mode == 3:   # plot |T|, arg T
					ydata2=getp(lines[0],'ydata') # reference is Line 0
					Eon =ydata[firstPoint:lastPoint]
					Eoff=ydata2[firstPoint:lastPoint]

					freq, cfieldOn, xlabel  = takeFFT(xdata[firstPoint:lastPoint], Eon, xunit)
					freq2, cfieldOff, xlabel  = takeFFT(xdata[firstPoint:lastPoint], Eoff, xunit)

					exprn = cfieldOn/cfieldOff

					newplot.plotData(newplot.axisList[0], freq,abs(exprn), xlabel=xlabel, ylabel='|T|', lineprops=lineProps)
					newplot.plotData(newplot.axisList[1], freq,unwrap(angle(exprn)), xlabel=xlabel, ylabel='<T', lineprops=lineProps)
#					newplot.plotFFT(newplot.axis, xdata[firstPoint:lastPoint],ydata[firstPoint:lastPoint], xunit=xunit, lineprops=lineProps, mode=mode)
					newplot.axis.set_ylim(0,1.0)
#					newplot.axis.set_xlim(0,3.0)
					newplot.canvas.draw()
#					print 'set ylim'


				elif mode == 4:   # plot Re T, Im T
					ydata2=getp(lines[0],'ydata') # reference is Line 0
					Eon =ydata[firstPoint:lastPoint]
					Eoff=ydata2[firstPoint:lastPoint]

					freq, cfieldOn, xlabel  = takeFFT(xdata[firstPoint:lastPoint], Eon, xunit)
					freq2, cfieldOff, xlabel  = takeFFT(xdata[firstPoint:lastPoint], Eoff, xunit)

					exprn = cfieldOn/cfieldOff

					newplot.plotData(newplot.axisList[0], freq,real(exprn), xlabel=xlabel, ylabel='Re[exprn]', lineprops=lineProps)
					newplot.plotData(newplot.axisList[1], freq,imag(exprn), xlabel=xlabel, ylabel='Im[exprn]', lineprops=lineProps)
#					newplot.plotFFT(newplot.axis, xdata[firstPoint:lastPoint],ydata[firstPoint:lastPoint], xunit=xunit, lineprops=lineProps, mode=mode)


				elif mode == 5:   # plot cond \propto 1/T - 1
					ydata2=getp(lines[0],'ydata')
					Eon=ydata[firstPoint:lastPoint]*(-0.01) + ydata2[firstPoint:lastPoint]
					Eoff=ydata2[firstPoint:lastPoint]

					freq, cfieldOn, xlabel  = takeFFT(xdata[firstPoint:lastPoint], Eon, xunit)
					freq2, cfieldOff, xlabel  = takeFFT(xdata[firstPoint:lastPoint], Eoff, xunit)

					exprn = cfieldOff/cfieldOn - 1

					newplot.plotData(newplot.axisList[0], freq,real(exprn), xlabel=xlabel, ylabel='Re[exprn]', lineprops=lineProps)
					newplot.plotData(newplot.axisList[1], freq,imag(exprn), xlabel=xlabel, ylabel='Im[exprn]', lineprops=lineProps)
#					newplot.plotFFT(newplot.axis, xdata[firstPoint:lastPoint],ydata[firstPoint:lastPoint], xunit=xunit, lineprops=lineProps, mode=mode)

				elif mode == 6:   # plot refractive index
					xdata=getp(lines[fftOptions['Reference:']],'xdata')
					ydata=getp(lines[fftOptions['Sample:']],'ydata')
					ydata2=getp(lines[fftOptions['Reference:']],'ydata')

					if fftOptions['Calculate d,n\n(needs 1st internal\nreflection in sample)']:
						ns, d = getSampleThickness(xdata, xunit, ydata2, ydata, peakWidth=20)
					else:
						ns = float(fftOptions['Assume n ='])
						d = float(fftOptions['Assume thickness d ='])

					print 'Calculating refractive index using ns='+str(ns)+', d='+str(d)

					xref=xdata[firstPoint:lastPoint]
					xsample=xdata[firstPoint:lastPoint]
					Esample=ydata[firstPoint:lastPoint]
					Eref   =ydata2[firstPoint:lastPoint]

					sf = int(fftOptions['Zero padding'])
					xPad, ErPadded = zeropad(xref,Eref,expansion=sf)
					xPad2, EsPadded = zeropad(xsample,Esample,expansion=sf)
#					print xPad[1]-xPad[0], xdata[1]-xdata[0]
					if fftOptions['Remove 1st\nreflection']:
						EsPadded = zeroSecondPeak(EsPadded,peakWidth=40)

					self.plotData(self.axisList[0], xPad, ErPadded, lineprops=dict(color='b', linewidth=4,linestyle='--'))
					self.plotData(self.axisList[0], xPad2, EsPadded, lineprops=dict(color='r', linewidth=4,linestyle='--'))
					onAutoScale(widget,self.axisList[0],self.canvas)

					freq, cfieldSample, xlabel  = takeFFT(xPad, EsPadded, xunit=xunit)
					freq2, cfieldRef, xlabel    = takeFFT(xPad, ErPadded, xunit=xunit)
#					freq, cfieldSample, xlabel  = takeFFT(xdata[firstPoint:lastPoint], Esample, xunit)
#					freq2, cfieldRef, xlabel    = takeFFT(xdata[firstPoint:lastPoint], Eref, xunit)

					trans=cfieldSample/cfieldRef

					tvstsv = 4 * ns /((ns+1)**2)
					absn = (-2.0 / d) * log(abs(trans)/(tvstsv))
					refrIndex = 1+ 2.998e8 * -1*unwrap(angle(trans)) / (2*pi*d*freq*1e12)

					newplot.plotData(newplot.axisList[0], freq,refrIndex, xlabel=xlabel, ylabel='n', lineprops=lineProps)
					newplot.plotData(newplot.axisList[1], freq2,absn, xlabel=xlabel, ylabel='alpha', lineprops=lineProps)

#					newplot.plotFFT(newplot.axis, xdata[firstPoint:lastPoint],ydata[firstPoint:lastPoint], xunit=xunit, lineprops=lineProps, mode=mode)

			newplot.win.show_all()

			self.fftWinList.append(newplot)
			
		else:
			self.fftWinList[0].plotFFT(self.fftWinList[0].axis, xdata[firstPoint:lastPoint],ydata[firstPoint:lastPoint], xunit=xunit, lineprops=lineProps, mode=mode)



	# routine to make a new FFT window from the time-windowed data selected
	def newFFTwin2(self, widget, mode=0):
		self.lastFFTsubplots = self.numFFTsubplots

		# mode = 0: amplitude only
		# mode = 1: normalised amplitude
		# mode = 2: amplitude and phase
		# mode = 3: abs and phase of (T)
		# mode = 4: real and imag parts of (T)
		# mode = 5: real and imag parts of (1/T - 1)
		# mode = 6: refractive index determination
		if (mode == 0) or (mode == 1):
			self.numFFTsubplots=[1,1]
		elif (mode > 1):
			self.numFFTsubplots = [2,1]

		if mode==5:   # only run fftoptions dialog if doing refractive index calc
			fftOptions,fftOptResult=self.getFFToptions(mode)
			print fftOptions, fftOptResult
		else:
			fftOptions={}
			fftOptResult=1


		if not fftOptResult:
			print 'PlotWidget2.newFFTwin()::getFFToptions dialog was cancelled'
			return

		if not self.lastFFTsubplots == self.numFFTsubplots:
			newWin = 1
		else:
			newWin = 0

#		lineNum=self.cmbBox.get_active()
#		print lineNum

		xmin=self.axis.r1._x
		xmax=xmin + self.axis.r1._width

		l=self.axis.get_lines()
#		if len(l)>=3:
#			lines=l[2:]
#		else:
		lines=l

		for lineNum in range(len(l)):
#			print lineNum
			xdata=getp(lines[lineNum],'xdata')
			ydata=getp(lines[lineNum],'ydata')
			col=getp(lines[lineNum],'color')
			lwidth=getp(lines[lineNum],'linewidth')
			lstyle=getp(lines[lineNum],'linestyle')

			lineProps=dict(color=col,linewidth=lwidth,linestyle=lstyle)

			firstPoint=0
			lastPoint=len(xdata)-1

			for m in range(len(xdata)):
				if xdata[m]>xmin:
					firstPoint=m
					break

			for m in range(len(xdata)):
				if xdata[m]>xmax:
					lastPoint=m
					break

#			print firstPoint, lastPoint

			xlabel = self.axis.get_xlabel()
			if '(mm)' in xlabel:
				xunit = 'mm'
			elif '(ps)' in xlabel:
				xunit = 'ps'
			else:
				xunit = 's'


			if (len(self.fftWinList)==0) or (newWin==1):
				titstr = 'FFT window ' + str(len(self.fftWinList)+1)
#				win = NewWindow(title=titstr)
				newplot=PlotWidget2(numSubplots=self.numFFTsubplots,makeTB=True)
				#p=PlotWidget2(mainProg=True)
#				win.addWidget(newplot.vbox)
#				win.win.connect('destroy',self.fftWinList.remove,len(self.fftWinList)+1)


				if not xdata == None:
					if mode < 3:
						newplot.plotFFT(newplot.axis, xdata[firstPoint:lastPoint],ydata[firstPoint:lastPoint], xunit=xunit, lineprops=lineProps, mode=mode)
						print lineNum, firstPoint, lastPoint

					elif mode == 3:   # plot |T|, arg T
						ydata2=getp(lines[0],'ydata') # reference is Line 0
						Eon =ydata[firstPoint:lastPoint]
						Eoff=ydata2[firstPoint:lastPoint]

						freq, cfieldOn, xlabel  = takeFFT(xdata[firstPoint:lastPoint], Eon, xunit)
						freq2, cfieldOff, xlabel  = takeFFT(xdata[firstPoint:lastPoint], Eoff, xunit)

						exprn = cfieldOn/cfieldOff

						newplot.plotData(newplot.axisList[0], freq,abs(exprn), xlabel=xlabel, ylabel='|T|', lineprops=lineProps)
						newplot.plotData(newplot.axisList[1], freq,unwrap(angle(exprn)), xlabel=xlabel, ylabel='<T', lineprops=lineProps)
	#					newplot.plotFFT(newplot.axis, xdata[firstPoint:lastPoint],ydata[firstPoint:lastPoint], xunit=xunit, lineprops=lineProps, mode=mode)

					elif mode == 4:   # plot Re T, Im T
						ydata2=getp(lines[0],'ydata') # reference is Line 0
						Eon =ydata[firstPoint:lastPoint]
						Eoff=ydata2[firstPoint:lastPoint]

						freq, cfieldOn, xlabel  = takeFFT(xdata[firstPoint:lastPoint], Eon, xunit)
						freq2, cfieldOff, xlabel  = takeFFT(xdata[firstPoint:lastPoint], Eoff, xunit)

						exprn = cfieldOn/cfieldOff

						newplot.plotData(newplot.axisList[0], freq,real(exprn), xlabel=xlabel, ylabel='Re[exprn]', lineprops=lineProps)
						newplot.plotData(newplot.axisList[1], freq,imag(exprn), xlabel=xlabel, ylabel='Im[exprn]', lineprops=lineProps)
	#					newplot.plotFFT(newplot.axis, xdata[firstPoint:lastPoint],ydata[firstPoint:lastPoint], xunit=xunit, lineprops=lineProps, mode=mode)

					elif mode == 5:   # plot cond \propto 1/T - 1
						ydata2=getp(lines[0],'ydata')
						Eon=ydata[firstPoint:lastPoint]*(-0.01) + ydata2[firstPoint:lastPoint]
						Eoff=ydata2[firstPoint:lastPoint]

						freq, cfieldOn, xlabel  = takeFFT(xdata[firstPoint:lastPoint], Eon, xunit)
						freq2, cfieldOff, xlabel  = takeFFT(xdata[firstPoint:lastPoint], Eoff, xunit)

						exprn = cfieldOff/cfieldOn - 1

						newplot.plotData(newplot.axisList[0], freq,real(exprn), xlabel=xlabel, ylabel='Re[exprn]', lineprops=lineProps)
						newplot.plotData(newplot.axisList[1], freq,imag(exprn), xlabel=xlabel, ylabel='Im[exprn]', lineprops=lineProps)
	#					newplot.plotFFT(newplot.axis, xdata[firstPoint:lastPoint],ydata[firstPoint:lastPoint], xunit=xunit, lineprops=lineProps, mode=mode)

					elif mode == 6:   # plot refractive index
						xdata=getp(lines[fftOptions['Reference:']],'xdata')

						ydata=getp(lines[fftOptions['Sample:']],'ydata')
						ydata2=getp(lines[fftOptions['Reference:']],'ydata')

						if fftOptions['Calculate d,n\n(needs 1st internal\nreflection in sample)']:
							ns, d = getSampleThickness(xdata, xunit, ydata2, ydata, peakWidth=20)
						else:
							ns = float(fftOptions['Assume n ='])
							d = float(fftOptions['Assume thickness d ='])

						print 'Calculating refractive index using ns='+str(ns)+', d='+str(d)

						xref=xdata[firstPoint:lastPoint]
						xsample=xdata[firstPoint:lastPoint]
						Esample=ydata[firstPoint:lastPoint]
						Eref   =ydata2[firstPoint:lastPoint]

						sf = int(fftOptions['Zero padding'])
						xPad, ErPadded = zeropad(xref,Eref,expansion=sf)
						xPad2, EsPadded = zeropad(xsample,Esample,expansion=sf)
	#					print xPad[1]-xPad[0], xdata[1]-xdata[0]
						if fftOptions['Remove 1st\nreflection']:
							EsPadded = zeroSecondPeak(EsPadded,peakWidth=40)

						self.plotData(self.axisList[0], xPad, ErPadded, lineprops=dict(color='b', linewidth=4,linestyle='--'))
						self.plotData(self.axisList[0], xPad2, EsPadded, lineprops=dict(color='r', linewidth=4,linestyle='--'))
						onAutoScale(widget,self.axisList[0],self.canvas)

						freq, cfieldSample, xlabel  = takeFFT(xPad, EsPadded, xunit=xunit)
						freq2, cfieldRef, xlabel    = takeFFT(xPad, ErPadded, xunit=xunit)
	#					freq, cfieldSample, xlabel  = takeFFT(xdata[firstPoint:lastPoint], Esample, xunit)
	#					freq2, cfieldRef, xlabel    = takeFFT(xdata[firstPoint:lastPoint], Eref, xunit)

						trans=cfieldSample/cfieldRef

						tvstsv = 4 * ns /((ns+1)**2)
						absn = (-2.0 / d) * log(abs(trans)/(tvstsv))
						refrIndex = 1+ 2.998e8 * -1*unwrap(angle(trans)) / (2*pi*d*freq*1e12)

						newplot.plotData(newplot.axisList[0], freq,refrIndex, xlabel=xlabel, ylabel='n', lineprops=lineProps)
						newplot.plotData(newplot.axisList[1], freq2,absn, xlabel=xlabel, ylabel='alpha', lineprops=lineProps)

	#					newplot.plotFFT(newplot.axis, xdata[firstPoint:lastPoint],ydata[firstPoint:lastPoint], xunit=xunit, lineprops=lineProps, mode=mode)

				newplot.win.show_all()

				self.fftWinList.append(newplot)
			
			else:
				self.fftWinList[0].plotFFT(self.fftWinList[0].axis, xdata[firstPoint:lastPoint],ydata[firstPoint:lastPoint], xunit=xunit, lineprops=lineProps, mode=mode)

#		print 'here'




	def appendToList(self,plotID,xlabel,ylabel):
		## get all properties of object
		#prop=matplotlib.artist.getp(plotID)
		#print prop
		self.cmbBox.append_text('Line '+ str(len(self.lineStore)))
		self.cmbBox.set_active(len(self.lineStore))
		
		self.lineStore.append(plotID)
		#print self.lineStore
	

	def fitExp(self, widget=None):
		lineNum= self.cmbBox.get_active()
		l=self.axis.get_lines()
#		if len(l)>=3:
#			lines=l[2:]
#		else:
		lines=l
		xdata  = getp(lines[lineNum],'xdata')
		ydata  = getp(lines[lineNum],'ydata')
		col    = getp(lines[lineNum],'color')
		lwidth = getp(lines[lineNum],'linewidth')
		lstyle = getp(lines[lineNum],'linestyle')
		if lstyle=='-':
			newlstyle='--'
		else:
			newlstyle='-'

		simx,simy = fitExpDecay(xdata,ydata)

		self.plotData(self.axisList[0], simx, simy, lineprops=dict(color=col,linewidth=lwidth,linestyle=newlstyle),addToList=True)

		self.cmbBox.set_active(lineNum) # make the data line that we fitted to active again


	def fitPolynomial(self, widget=None, mode=0):
		lineNum= self.cmbBox.get_active()
		l=self.axis.get_lines()
#		if len(l)>=3:
#			lines=l[2:]
#		else:
		lines=l
		xdata  = getp(lines[lineNum],'xdata')
		ydata  = getp(lines[lineNum],'ydata')
		col    = getp(lines[lineNum],'color')
		lwidth = getp(lines[lineNum],'linewidth')
		lstyle = getp(lines[lineNum],'linestyle')
		if lstyle=='-':
			newlstyle='--'
		else:
			newlstyle='-'

		# old option : set xmin and xmax according to axis positions.
		# new option : gets from fit dialog
		if 0:
			xmin=self.axis.r1._x
			xmax=xmin + self.axis.r1._width

			firstPoint=0
			lastPoint=len(xdata)-1

			for m in range(len(xdata)):
				if xdata[m]>xmin:
					firstPoint=m
					break

			for m in range(len(xdata)):
				if xdata[m]>xmax:
					lastPoint=m
					break

		if mode==2:
			self.fitExp()
			return
		elif mode==3:
			print 'subtract exponential from time windowed data'

			if 1:
				xmin=self.axis.r1._x
				xmax=xmin + self.axis.r1._width

				firstPoint=0
				lastPoint=len(xdata)-1

				for m in range(len(xdata)):
					if xdata[m]>xmin:
						firstPoint=m
						break

				for m in range(len(xdata)):
					if xdata[m]>xmax:
						lastPoint=m
						break
			print xmin,xmax

			if 'mm' in self.axis.get_xlabel():
				xsf=0.15
			else:
				xsf=1
			s=SimLattice(xdata[firstPoint:lastPoint]/xsf*1e-12,ydata[firstPoint:lastPoint])
			self.plotData(self.axisList[0], s.time/1e-12*xsf, s.dRlat, lineprops=dict(color=col,linewidth=lwidth,linestyle='-'),addToList=True,reDraw=True)

			return
		else:
#			get value of polynomial
			resultDict, result=self.getFitOptions(mode)
			if result:
				order=int(resultDict['Polynomial order'])
				xmin = float(resultDict['Min x'])
				xmax = float(resultDict['Max x'])
			else:
				print 'PlotWidget2.fitPolynomial()::getFitOptions dialog was cancelled'
				return

		firstPoint=0
		lastPoint=len(xdata)-1

		for m in range(len(xdata)):
			if xdata[m]>xmin:
				firstPoint=m
				break

		for m in range(len(xdata)):
			if xdata[m]>xmax:
				lastPoint=m
				break

		print '\nFitting polynomial of order '+str(order)+' over range '+str(xmin)+', ' + str(xmax)

		fitparams = polyfit(xdata[firstPoint:lastPoint], ydata[firstPoint:lastPoint], order)
		fitfn = poly1d(fitparams)

#		paramStr = '%(mu)4.3f, %(sigma)4.3f' % {'mu':fitParams[0], 'sigma':fitParams[1]}
#		self.axisList[0].text(fitParams[0]-fitParams[1],max(simBeamShape), paramStr,color='r', fontsize=18)

		paramStr = ''
		for m in range(order+1):
#			print m
			paramStr='%(z)s %(x)4.3f x^%(y)i +' % {'x':fitparams[order-m],'y':(m),'z':paramStr}
		self.axisList[0].text(xdata[firstPoint],ydata[firstPoint], paramStr[:-2],color='r', fontsize=18)

		print 'Fit parameters are:'
		print fitparams

		ylim=self.axisList[0].get_ylim()

#		self.axisList[0].grid(False)
		self.plotData(self.axisList[0], xdata, fitfn(xdata), lineprops=dict(color=col,linewidth=lwidth,linestyle=newlstyle),addToList=True,reDraw=False)
		self.axisList[0].set_ylim(ylim)
		self.canvas.draw()


		self.cmbBox.set_active(lineNum) # make the data line that we fitted to active again

		return


	def getBeamWidth(self, widget=None):
		lineNum=self.cmbBox.get_active()
		l=self.axis.get_lines()
#		if len(l)>=3:
#			lines=l[2:]
#		else:
		lines=l
		xdata=getp(lines[lineNum],'xdata')
		ydata=getp(lines[lineNum],'ydata')

		simBeamShape, beamShape, fitParams=findBeamwidth(xdata,ydata)
		grady1 = abs(gradient(ydata))
		grady1 = grady1/max(grady1)*max(ydata)

		paramStr = '%(mu)4.3f, %(sigma)4.3f' % {'mu':fitParams[0], 'sigma':fitParams[1]}
		self.axisList[0].text(fitParams[0]-fitParams[1],max(simBeamShape), paramStr,color='r', fontsize=18)

		self.plotData(self.axisList[0], xdata, simBeamShape, lineprops=dict(color='r', linewidth=2,linestyle='-'),addToList=True)
		self.plotData(self.axisList[0], xdata, grady1, lineprops=dict(color='y', linewidth=2,linestyle='-',marker='.'),addToList=True)

		legStr = 'Beam centred at mu = %(mu)4.3f, beam width sigma = %(sigma)4.3f' % {'mu':fitParams[0], 'sigma':fitParams[1]}
		print legStr



	def getFitOptions(self, mode):
		newDlg=NewDialog(self.win)
#		for x in self.fftWinList:
#			printClass(x)

		out=self.cmbBox.get_model()
		lineList=[]
		for x in out:
			lineList.append(x[0])

		result=0
		resultDict={}
#		resultDict['Sample']=0

		if (mode==0) or (mode==1):
			figList=['New figure']
			paramNames = ['Polynomial order','Min x','Max x']
			paramTypes = ['spn','en','en']
			paramDefaultValues = [mode+1,0,1]

			paramBoxes = ParamWidget(paramNames,paramTypes,paramDefaultValues)
			paramBoxes.vbox.show_all()
			newDlg.add(paramBoxes.frame)

			# add all the default parameters to the results list
			for widget, name in zip(paramBoxes.objectList, paramNames):
				result = getWidgetValue(widget)
				resultDict[name]=result

			for x in range(len(paramBoxes.objectList)):
				if (paramTypes[x]=='cmb') or (paramTypes[x]=='en'):
					paramBoxes.objectList[x].connect("changed",self.getParamValue,paramNames[x],resultDict)
				elif paramTypes[x]=='chk':
					paramBoxes.objectList[x].connect("toggled",self.getParamValue,paramNames[x],resultDict)
				elif (paramTypes[x]=='spn'):
					paramBoxes.objectList[x].connect("value-changed",self.getParamValue,paramNames[x],resultDict)	

			result=newDlg.run()

		return resultDict, result



	def getFFToptions(self, mode):
		newDlg=NewDialog(self.win)
#		for x in self.fftWinList:
#			printClass(x)

		out=self.cmbBox.get_model()
		lineList=[]
		for x in out:
			lineList.append(x[0])

		result=0
		resultDict={}
#		resultDict['Sample']=0

		if mode==5:
			figList=['New figure']
			paramNames = ['Plot to figure:','Sample:','Reference:','Calculate d,n\n(needs 1st internal\nreflection in sample)','Assume n =','Assume thickness d =','Zero padding','Remove 1st\nreflection']
			paramTypes = ['cmb','cmb','cmb','chk','en','en','spn','chk']
			paramDefaultValues = [figList,lineList,lineList,0,'3.5','370e-6',1.0,0]

			paramBoxes = ParamWidget(paramNames,paramTypes,paramDefaultValues)
			paramBoxes.vbox.show_all()
			newDlg.add(paramBoxes.frame)

			# add all the default parameters to the results list
			for widget, name in zip(paramBoxes.objectList, paramNames):
				result = getWidgetValue(widget)
				resultDict[name]=result

			for x in range(len(paramBoxes.objectList)):
				if (paramTypes[x]=='cmb') or (paramTypes[x]=='en'):
					paramBoxes.objectList[x].connect("changed",self.getParamValue,paramNames[x],resultDict)
				elif paramTypes[x]=='chk':
					paramBoxes.objectList[x].connect("toggled",self.getParamValue,paramNames[x],resultDict)
				elif paramTypes[x]=='spn':
					paramBoxes.objectList[x].connect("value-changed",self.getParamValue,paramNames[x],resultDict)

			result=newDlg.run()


			if resultDict['Sample:']==resultDict['Reference:']:
				resultDict['Reference:']=0
				resultDict['Sample:']=1
				print 'Warning: chose the same sample and reference data sets, defaulting to first line=reference and second line=sample'

		return resultDict, result



	def editPlotParamsOld(self, widget):
		newDlg=NewDialog(self.win)

		result=0
		resultDict={}

		xlabel=self.axis.get_xlabel()
		ylabel=self.axis.get_ylabel()
		title=self.axis.get_title()
		xmin,xmax = self.axis.get_xlim()
		ymin,ymax = self.axis.get_ylim()

#		scaleList=['linear','log','symlog']
		scaleList=['linear','log']
		xsc = self.axis.get_xscale()
		xscale=0
		for x in range(len(scaleList)):
			if xsc == scaleList[x]:
				xscale = x
		ysc = self.axis.get_yscale()
		yscale=0
		for y in range(len(scaleList)):
			if ysc == scaleList[y]:
				yscale = y


		paramNames = ['Title','x-axis label','x-axis min','x-axis max','x-axis scale','y-axis label','y-axis min','y-axis max','y-axis scale']
		paramTypes = ['en','en','en','en','cmb','en','en','en','cmb']
		paramDefaultValues = [title,xlabel,xmin,xmax,scaleList,ylabel,ymin,ymax,scaleList]

		paramBoxes = ParamWidget(paramNames,paramTypes,paramDefaultValues)

		paramBoxes.objectList[4].set_active(xscale)
		paramBoxes.objectList[8].set_active(yscale)

		paramBoxes.vbox.show_all()
		newDlg.add(paramBoxes.frame)

		# add all the default parameters to the results list
		for widget, name in zip(paramBoxes.objectList, paramNames):
			result = getWidgetValue(widget)
			resultDict[name]=result

		for x in range(len(paramBoxes.objectList)):
			if paramTypes[x]=='cmb':
				paramBoxes.objectList[x].connect("changed",self.getParamValue,paramNames[x],resultDict)
			elif paramTypes[x]=='chk':
				paramBoxes.objectList[x].connect("toggled",self.getParamValue,paramNames[x],resultDict)
			elif paramTypes[x]=='en':
				paramBoxes.objectList[x].connect("changed",self.getParamValue,paramNames[x],resultDict)


		result=newDlg.run()

		if result:
			self.axLabel(self.axis, resultDict['x-axis label'], resultDict['y-axis label'])   # set x and y-axis labels
			self.axis.set_title(resultDict['Title'],fontdict=self.titleLabelDict)    # set plot title

			self.axis.set_xscale(scaleList[resultDict['x-axis scale']])
			self.axis.set_yscale(scaleList[resultDict['y-axis scale']]) # note - must set scale before setting axis limits as there seems to be an autoscaling routine called by matplotlib after setting the axis scale.
			self.axis.set_xlim((float(resultDict['x-axis min']),float(resultDict['x-axis max'])))
			self.axis.set_ylim((float(resultDict['y-axis min']),float(resultDict['y-axis max'])))			

			self.canvas.draw()

		return resultDict, result



	def editPlotParams(self, widget):
		newDlg=NewDialog(self.win,title='Plot parameters')	# must pass parent to dialog (so it can be modal)

		axis=self.axis

		result=0
		resultDict={}
		resultDict['Grid colour']=self.axis.get_xgridlines()[0].get_color()
#		print resultDict

		xlabel=axis.get_xlabel()
		ylabel=axis.get_ylabel()
		title=axis.get_title()
		xmin,xmax = axis.get_xlim()
		ymin,ymax = axis.get_ylim()
		gridLine=axis.get_xaxis().get_gridlines()[0]
		grid_colour=gridLine.get_color()
		grid_linestyle=gridLine.get_linestyle()
		grid_linewidth=gridLine.get_linewidth()
#		drawx = int(self.plotWidgetList[m].drawx)
#		drawy = int(self.plotWidgetList[m].drawy)

#		scaleList=['linear','log','symlog']
		scaleList=['linear','log']
		xsc = axis.get_xscale()
		xscale=0
		for x in range(len(scaleList)):
			if xsc == scaleList[x]:
				xscale = x
		ysc = axis.get_yscale()
		yscale=0
		for y in range(len(scaleList)):
			if ysc == scaleList[y]:
				yscale = y

		frameOn=axis.get_frame_on()

		######################### DEFINE WIDGETS FOR TABBED PROPERTIES BOX

		if 'THz' in xlabel:
			oldXunit='THz'
		elif ('cm-1' in xlabel) or ('cm^-1' in xlabel) or ('cm$^{-1}$' in xlabel):
			oldXunit='cm-1'
		elif 'eV' in xlabel:
			oldXunit='eV'
		elif 'meV' in xlabel:
			oldXunit='meV'
		elif 'um' in xlabel:
			oldXunit='um'
		elif 'nm' in xlabel:
			oldXunit='nm'
		else:
			oldXunit=''

		unitOptions=['THz','cm-1','eV','meV','um','nm']

		##### Axis properties
		paramNames = ['Title','x-axis label','original x-units','new x-units','x-axis min','x-axis max','x-axis scale','draw x=0','y-axis label','y-axis min','y-axis max','y-axis scale','draw y=0','Axis frame']
		paramTypes = ['en','en','lbl','cmb','en','en','cmb','chk','en','en','en','cmb','chk','chk']
		paramDefaultValues = [title,xlabel,oldXunit,unitOptions,xmin,xmax,scaleList,False,ylabel,ymin,ymax,scaleList,False,frameOn]

		paramBoxes = ParamWidget(paramNames,paramTypes,paramDefaultValues)

		paramBoxes.objectList[6].set_active(xscale)
		paramBoxes.objectList[11].set_active(yscale)

		paramBoxes.vbox.show_all()


		##### Grid properties
		paramNames2 = ['Show grid','Grid colour','Grid linestyle','Grid linewidth']
		paramTypes2 = ['chk','imagebtn','en','en']
		paramDefaultValues2 = [1,gtk.STOCK_SELECT_COLOR,grid_linestyle,grid_linewidth]

		paramBoxes2 = ParamWidget(paramNames2,paramTypes2,paramDefaultValues2)


		if grid_colour==None:
			grid_colour=[1,1,1]
		col=colorConverter.to_rgb(grid_colour)

		gridColour=col
		# connect callbacks for special routines (generic items, e.g. cmb, en, chk handled below)
		paramBoxes2.objectList[1].connect("clicked",self.getColour,paramNames2[1],resultDict,gridColour)
		r=gridColour[0]
		g=gridColour[1]
		b=gridColour[2]
		paramBoxes2.objectList[1].modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(red=r,green=g,blue=b))	# set colour

#		self.getColour(None,paramNames2[1],resultDict,self.plotWidgetList[m].info.gridColour)

		paramBoxes2.vbox.show_all()

		rect=self.axis.get_position()
		##### Subplot location properties
		paramNames3 = ['Axis left','Axis bottom','Axis width','Axis height']
		paramTypes3 = ['hscale','hscale','hscale','hscale']
		paramDefaultValues3 = [rect.x0,rect.y0,rect.width,rect.height]

		paramBoxes3 = ParamWidget(paramNames3,paramTypes3,paramDefaultValues3)
		paramBoxes3.vbox.show_all()


		##### Axis tick marks
		try:
			xmaj=self.xmajorSpacing
		except AttributeError:
			xt=self.axis.get_xticks()
			xmaj=xt[1]-xt[0]
#			xmaj='10'

		try:
			xmin=self.xminorSpacing
		except AttributeError:
			xmin=xmaj/5.0

		try:
			xstr=self.xtickFormatStr
		except AttributeError:
			xstr='%4.3g'

		try:
			ymaj=self.ymajorSpacing
		except AttributeError:
			yt=self.axis.get_yticks()
			ymaj=yt[1]-yt[0]
#			ymaj='10'

		try:
			ymin=self.yminorSpacing
		except AttributeError:
			ymin=ymaj/5.0
#			ymin='1'

		try:
			ystr=self.ytickFormatStr
		except AttributeError:
			ystr='%4.3g'

		paramNames4 = ['x major spacing','x minor spacing','x tick format string','y major spacing','y minor spacing','y tick format string']
		paramTypes4 = ['en','en','en','en','en','en']
		paramDefaultValues4 = [xmaj,xmin,xstr,ymaj,ymin,ystr]

		paramBoxes4 = ParamWidget(paramNames4,paramTypes4,paramDefaultValues4)
		paramBoxes4.vbox.show_all()


		##################################### MAKE TABBED CONTAINER AND PUT WIDGETS IN
		t=TabbedContainer(tabs=['Axes','Grid','Location','Ticks'],vboxList=[paramBoxes.frame,paramBoxes2.frame,paramBoxes3.frame,paramBoxes4.frame])
		t.table.show_all()

		newDlg.add(t.table)		# adds table, which contains notebook, to dialog
#		newDlg.add(paramBoxes.frame)


		#self.connectStuff(paramBoxes0.objectList,paramTypes0,paramNames0,resultDict)
		self.connectStuff(paramBoxes.objectList,paramTypes,paramNames,resultDict)
		self.connectStuff(paramBoxes2.objectList,paramTypes2,paramNames2,resultDict)
		self.connectStuff(paramBoxes3.objectList,paramTypes3,paramNames3,resultDict)
		self.connectStuff(paramBoxes4.objectList,paramTypes4,paramNames4,resultDict)

		result=newDlg.run()

		if result:
			print resultDict
			self.xmajorSpacing=resultDict['x major spacing']
			self.xminorSpacing=resultDict['x minor spacing']
			self.ymajorSpacing=resultDict['y major spacing']
			self.yminorSpacing=resultDict['y minor spacing']

			#try:
			rect=[resultDict['Axis left'],resultDict['Axis bottom'],resultDict['Axis width'],resultDict['Axis height']]
			self.axis.set_position(rect)
			#except:
			#	print 'could not set axis position'
			#	pass

			try:
				self.axis.set_frame_on(bool(resultDict['Axis frame']))
			except:
				print 'could not set axis frame'
				pass

			# draw grid if asked for
			if resultDict['Show grid']:
				if resultDict['Grid colour']==None:
					gc='k'
				else:
					gc=resultDict['Grid colour']
				self.axis.grid(color=gc,linewidth=resultDict['Grid linewidth'],linestyle=resultDict['Grid linestyle'])
				print 'show grid'
			else:
				self.axis.grid(b=False)
				print 'no grid'

			newXunit=unitOptions[resultDict['new x-units']]
			if oldXunit==newXunit:
				newxlabel=resultDict['x-axis label']
			else:
				print 'x unit changed to '+str(newXunit)

				if newXunit=='THz':
					newxlabel='Frequency (THz)'
				elif newXunit=='cm-1':
					newxlabel='Wavenumber (cm$^{-1}$)'
				elif newXunit=='eV':
					newxlabel='Energy (eV)'
				elif newXunit=='meV':
					newxlabel='Energy (meV)'
				elif newXunit=='nm':
					newxlabel='Wavelength (nm)'
				elif newXunit=='um':
					newxlabel='Wavelength ($\mu$m)'

			self.axLabel(self.axis, newxlabel, resultDict['y-axis label'])   # set x and y-axis labels

			self.axis.set_title(resultDict['Title'],fontdict=titleLabelDict)    # set plot title
			self.axis.set_xscale(scaleList[resultDict['x-axis scale']])
			self.axis.set_yscale(scaleList[resultDict['y-axis scale']]) # note - must set scale before setting axis limits as there seems to be an autoscaling routine called by matplotlib after setting the axis scale.
			self.axis.set_xlim((float(resultDict['x-axis min']),float(resultDict['x-axis max'])))
			self.axis.set_ylim((float(resultDict['y-axis min']),float(resultDict['y-axis max'])))

			try:
				self.setTicks(self.axis.get_xaxis(),resultDict['x major spacing'],resultDict['x minor spacing'],resultDict['x tick format string'])
			except:
				print 'could not set x ticks'
				pass

			try:
				self.setTicks(self.axis.get_yaxis(),resultDict['y major spacing'],resultDict['y minor spacing'],resultDict['y tick format string'])
			except:
				print 'could not set y ticks'
				pass


			self.canvas.draw()
		return resultDict, result


	def setTicks(self,axis,majorSpacing=1.0,minorSpacing=0.2,formatStr='%4.3g',useMaxN=False):

		if axis.get_scale()=='log':
			useLog=True
		else:
			useLog=False


		if not useLog:
			if not useMaxN:
				majorLocator   = MultipleLocator(float(majorSpacing))
				majorFormatter = FormatStrFormatter(formatStr)
				minorLocator   = MultipleLocator(float(minorSpacing))
			else:
				majorLocator   = MaxNLocator(4)
				majorFormatter = FormatStrFormatter(formatStr)
				minorLocator   = AutoMinorLocator()

			axis.set_major_locator(majorLocator)
			axis.set_major_formatter(majorFormatter)
			axis.set_minor_locator(minorLocator)

		else:
			majorLocator   = LogLocator()
			majorFormatter = LogFormat()
#			minorLocator   = MultipleLocator(float(minorSpacing))

			axis.set_major_locator(majorLocator)
			axis.set_major_formatter(majorFormatter)



		return


	def editLegendOld(self, widget):
		newDlg=NewDialog(self.win,title='Edit lines and legend')

		result=0
		resultDict={}

		leg=self.axis.legend()

		legPositions=['no legend','upper right','upper left','lower left','lower right','right','centre left','centre right','lower centre','upper centre','centre']

		handles, legLabels = self.axis.get_legend_handles_labels()
		self.axis.legend(handles, legLabels)
		legLabelsStr=str(legLabels).lstrip('[').rstrip(']')

		paramNames = ['Legend position','Transparency']
		paramTypes = ['cmb','en']
		paramDefaultValues = [legPositions,0.5]

		paramBoxes = ParamWidget(paramNames,paramTypes,paramDefaultValues)
		paramBoxes.vbox.show_all()
		newDlg.add(paramBoxes.frame)

		paramBoxes.objectList[0].set_active(1)

		# add all the default parameters to the results list
		for widget, name in zip(paramBoxes.objectList, paramNames):
			result = getWidgetValue(widget)
			resultDict[name]=result

		for x in range(len(paramBoxes.objectList)):
			if paramTypes[x]=='cmb':
				paramBoxes.objectList[x].connect("changed",self.getParamValue,paramNames[x],resultDict)
			elif paramTypes[x]=='chk':
				paramBoxes.objectList[x].connect("toggled",self.getParamValue,paramNames[x],resultDict)
			elif paramTypes[x]=='en':
				paramBoxes.objectList[x].connect("changed",self.getParamValue,paramNames[x],resultDict)

		paramNames2=[]
		paramTypes2=[]
		for m in range(len(handles)):
			paramNames2.append('Label '+str(m))
			paramTypes2.append('en')

		paramBoxes2 = ParamWidget(paramNames2,paramTypes2,legLabels)
		paramBoxes2.vbox.show_all()
		newDlg.add(paramBoxes2.frame)

		for x in range(len(paramBoxes2.objectList)):
			if paramTypes2[x]=='cmb':
				paramBoxes2.objectList[x].connect("changed",self.getParamValue,paramNames2[x],resultDict)
			elif paramTypes2[x]=='chk':
				paramBoxes2.objectList[x].connect("toggled",self.getParamValue,paramNames2[x],resultDict)
			elif paramTypes2[x]=='en':
				paramBoxes2.objectList[x].connect("changed",self.getParamValue,paramNames2[x],resultDict)


		result=newDlg.run()


		if result:
			print resultDict

			for m in range(len(handles)):
				try:
					newLabel=resultDict['Label '+str(m)].lstrip("'").rstrip("'")
	#				print newLabel
					legLabels[m]=newLabel
					handles[m].set_label(newLabel)
				except KeyError:	# if not found in resultDict then no change made...
					pass

			if resultDict['Legend position']==0:
				self.axis.legend_ = None
			else:
				leg=self.axis.legend(handles,legLabels,loc=int(resultDict['Legend position']), fancybox=True, shadow=True)

			leg.get_frame().set_alpha(1.0-float(resultDict['Transparency']))
			self.currentLegTrans=1.0-float(resultDict['Transparency'])
			self.currentLegPos  =resultDict['Legend position']

			self.canvas.draw()

		return resultDict, result


	def connectStuff(self,objects,paramTypes,paramNames,resultDict):
		# add all the default parameters to the results list
		for widget, name in zip(objects, paramNames):
			result = getWidgetValue(widget)
			resultDict[name]=result

		for x in range(len(objects)):
			if paramTypes[x]=='cmb':
				objects[x].connect("changed",self.getParamValue,paramNames[x],resultDict)
			elif paramTypes[x]=='chk':
				objects[x].connect("toggled",self.getParamValue,paramNames[x],resultDict)
			elif paramTypes[x]=='en':
				objects[x].connect("changed",self.getParamValue,paramNames[x],resultDict)
			elif paramTypes[x]=='spn':
				objects[x].connect("changed",self.getParamValue,paramNames[x],resultDict)
			elif paramTypes[x]=='hscale':
				objects[x].connect("value-changed",self.getParamValue,paramNames[x],resultDict)


	def editLegend(self, widget):
		newDlg=NewDialog(self.win,title='Edit lines and legend')

		axis=self.axis
		

		leg=axis.get_legend()
		if leg==None:
			handles, labels = axis.get_legend_handles_labels()
			print labels
			leg=axis.legend(handles,labels)
		

		result=0
		resultDict={}

		lineColours=[]
		for x in leg.get_lines():
			lineColours.append(x.get_color())
		#print lineColours

		legendFontSize=leg.get_texts()[0].get_fontsize()

#		leg=axis.legend()

		legPositions=['no legend','upper right','upper left','lower left','lower right','right','centre left','centre right','lower centre','upper centre','centre']

		handles, legLabels = axis.get_legend_handles_labels()
#		print legLabels
		axis.legend(handles, legLabels)
		legLabelsStr=str(legLabels).lstrip('[').rstrip(']')

		alpha = leg.get_frame().get_alpha()
		if alpha==None:
			alpha = 1.0
		trans = 1.0-alpha
		paramNames = ['Legend position','Transparency','Box','Shadow','Legend font size']
		paramTypes = ['cmb','en','chk','chk','spn']
		paramDefaultValues = [legPositions,str(trans),leg.get_frame().get_visible(),int(leg.shadow),int(legendFontSize)]

		paramBoxes = ParamWidget(paramNames,paramTypes,paramDefaultValues)
		paramBoxes.vbox.show_all()

		paramBoxes.objectList[0].set_active(leg._loc)


		paramNames2=[]
		paramTypes2=[]
		paramDefaults2=[]
		for m in range(len(handles)):
			paramNames2.append('Line '+str(m))
			paramTypes2.append('en')
			paramDefaults2.append(legLabels[m])
			paramNames2.append('Colour '+str(m))
			paramTypes2.append('imagebtn')
			paramDefaults2.append(gtk.STOCK_SELECT_COLOR)
			paramNames2.append('Style '+str(m))
			paramTypes2.append('cmb')
			paramDefaults2.append(self.ALLOWED_LINESTYLES)
			paramNames2.append('Marker '+str(m))
			paramTypes2.append('en')
			paramDefaults2.append('-')


		paramBoxes2 = ParamWidget(paramNames2,paramTypes2,paramDefaults2)
		paramBoxes2.vbox.show_all()

		##################################### MAKE TABBED CONTAINER AND PUT WIDGETS IN
		t=TabbedContainer(tabs=['Lines','Legend'],vboxList=[paramBoxes2.frame,paramBoxes.frame])
		t.table.show_all()

		newDlg.add(t.table)		# adds table, which contains notebook, to dialog
#		newDlg.add(paramBoxes.frame)
#		newDlg.add(paramBoxes2.frame)


		self.connectStuff(paramBoxes.objectList,paramTypes,paramNames,resultDict)


		for m in range(len(paramNames2)/4):
#			print m, len(paramBoxes2.objectList)
			paramBoxes2.objectList[m*4+1].connect("clicked",self.getColour,paramNames2[m*2+1],resultDict,lineColours[m])
			col= handles[m].get_color()
			col=colorConverter.to_rgb(col)
#			print col
			paramBoxes2.objectList[m*4+1].modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(red=float(col[0]),green=float(col[1]),blue=float(col[2])))	# set colour


		for x in range(len(paramBoxes2.objectList)):
			if paramTypes2[x]=='cmb':
				paramBoxes2.objectList[x].connect("changed",self.getParamValue,paramNames2[x],resultDict)
			elif paramTypes2[x]=='chk':
				paramBoxes2.objectList[x].connect("toggled",self.getParamValue,paramNames2[x],resultDict)
			elif paramTypes2[x]=='en':
				paramBoxes2.objectList[x].connect("changed",self.getParamValue,paramNames2[x],resultDict)



		result=newDlg.run()


		if result:
			print resultDict

			for m in range(len(handles)):
				try:
					newLabel=resultDict['Line '+str(m)].lstrip("'").rstrip("'")
	#				print newLabel
					legLabels[m]=newLabel
					handles[m].set_label(newLabel)
				except KeyError:	# if not found in resultDict then no change made...
					pass

			for m in range(len(handles)):
				try:
					newLineColour=resultDict['Colour '+str(m)]

					line=self.axis.get_lines()[m]
					if not '_line' in line.get_label():
						line.set_color(newLineColour)

				except KeyError:	# if not found in resultDict then no change made...
					pass

			for m in range(len(handles)):
				try:
					newMarker=resultDict['Marker '+str(m)]

					line=self.axis.get_lines()[m]
					if not '_line' in line.get_label():
						if not newMarker=='-':
							line.set_marker(newMarker)

				except KeyError:	# if not found in resultDict then no change made...
					pass


			for m in range(len(handles)):
				try:
					newStyle=self.ALLOWED_LINESTYLES[resultDict['Style '+str(m)]]

					line=self.axis.get_lines()[m]
					if not '_line' in line.get_label():
						line.set_linestyle(newStyle)

				except KeyError:	# if not found in resultDict then no change made...
					pass


			if resultDict['Legend position']==0:
				axis.legend_ = None
			else:
				leg=axis.legend(handles,legLabels,loc=int(resultDict['Legend position']), shadow=resultDict['Shadow'], fancybox=True, prop={'size':int(resultDict['Legend font size'])})

			leg.get_frame().set_visible(resultDict['Box'])
			leg.get_frame().set_alpha(1.0-float(resultDict['Transparency']))
			txt=leg.get_texts()
			for t in txt:
				t.set_fontsize(int(resultDict['Legend font size']))


			self.currentLegTrans=1.0-float(resultDict['Transparency'])
			self.currentLegPos  =resultDict['Legend position']


			self.canvas.draw()


		return resultDict, result


	# Allows user to add additional data sets to a plot
	def addData(self, widget):
		print 'FLAG'


	# Drawingarea event handler
	def change_style(self, widget):
#		print str(widget.get_active())
		style= widget.get_active_text()
		newStyle=style.split(', ')[1]
#		print newStyle

		currentLineNum=self.cmbBox.get_active()
		currentStyle = matplotlib.artist.getp(self.lineStore[currentLineNum],'linestyle')

		if currentLineNum > -1:
			matplotlib.artist.setp(self.lineStore[currentLineNum],'linestyle',newStyle)
			leg=self.axis.legend(loc=self.currentLegPos, fancybox=True, shadow=True)
			leg.get_frame().set_alpha(self.currentLegTrans)
			self.canvas.draw()



	# Drawingarea event handler
	def change_colour(self, widget):
		self.colorseldlg = gtk.ColorSelectionDialog("Select new colour")

		# Get the ColorSelection widget
		colorsel = self.colorseldlg.colorsel

		currentLineNum=self.cmbBox.get_active()
		currentColour = matplotlib.artist.getp(self.lineStore[currentLineNum],'color')

		col=colorConverter.to_rgb(currentColour)

		colorsel.set_previous_color(gtk.gdk.Color(red=col[0],green=col[1],blue=col[2]))
		colorsel.set_current_color(gtk.gdk.Color(red=col[0],green=col[1],blue=col[2]))
		colorsel.set_has_palette(True)

		# Connect to the "color_changed" signal
#		colorsel.connect("color_changed", self.color_changed_cb)
		# Show the dialog
		response = self.colorseldlg.run()
		self.colorseldlg.hide()

		if response == gtk.RESPONSE_OK:
			self.color = colorsel.get_current_color()
		else:
			return 0
#			self.drawingarea.modify_bg(gtk.STATE_NORMAL, self.color)
		
		colorstr=self.color.to_string()
		
		red=int(colorstr[1:5],16)/65535.0
		green=int(colorstr[5:9],16)/65535.0
		blue=int(colorstr[9:13],16)/65535.0

		col=colorConverter.to_rgb(tuple([red,green,blue]))
		self.color=gtk.gdk.Color(red=int(round(65535*red)),green=int(round(65535*green)),blue=int(round(65535*blue)))

		self.colourBtn.modify_bg(gtk.STATE_NORMAL, self.color)

		if currentLineNum > -1:
			matplotlib.artist.setp(self.lineStore[currentLineNum],'color',col)		
			self.canvas.draw()

		return 1


	def toggle_line(self,widget):
		currentLineNum=self.cmbBox.get_active()
		if currentLineNum > -1:
#			self.cmbBox.remove_text(currentLineNum)
#			del self.axis.lines[currentLineNum]
#			del self.lineStore[currentLineNum]
#			self.cmbBox.set_active(0)
#			print 'toggled ',currentLineNum
			newState=not self.axis.lines[currentLineNum].get_visible()
			if newState:
#				widget.set_label('Hide')
				widget.set_stock_id(gtk.STOCK_NO)
				widget.set_tooltip_text('Hide')
			else:
#				widget.set_label('Show')				
				widget.set_stock_id(gtk.STOCK_YES)
				widget.set_tooltip_text('Show')
			self.axis.lines[currentLineNum].set_visible(newState)
#			self.axis.lines[currentLineNum].set_linewidth()
			self.canvas.draw()



	def remove_line(self,widget,currentLineNum=None):
		if currentLineNum==None:
			currentLineNum=self.cmbBox.get_active()

		if currentLineNum > -1:
			self.cmbBox.remove_text(currentLineNum)
			del self.axis.lines[currentLineNum]
			del self.lineStore[currentLineNum]
			self.cmbBox.set_active(0)
			self.canvas.draw()


	def enter_axes(self,event):
#		print 'enter_axes', event.inaxes
		event.inaxes.patch.set_facecolor((0.99,0.8,0.8))
		event.canvas.draw()
		self.axis=event.inaxes


	def leave_axes(self,event):
#		print 'leave_axes', event.inaxes
		event.inaxes.patch.set_facecolor('white')
		event.canvas.draw()
#		self.axis=None


	### Clear the current plot window
	def OnClear(self, widget):
		#self.axis.cla()
		#self.axis.grid(True)
#		axisLines = self.axis.get_lines()

		del self.axis.lines[:]
		self.canvas.draw()

#		for currentLineNum in range(len(self.cmbBox.get_model())+1):
#		if currentLineNum > -1:
#			self.cmbBox.remove_text(currentLineNum)
#			del self.axis.lines[currentLineNum]
#			del self.lineStore[currentLineNum]


	def OnPress(self,event):
		x,y = event.xdata, event.ydata
		currXlim=self.axis.get_xlim()
		currYlim=self.axis.get_ylim()
		lineprops=dict(color='b', linewidth=2,linestyle='o')

		for axis in self.axisList:
			if event.button == 1:   # 1 for left mouse button, 2 for middle, 3 for right
				if self.clickMode == 1:
					oldx=axis.r1._x
					oldwidth=axis.r1._width
					axis.r1._x=x
	#				axis.set_xlim((x,currXlim[1]))
					axis.r1._width=abs(oldx+oldwidth-x)
				elif self.clickMode == 2:
					oldx=axis.r1._x
					axis.r1._width=abs(x-oldx)
	#			elif self.clickMode == 3:
	#				axis.set_ylim((y,currYlim[1]))
	#			elif self.clickMode == 4:
	#				axis.set_ylim((currYlim[0],y))
				elif self.clickMode == 3:
					axis.set_xlim((x,currXlim[1]))
				elif self.clickMode == 4:
					axis.set_xlim((currXlim[0],x))
				elif self.clickMode == 5:
					x0, y0 = findPoint(x,y,axis,self.cmbBox.get_active())
					lineprops=dict(color='b', linewidth=4,linestyle='-',marker='o',markersize=10,markerfacecolor='r')
					self.point = axis.plot([x0],[y0],**lineprops)
				
					labelstr = "%5.3g, %5.3g" % (x0, y0)
					axis.text(x0,y0, labelstr, fontsize=20)

				self.canvas.draw()
			elif event.button == 3:
	#			axis.set_xlim((currXlim[0],x))
	#			self.canvas.draw()
				print 'right mouse button (button 3) pressed'



class PlotZoomToolbar(NavigationToolbar2):
	def __init__(self, canvas, win, axis):
		# create the default toolbar from NavigationToolbar2
		NavigationToolbar2.__init__(self, canvas, win)

		# remove the unwanted (sub-plot) button --- removed this 15/08/14 as it is removing the "hand/grab" button
#		btn = self.get_children()[4]
#		self.remove(btn)

#		btn = self.get_children()[5]
#		self.remove(btn)

#		btn = self.get_children()[5]
#		self.remove(btn)

		self.axis=axis
		self.canvas = canvas

		btn=gtk.ToolButton(gtk.STOCK_ZOOM_IN)
		btn.connect("clicked",zoomIn,axis,canvas)
		btn.set_tooltip_text('Zoom in.')
		self.add(btn)

		btn1=gtk.ToolButton(gtk.STOCK_ZOOM_OUT)
		btn1.connect("clicked",zoomOut,axis,canvas)
		btn1.set_tooltip_text('Zoom out.')
		self.add(btn1)

		btn2=gtk.ToolButton(gtk.STOCK_ZOOM_100)
		btn2.connect("clicked",onAutoScale,axis,canvas)
		btn2.set_tooltip_text('Zoom out (show all data).')
		self.add(btn2)

		btn3=gtk.ToolButton(gtk.STOCK_ZOOM_FIT)
		btn3.connect("clicked",self.zoom)
		btn3.set_tooltip_text('Zoom to rectangle.')
		self.add(btn3)


		#### add figure save (my format) button-->
		btn9=gtk.ToolButton(gtk.STOCK_SAVE_AS)
		btn9.connect("clicked",self.saveFig)
		btn9.set_label('Save')
		btn9.set_tooltip_text('Save figure.')

		self.add(btn9)
		### <--



	def saveFig(self, widget):
		l=self.axis.get_lines()
#		if len(l)>=3:
#			lines=l[2:]
#		else:
		lines=l

		### to add:: choose file via dialog here...

		stub='newfigure'

		xdata=[]
		ydata=[]

		for l in lines:
			x = l.get_xdata()
			y = l.get_ydata()
			xdata.append(x)
			ydata.append(y)

		output = open(stub+'.dat', 'wb')
		pickle.dump(xdata,output)
		pickle.dump(ydata,output)
		output.close()

		### save a new figure file with all the plot options
		axisPropToFile(stub+'.fig',self.axis,datafile=stub+'.dat')





class PlotToolbar(NavigationToolbar2):
	def __init__(self, canvas, win, axis):
		# create the default toolbar from NavigationToolbar2
		NavigationToolbar2.__init__(self, canvas, win)

		# remove the unwanted (sub-plot) button
		for m in range(7):
			btn = self.get_children()[0]
			self.remove(btn)

		btn = self.get_children()[1]
		self.remove(btn)
		btn = self.get_children()[1]
		self.remove(btn)

		self.axis=axis

		self.canvas = canvas

#		sep=gtk.SeparatorToolItem()
#		self.add(sep)
		
		btn4=gtk.ToggleToolButton(gtk.STOCK_SORT_DESCENDING)
		btn4.connect("clicked",OnLogY, axis, canvas)
		btn4.set_label('Log y')
		btn4.set_tooltip_text('Logarithmic y-axis.')
		self.add(btn4)
		


################################################################################
######## Data browser dialog:  #######################################
######## 1. Accepts a list of data file names
######## 2. Lets the user browse the data in the given list of files, or add other data files
class PlotDialog():
	"""This class is used to show PlotDlg"""
	
	PREVIEW_PLOT_POSITION = [0.19,0.14,0.75,0.8]

	def __init__(self,parent,labels,filenameList=[],axisChoice=True,contourPlot=False):
		# do nothing
		self.temp=0
		self.filenameList=filenameList

		# make the dialog
		self.dlg = gtk.Dialog(title="Data chooser",parent=parent,flags=0,buttons=())

		self.btnCancel = self.dlg.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
  		self.btnOk = self.dlg.add_button(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)
		self.btnOk.grab_default()

		shortfilename = self.getShortFilename(filenameList[0])

		shortlist=[]
		for f in filenameList:
			shortlist.append(self.getShortFilename(f))

		self.numCols = len(labels)

		self.vbox=gtk.VBox(homogeneous=False, spacing=0)

		paramNames = ['Filename: ','Add data file: ']
		paramTypes = ['cmb','btn']
		paramDefaultValues = [shortlist,gtk.STOCK_ADD]

		paramBoxes = ParamWidget(paramNames,paramTypes,paramDefaultValues)
		self.cmbFile = paramBoxes.objectList[0]
		self.btnFile = paramBoxes.objectList[1]
#		self.btnFile.set_label('Load another data file')
		self.cmbFile.connect("changed",self.onAxisChanged)

		paramBoxes.frame.set_label('Data files')
		self.vbox.pack_start(paramBoxes.frame)

		hbox=gtk.HBox(homogeneous=False, spacing=0)

		paramNames = ['Num. plot columns: ','Num. plot rows: ','Plot to figure: ','x-axis: ','x scale factor: ','x label: ','Zero x:','y-axis: ','y scale factor: ','Normalise y-axis: ','y label: ','z-axis: ','z scale factor: ','z label: ','Plotting: ']
		paramTypes = ['spn','spn','cmb','cmb','en','en','chk','cmb','en','chk','en','cmb','en','en','lbl']
		paramDefaultValues = [1,1,['1, 1'],labels,1.0,labels[0],0.0,labels,1.0,0,labels[0],shortlist,1.0,labels[0],'']


		paramBoxes = ParamWidget(paramNames,paramTypes,paramDefaultValues)
		self.spnNumCols = paramBoxes.objectList[0]
		self.spnNumRows = paramBoxes.objectList[1]
		self.cmbPlotFig = paramBoxes.objectList[2]
		self.cmbX1 = paramBoxes.objectList[3]
		self.enX1sf = paramBoxes.objectList[4]
		self.enX1lab = paramBoxes.objectList[5]
		self.chkZeroX1 = paramBoxes.objectList[6]
		self.cmbY1 = paramBoxes.objectList[7]
		self.enY1sf = paramBoxes.objectList[8]
		self.chkNorm = paramBoxes.objectList[9]
		self.enY1lab = paramBoxes.objectList[10]
		self.cmbZ1 = paramBoxes.objectList[11]
		self.enZ1sf = paramBoxes.objectList[12]
		self.enZ1lab = paramBoxes.objectList[13]
#		self.btnAdd = paramBoxes.objectList[5]
#		self.btnClear = paramBoxes.objectList[6]
		self.lblPlot = paramBoxes.objectList[14]
		paramBoxes.frame.set_label('Plot options')

		self.cmbX1con = self.cmbX1.connect("changed",self.onAxisChanged)
		self.cmbY1con = self.cmbY1.connect("changed",self.onAxisChanged)
		self.btnFile.connect("clicked",self.onFile)
		self.spnNumCols.connect("value-changed",self.onNumChanged)
		self.spnNumRows.connect("value-changed",self.onNumChanged)
		self.chkNorm.connect("toggled",self.onyNormChanged)

		hbox.pack_start(paramBoxes.frame)

		hboxBtn=gtk.HBox(homogeneous=False, spacing=0)
		self.btnAdd = IconButton(label='Add to plot list',icon=gtk.STOCK_ADD)
		self.btnAddAll = IconButton(label='Add all files',icon=gtk.STOCK_ADD)
		self.btnClear = IconButton(label='Clear plot list',icon=gtk.STOCK_CLEAR)
		self.btnAdd.connect("clicked",self.onAdd)
		self.btnAddAll.connect("clicked",self.onAddAll)
		self.btnClear.connect("clicked",self.onClear)
		hboxBtn.pack_start(self.btnAdd)
		hboxBtn.pack_start(self.btnAddAll)
		hboxBtn.pack_start(self.btnClear)
		nrows=paramBoxes.table.get_property('n-rows')
		paramBoxes.table.attach(hboxBtn, 0, 2, nrows, nrows+1)

		### preview plot widget
		self.previewPlot = PlotWidget2(self.dlg,numSubplots=[1,1,1],figWidth=300,figHeight=300,makeTB=False)
		self.previewPlot.axisList[0].set_position(self.PREVIEW_PLOT_POSITION)
		hbox.pack_start(self.previewPlot.vbox)
		self.vbox.pack_start(hbox)

		self.previewPlot.axis.set_title('Preview of plot')

		self.vbox.show_all()
		self.dlg.get_content_area().pack_start(self.vbox)

		if contourPlot:
			self.contourPlot=True
			self.cmbZ1.show()
			self.cmbX1.set_sensitive(False)
			self.cmbY1.set_sensitive(False)
#			self.cmbZ1.set_active(2)
		else:
			self.cmbZ1.hide()
			self.enZ1sf.hide()
			self.enZ1lab.hide()
			self.contourPlot=False
		
		self.onClear(None)
		self.cmbX1.set_active(0)
		self.cmbY1.set_active(1)

		if axisChoice==False:
			self.spnNumCols.set_sensitive(False)
			self.spnNumRows.set_sensitive(False)
			self.cmbPlotFig.set_sensitive(False)

#		if '(mm)' in self.cmbX1.get_active_text():
#			self.enX1sf.set_text('6.666667')

		self.enX1lab.set_text(self.cmbX1.get_active_text())
		self.enY1lab.set_text(self.cmbY1.get_active_text())
		self.enZ1lab.set_text('z-axis')

		self.x1SF=[]		
		self.y1SF=[]


	def onyNormChanged(self, widget):
		if widget.get_active():
			self.enY1sf.set_sensitive(False)
		else:
			self.enY1sf.set_sensitive(True)


	def onAxisChanged(self,widget):

		if self.contourPlot:
#			print 'contourPlot routine' # GET CONTOUR DATA ROUTINE:
			filename=self.cmbFile.get_active_text()
			print 'contour plot routine\nfile:' + filename
			dataArray=loadtxt(filename,comments='% ') # ,delimiter=',') # removed 13-07-11

			expFile = filename.split('-2Darray')[0]+'.exp'
			xdata,ydata,xlabel,ylabel=getXYdataForContourPlot(expFile)

			self.previewPlot.remove_line(widget)  # widget is a dummy variable here

			self.previewPlot.plotContour(self.previewPlot.axis,dataArray,xax=xdata,yax=ydata)
		else:
			m = self.cmbFile.get_active()
			x = self.cmbX1.get_active()
			y = self.cmbY1.get_active()

			self.previewPlot.remove_line(widget)  # widget is a dummy variable here
			ret=self.previewPlot.getData(self.filenameList[m],x,y)
			self.previewPlot.plotData(self.previewPlot.axis,self.previewPlot.xDataStore[-1],self.previewPlot.yDataStore[-1],lineprops=dict(color='b', linewidth=2,linestyle='-'))

			self.currYmax=max(self.previewPlot.yDataStore[-1])


#			onAutoScale(widget,self.previewPlot.axis,self.previewPlot.canvas)

			self.previewPlot.axLabel(self.previewPlot.axis,self.previewPlot.axLabels[-1][0],self.previewPlot.axLabels[-1][1])

		return



	def onNumChanged(self,widget):
		for x in range(10):
			try:
				self.cmbPlotFig.remove_text(0)
			except:
				pass

		for x in range(int(self.spnNumCols.get_value())):
			for y in range(int(self.spnNumRows.get_value())):
				self.cmbPlotFig.append_text(str(x+1)+', '+str(y+1))
		self.cmbPlotFig.set_active(0)


	def onAdd(self,widget):
		m=self.cmbFile.get_active()
		self.filenames.append(self.filenameList[m])
		self.plotFig.append(self.cmbPlotFig.get_active())
		self.x1.append(self.cmbX1.get_active())
		xsf=self.enX1sf.get_text()
		self.x1SF.append(float(xsf))

		self.y1.append(self.cmbY1.get_active())
		if self.chkNorm.get_active():
			ysf=1.0/self.currYmax
		else:
			ysf=self.enY1sf.get_text()
		self.y1SF.append(float(ysf))

		if self.chkZeroX1.get_active():
			self.x1zero.append(1)
		else:
			self.x1zero.append(0)

#		self.z1.append(self.cmbZ1.get_active())
		
		self.lblPlot.set_text('xCol='+str(self.x1)+'\nyCol='+str(self.y1)+'\nxZero='+str(self.x1zero)+'\nySF='+str(self.y1SF)+'\non fig. '+str(self.cmbPlotFig.get_active_text()))

		self.btnOk.set_sensitive(True)


	def onAddAll(self,widget):

		for m in range(len(self.filenameList)):
			print m, self.filenameList[m]
			self.plotFig.append(self.cmbPlotFig.get_active())	#	plot to figure number (...)
			self.filenames.append(self.filenameList[m])

			if self.chkNorm.get_active():
				ysf=1.0/self.currYmax
			else:
				ysf=self.enY1sf.get_text()
			self.y1SF.append(float(ysf))

			self.x1.append(self.cmbX1.get_active())
			xsf=self.enX1sf.get_text()
			self.x1SF.append(float(xsf))

			self.y1.append(self.cmbY1.get_active())
	#		self.z1.append(self.cmbZ1.get_active())

			if self.chkZeroX1.get_active():
				self.x1zero.append(1)
			else:
				self.x1zero.append(0)

#		self.lblPlot.set_text('xCol='+str(self.x1)+'\nyCol='+str(self.y1)+'\nxZero='+str(self.x1zero)+'\nySF='+str(round(self.y1SF,3))+'\non fig. '+str(self.cmbPlotFig.get_active_text()))
		self.lblPlot.set_text('xCol='+str(self.x1)+'\nyCol='+str(self.y1)+'\nxZero='+str(self.x1zero)+'\nySF='+str(self.y1SF)+'\non fig. '+str(self.cmbPlotFig.get_active_text()))

		self.btnOk.set_sensitive(True)



	def onClear(self,widget):
		self.filenames=[]
		self.plotFig=[]
		self.x1=[]
		self.y1=[]
		self.x1SF=[]		
		self.x1zero=[]
		self.y1SF=[]
		self.y1norm=[]
#		self.z1=[]
		self.lblPlot.set_text('x='+str(self.x1)+'\ny='+str(self.y1)) #+'\nz='+str(self.z1))
		self.btnOk.set_sensitive(False)


	def getShortFilename(self,newfile):
		shortfilename = string.split(newfile,'/')[-1].rstrip()
#		self.filename = newfile

		return shortfilename


	def getDirectory(self,filepath):
		dirList = string.split(filepath,'/')
		directory=''
		for m in range(1,len(dirList)-1):
			directory=directory+'/'+dirList[m]

		return directory


	def onFile(self,widget):
#		self.cmbFile.handler_block(self.onAxisChanged)
		self.cmbX1.handler_block(self.cmbX1con)
		self.cmbY1.handler_block(self.cmbY1con)

		m=self.cmbFile.get_active()
		oldfilename=self.filenameList[m]
		directory=self.getDirectory(oldfilename)

		newfile = fileDialog('open', file_name="", file_filter_name="Data files", file_filter="txt", currentDir=directory, title_string="Choose file")

		if newfile:
			delim, numCols, axLabels = getColumnDelim(newfile)   # get the column delimiter and info

	#		shortfilename = self.updateFilename(newfile)
			self.cmbFile.append_text(self.getShortFilename(newfile))
			self.filenameList.append(newfile)

			for x in range(10):
				try:
					self.cmbX1.remove_text(0)
					self.cmbY1.remove_text(0)
	#				self.cmbZ1.remove_text(0)
				except:
					pass

			for x in axLabels:
				self.cmbX1.append_text(x)
				self.cmbY1.append_text(x)
	#			self.cmbZ1.append_text(x)

			self.cmbX1.set_active(0)
			self.cmbY1.set_active(1)
			self.cmbX1.handler_unblock(self.cmbX1con)
			self.cmbY1.handler_unblock(self.cmbY1con)
			ans=self.cmbFile.get_model()
			self.cmbFile.set_active(len(ans)-1)
	#		self.cmbFile.handler_unblock(self.onAxisChanged)
			self.onAxisChanged(widget)

			if not self.contourPlot:
				onAutoScale(widget,self.previewPlot.axis,self.previewPlot.canvas)
		

	def run(self):
		"""This function will show the PlotDlg"""	
	
		#run the dialog and store the response		
		self.result = self.dlg.run()

#		if self.numCols > 2:
#			z1=self.cmbZ1.get_active()		

		#we are done with the dialog, destroy it
		self.dlg.destroy()

		#return the result and the data
		if self.result == gtk.RESPONSE_ACCEPT:
			return 1
		else:
			return 0




################################################################################
######## Create the plot windows:  #######################################
######## 1. choose a file if none specified
######## 2. run PlotDialog to choose the parts of the file(s) to plot
######## 3. plot all the requested lines
######## 
class CreatePlotWindow:
	"""Creates a plot window using """
	def __init__(self,filenameList=[],figureNumber=1):
		self.plotList=[]
		self.plotInfo=[]
		self.lineColour=['b','r','g','y','m','b','r','g','y','m']

		widget=gtk.Label()
		self.createPlots(widget,filenameList,figureNumber)


	def createPlots(self,widget,filenameList,figureNumber):

		# choose a file if none specified in input
		if filenameList==[]:
			filename = fileDialog('open', file_name="", file_filter_name="Data files", file_filter="txt", currentDir='./', title_string="Choose file")
			filenameList.append(filename)

		if not filenameList==['']:
			delim, numCols, axLabels = getColumnDelim(filenameList[0])   # get the column delimiter and info
			if numCols>5:
				print 'large number of columns - plot contour?'
				plotDlg=PlotDialog(None,axLabels,filenameList,contourPlot=True)
				result = plotDlg.run()
			else:
				plotDlg=PlotDialog(None,axLabels,filenameList,contourPlot=False)
				result = plotDlg.run()
		
			if result:
				if plotDlg.contourPlot:
					filenames=plotDlg.filenames
					xIndex=plotDlg.x1
					yIndex=plotDlg.y1
					plotId=plotDlg.plotFig

					numCols = int(plotDlg.spnNumCols.get_value())
					numRows = int(plotDlg.spnNumRows.get_value())

					if plotDlg.enX1sf.get_text()=='':
						print 'CreatePlotWindow::CreatePlots::WARNING:: enX1sf is empty'
						xAxSF=1.0
					else:
						xAxSF=float(plotDlg.enX1sf.get_text())

					if plotDlg.enY1sf.get_text()=='':
						print 'CreatePlotWindow::CreatePlots::WARNING:: enY1sf is empty'
						yAxSF=1.0
					else:
						yAxSF=float(plotDlg.enY1sf.get_text())

					xAxLabel = plotDlg.enX1lab.get_text()
					yAxLabel = plotDlg.enY1lab.get_text()

					self.win = NewWindow()
					self.vbox = gtk.VBox(homogeneous=False, spacing=0)
					self.win.vbox.pack_start(self.vbox)
			#		self.createToolbar(self.vbox)

					# create the subplots by looping over all rows & columns
					widget=gtk.Button() # dummy widget


					n=0
					for x in range(numRows):
						self.hbox = gtk.HBox(homogeneous=False, spacing=0)			
						for y in range(numCols):
							self.plotList.append(PlotWidget2(self.win.win,numSubplots=[1,1],makeTB=True,showRect=False))
							if numRows>1:
								self.plotList[n].vbox.set_size_request(500,300)
							self.hbox.pack_start(self.plotList[n].vbox)
							n=n+1
						self.vbox.pack_start(self.hbox)

					# loop over all plots
					for m in range(len(filenames)):
						dataArray=loadtxt(filenames[m],comments='%') #,delimiter=',') ## removed 13-07-11
						expFile = filenames[m].split('-2Darray')[0]+'.exp'
						xdata, ydata, xlabel, ylabel = getXYdataForContourPlot(expFile)

						self.plotList[plotId[m]].plotContour(self.plotList[plotId[m]].axis,dataArray,xax=xdata,yax=ydata)

					self.win.win.set_title('Figure '+str(figureNumber))
					self.win.win.show_all()

				else:
					filenames=plotDlg.filenames
					xIndex=plotDlg.x1
					yIndex=plotDlg.y1
					plotId=plotDlg.plotFig

					numCols = int(plotDlg.spnNumCols.get_value())
					numRows = int(plotDlg.spnNumRows.get_value())

					currtxt = str(plotDlg.enX1sf.get_text())

#					if currtxt=='':
#					if plotDlg.enX1sf.get_text()=='':
#						print 'CreatePlotWindow::CreatePlots::WARNING:: enX1sf is empty'
#						xAxSF=1.0
#					else:
#					xAxSF=float(plotDlg.enX1sf.get_text())

#					if plotDlg.enY1sf.get_text()=='':
#						print 'CreatePlotWindow::CreatePlots::WARNING:: enY1sf is empty'
#						yAxSF=1.0
#					else:
#					yAxSF=float(plotDlg.enY1sf.get_text())


	#				xAxSF = float()
	#				yAxSF = float(plotDlg.enY1sf.get_text())
					xAxLabel = plotDlg.enX1lab.get_text()
					yAxLabel = plotDlg.enY1lab.get_text()

					if ('position' in axLabels[0]) or ('delay' in axLabels[0]) or 'time' in axLabels[0]:
						rectVisible=True
					else:
						rectVisible=False
#					print '\n\n*** xlabel=',xAxLabel,', rectangle visible = ', rectVisible

					self.win = NewWindow()
					self.vbox = gtk.VBox(homogeneous=False, spacing=0)
					self.win.vbox.pack_start(self.vbox)
			#		self.createToolbar(self.vbox)

					# create the subplots by looping over all rows & columns
					widget=gtk.Button() # dummy widget


					n=0
					for x in range(numRows):
						self.hbox = gtk.HBox(homogeneous=False, spacing=0)			
						for y in range(numCols):
							self.plotList.append(PlotWidget2(self.win.win,numSubplots=[1,1],makeTB=True,showRect=rectVisible))
							if numRows>1:
								self.plotList[n].vbox.set_size_request(500,300)
							self.hbox.pack_start(self.plotList[n].vbox)
							n=n+1
						self.vbox.pack_start(self.hbox)

					lines=[]
					self.lined = dict()

					# loop over all curves to plot
					for m in range(len(filenames)):
						print m, filenames[m]
						ret=self.plotList[plotId[m]].getData(filenames[m],xIndex[m],yIndex[m])   # get data

						xdat = array(self.plotList[plotId[m]].xDataStore[-1])
						xdat = xdat*plotDlg.x1SF[m]	# do scaling first so that zeroing routine works

						ydat = array(self.plotList[plotId[m]].yDataStore[-1])
						maxVal=max(ydat)
						maxPos=find(ydat==maxVal)[0]

						#### zero the x axis
						if plotDlg.x1zero[m]==1:
							xoff = xdat[maxPos]
						else:
							xoff = 0.0
						xdat = (xdat - xoff)         # set zero of x axis according to peak position of y data

						if plotDlg.chkNorm.get_active():
#							ydat = (ydat-ydat[-1])
							ydat = ydat/max(ydat)
						else:
							print plotDlg.y1SF[m]
							ydat = ydat * plotDlg.y1SF[m]


						line=self.plotList[plotId[m]].plotData(self.plotList[plotId[m]].axis,xdat,ydat,xlabel=self.plotList[plotId[m]].axLabels[0][0],ylabel=self.plotList[plotId[m]].axLabels[0][1],lineprops=dict(color=self.lineColour[0], linewidth=2,linestyle='-'))
						lines.append(line)
						iter_list_items(self.lineColour)
						self.plotList[plotId[m]].axLabel(self.plotList[plotId[m]].axis,self.plotList[plotId[m]].axLabels[-1][0],self.plotList[plotId[m]].axLabels[-1][1])
	#					self.plotList[plotId[m]].axLabel(self.plotList[plotId[m]].axis,xAxLabel,yAxLabel)

						self.plotInfo.append([filenames[m],self.plotList[plotId[m]].axLabels[0][0],self.plotList[plotId[m]].axLabels[0][1],xIndex[m],yIndex[m],len(self.plotList[plotId[m]].xDataStore[-1])])

						lab=filenames[m].split('/')[-1]
						self.plotList[plotId[m]].lineStore[m].set_label(lab)

#						self.plotList[plotId[m]].axis.r1._visible = False


					leg = self.plotList[plotId[m]].axis.legend(loc=self.plotList[plotId[m]].currentLegPos, fancybox=True, shadow=True)
					leg.get_frame().set_alpha(self.plotList[plotId[m]].currentLegTrans)


					for legline, origline in zip(leg.get_lines(), lines):
						legline.set_picker(5)  # 5 pts tolerance
						self.lined[legline] = origline

					for m in range(n):
						onAutoScale(widget,self.plotList[m].axis,self.plotList[m].canvas)
						currLim=getAxisLimits(self.plotList[m].axis)
						resizeRect(self.plotList[m].axis.r1,currLim,self.plotList[m].canvas)
						self.plotList[m].canvas.mpl_connect('pick_event', self.onpick)

					self.win.win.set_title('Figure '+str(figureNumber))
					self.win.win.show_all()





	def onpick(self, event):
		# on the pick event, find the orig line corresponding to the
		# legend proxy line, and toggle the visibilit
		legline = event.artist
		origline = self.lined[legline]
		vis = not origline.get_visible()
		origline.set_visible(vis)
		# Change the alpha on the line in the legend so we can see what lines
		# have been toggled
		if vis:
			legline.set_alpha(1.0)
			self.plotList[0].canvas.draw()
		else:
			legline.set_alpha(0.2)
			self.plotList[0].canvas.draw()


	def plotToExistingAxis(self,widget,filenameList,plotId):
		plotInfo = []

		# choose a file if none specified in input
		if filenameList==[]:
			filename = fileDialog('open', file_name="", file_filter_name="Data files", file_filter="txt", currentDir='./', title_string="Choose file")
			filenameList.append(filename)

		if filenameList:
			delim, numCols, axLabels = getColumnDelim(filenameList[0])   # get the column delimiter and info

			plotDlg=PlotDialog(None,axLabels,filenameList,axisChoice=False)
			result = plotDlg.run()
		
			if result:
				filenames=plotDlg.filenames
				xIndex=plotDlg.x1
				yIndex=plotDlg.y1

				# loop over all curves to plot
				for m in range(len(filenames)):
					ret=plotId.getData(filenames[m],xIndex[m],yIndex[m])
					plotId.plotData(plotId.axis,plotId.xDataStore[-1],plotId.yDataStore[-1],xlabel=plotId.axLabels[0][0],ylabel=plotId.axLabels[0][1],lineprops=dict(color=self.lineColour[0], linewidth=2,linestyle='-'))
					iter_list_items(self.lineColour)
#					plotId.axLabel(plotId.axis,plotId.axLabels[-1][0],plotId.axLabels[-1][1])

					plotInfo=[filenames[m],plotId.axLabels[0][0],plotId.axLabels[0][1],xIndex[m],yIndex[m],len(plotId.xDataStore[-1])]

				onAutoScale(widget,plotId.axis,plotId.canvas)

		return plotInfo


################################################################################
###### GENERIC AUTOSCALE ROUTINE FOR PLOT WIDGETS
def onAutoScale(widget,axis,canvas):

	l=axis.get_lines()
#	if len(l)>=3:
#		lines=l[2:]
#	else:
	lines=l

	xdata=getp(lines[0],'xdata')
	ydata=getp(lines[0],'ydata')
	globalxMin=min(xdata)
	globalxMax=max(xdata)
	globalyMin=min(ydata)
	globalyMax=max(ydata)

	# do the autoscaling
	for m in range(len(lines)):
		xdata=getp(lines[m],'xdata')
		ydata=getp(lines[m],'ydata')
		if min(xdata)<globalxMin:
			globalxMin=min(xdata)
		if max(xdata)>globalxMax:
			globalxMax=max(xdata)
		if min(ydata)<globalyMin:
			globalyMin=min(ydata)
		if max(ydata)>globalyMax:
			globalyMax=max(ydata)

	print globalxMin, globalxMax

	axis.set_xlim((globalxMin,globalxMax))
	if globalyMin<0:
		if globalyMax>0:
			axis.set_ylim((1.1*globalyMin,1.1*globalyMax))
		else:
			axis.set_ylim((1.1*globalyMin,0.9*globalyMax))			
	else:
		axis.set_ylim((0.9*globalyMin,1.1*globalyMax))

	# set the ticks
	currXlim=axis.get_xlim()
	dx=abs(currXlim[1]-currXlim[0])
	currYlim=axis.get_ylim()
	dy=abs(currYlim[1]-currYlim[0])

#	log10(currYlim[1])

#	axis.xaxis.set_major_formatter(FormatStrFormatter('%g'))
	xspacing=10**(int(round(log10(dx))))
	axis.xaxis.set_major_locator(MultipleLocator(0.2*xspacing))
	axis.xaxis.set_minor_locator(MultipleLocator(0.1*xspacing))

#	axis.yaxis.set_major_formatter(FormatStrFormatter('%g'))
	yspacing=10**(int(round(log10(dy))))
	if yspacing<=10:
		print dy, yspacing
		axis.yaxis.set_major_locator(MultipleLocator(0.1*yspacing))
		axis.yaxis.set_minor_locator(MultipleLocator(0.05*yspacing))
	else:
		axis.yaxis.set_major_locator(MultipleLocator(0.5*yspacing))
		axis.yaxis.set_minor_locator(MultipleLocator(0.05*yspacing))

	axis.xaxis.grid(True,'minor')
	axis.yaxis.grid(True,'minor')
	axis.xaxis.grid(True,'major',linewidth=1,linestyle='--')
	axis.yaxis.grid(True,'major',linewidth=1,linestyle='--')

	print 'autoscaled'
	canvas.draw()



###### GENERIC ZOOM-IN ROUTINE FOR PLOT WIDGETS
def zoomIn(widget,axis,canvas):
	currXlim=axis.get_xlim()
	dx=abs(currXlim[1]-currXlim[0])
	x0=(currXlim[0]+currXlim[1])/2
	currYlim=axis.get_ylim()
	dy=abs(currYlim[1]-currYlim[0])
	y0=(currYlim[0]+currYlim[1])/2
	
	axis.set_xlim((x0-0.9*dx/2.0,x0+0.9*dx/2.0))
	axis.set_ylim((y0-0.9*dy/2.0,y0+0.9*dy/2.0))
	canvas.draw()


###### GENERIC ZOOM-IN ROUTINE FOR PLOT WIDGETS
def zoomOut(widget,axis,canvas):
	currXlim=axis.get_xlim()
	dx=abs(currXlim[1]-currXlim[0])
	x0=(currXlim[0]+currXlim[1])/2
	currYlim=axis.get_ylim()
	dy=abs(currYlim[1]-currYlim[0])
	y0=(currYlim[0]+currYlim[1])/2
	
	axis.set_xlim((x0-1.1*dx/2.0,x0+1.1*dx/2.0))
	axis.set_ylim((y0-1.1*dy/2.0,y0+1.1*dy/2.0))
	canvas.draw()


###### GENERIC FIND POINT ROUTINE FOR PLOT WIDGETS (CLICK NEAR POINT, MAKES MARKER AND SHOWS VALUE)
def findPoint(clickX,clickY,axis,n):
	lines=axis.get_lines()
	xdata=getp(lines[n],'xdata')
	ydata=getp(lines[n],'ydata')

	for m in range(len(xdata)-1):
		if xdata[m]>clickX:
			x0=(xdata[m]+xdata[m+1])/2
			y0=(ydata[m]+ydata[m+1])/2
			break
		else:

			x0=xdata[m+1]
			y0=ydata[m+1]

	return x0,y0



###### GENERIC ADD RECTANGLE ROUTINE FOR PLOT WIDGETS
def plotRect(axis,canvas,xy=(0.0,0.0),width=1.0,height=1.0,alpha=0.2,edgecolor=None,facecolor='g',showRect=False):
	r1=matplotlib.patches.Rectangle(xy,width,height,alpha=alpha,edgecolor=edgecolor,facecolor=facecolor)
	axis.add_artist(r1)

	r1._visible=showRect

	canvas.draw()

	return r1

###### GENERIC RESIZE RECTANGLE ROUTINE FOR PLOT WIDGETS
def resizeRect(rect,newSize,canvas):
	rect._x = newSize[0]
	rect._y = newSize[1]
	rect._width = newSize[2]
	rect._height = newSize[3]
	canvas.draw()


def getAxisLimits(axis):
	currXlim=axis.get_xlim()
	dx=abs(currXlim[1]-currXlim[0])
	x0=currXlim[0]
	currYlim=axis.get_ylim()
	dy=abs(currYlim[1]-currYlim[0])
	y0=currYlim[0]

	return [x0, y0, dx, dy]




### set the y axis to logarithmic if the toggle is active
def OnLogY(widget, axis, canvas):
	currXlim=axis.get_xlim()

	if widget.get_active():
		#setp(self.axis,'yscale','log')
		axis.set_yscale('log')

	else:
		setp(axis,'yscale','linear')
#			try:
#				setp(self.axis,'ylim',[1.1*self.newPage[currPage].yArray.min(), 1.1*self.newPage[currPage].yArray.max()])
#			except AttributeError:
#				print 'PlotWidget::OnLogY::WARNING:: No data in figure.'

	axis.set_xlim(currXlim)	
	canvas.draw()




if __name__ == "__main__":

	######  the whole shebang, including the data chooser dialog
	if 0:
		w=CreatePlotWindow(filenameList=['LAO-L3-293K.txt'])


	###### this example:
	#          - creates one plot window which EXITS when destroyed (mainProg=True)
	#          - uses the necessary individual functions to load and plot the data
	#   NOTE: the green box size (and therefore the data window) can be choosen using the "Left-click sets:" command box in the "Axis" area at the bottom/middle of each window. Current default for the FFT button is to do a time-windowed FFT of ALL lines
	if 1:
		p=PlotWidget2(title='Plot 1',mainProg=True,showRect=True,figHeight=300)	# create the plot window + widget

		# load the data from a file
		p.getData(filename='ref-293K.txt')	

		p.plotData(p.axis,p.xDataStore[-1],p.yDataStore[-1],xlabel=p.axLabels[0][0],ylabel=p.axLabels[0][1])
		p.axLabel(p.axis,p.axLabels[-1][0],p.axLabels[-1][1])

		# this part is needed to resize the green bounding box (for the windowed FFT) after the data has been plotted
		currLim=getAxisLimits(p.axis)		
		resizeRect(p.axis.r1,currLim,p.canvas)


	###### this example:
	#         - creates a plot window
	#         - loads two data sets
	#         - plots them all in one go
	#   NOTE: the green box size (and therefore the data window) can be choosen using the "Left-click sets:" command box in the "Axis" area at the bottom/middle of each window. Current default for the FFT button is to do a time-windowed FFT of ALL lines
	if 1:
		p=PlotWidget2(title='Plot 2',mainProg=False,showRect=True)	# create the plot window + widget
		p.getData(filename='ref-293K.txt')	# load the data from a file
		p.getData(filename='LAO-L3-293K.txt')

		p.plotAll()


	gtk.main()
