import os
import string
import fileinput
import datetime
from numpy import shape, loadtxt, savetxt, linspace, logspace, zeros, array
from types import * 

#from prmClass import *
from generic import * 

################################################
currTime=datetime.datetime




def savedata(pathname,filename,info,dataArray,overwrite=0,logfile='control.log'):
	"""Output the data to a file"""
	currDir=os.getcwd()
#	pathname=pathname+'/data'
	os.chdir(pathname)

	if overwrite==0:
		# check to see if filename exists already
		newfilename=checkIfFileExists(filename)
	else:
		newfilename=filename
	
	os.chdir(currDir)
	logprint(logfile,'Saved data: ' + pathname + '/' + newfilename)
	os.chdir(pathname)

	# write data to new file
	try: 
		f=open(newfilename,'w')
	except IOError:
		print 'savedata::ERROR:: cannot open ' + newfilename + ' for writing'
		return 'ERROR'

	f.write(info)
	
	dimns=shape(dataArray)
	for i in range(dimns[1]):   # loop over rows of dataArray
		if dimns[0] == 2:   # save x, y
			lineStr = '%(x)7.6e\t%(y)7.6e\n' % {'x':dataArray[0,i], 'y':dataArray[1,i]}
		elif dimns[0] == 3: # x, y1, y2
			lineStr = '%(x)7.6e\t%(y1)7.6e\t%(y2)7.6e\n' % {'x':dataArray[0,i], 'y1':dataArray[1,i], 'y2':dataArray[2,i]}
		elif dimns[0] == 4:
			lineStr = '%(x)7.6e\t%(y1)7.6e\t%(y2)7.6e\t%(y3)7.6e\n' % {'x':dataArray[0,i], 'y1':dataArray[1,i], 'y2':dataArray[2,i], 'y3':dataArray[3,i]}
		elif dimns[0] == 5: # x, y1, y2, y3, y4
			lineStr = '%(x)7.6e\t%(y1)7.6e\t%(y2)7.6e\t%(y3)7.6e\t%(y4)7.6e\n' % {'x':dataArray[0,i], 'y1':dataArray[1,i], 'y2':dataArray[2,i], 'y3':dataArray[3,i], 'y4':dataArray[4,i]}
		else:
			lineStr = 'savedata:: Error - Invalid data'
			
		f.write(lineStr)

	f.close()
	os.chdir(currDir)

	return newfilename    # return the filename used

	
def loadData(filename,delim='\t',xIndex=0,yIndex=1,comments='% '):
	"""Load two columns of data from a file"""
#	print filename, xIndex, yIndex, comments
	try:
		data=loadtxt(filename,delimiter=delim,comments=comments,usecols=(xIndex,yIndex))

	except IndexError:
		f=open(filename,'r')
		m=0
		for line in f:
			m=m+1
			if 'Angle,Intensity' in line:
				break
		f.close()
		data=loadtxt(filename,delimiter=delim,comments=comments,usecols=(xIndex,yIndex),skiprows=m+1)

	except ValueError:	# probably could not convert string to float
		data=loadtxt(filename,comments=comments,usecols=(xIndex,yIndex))


	return data[:,0], data[:,1]


def checkIfFileExists(filename,path='.'):
	tryfilename=filename

	# check to see if filename exists already
	for i in range(10000):
		try:
			f = open(path+'/'+tryfilename, 'r')
			f.close()
		except IOError:   # if the file doesn't already exist:
			newfilename=tryfilename
			break
#			else:    # if the file already exists:
#				
#		pathDirs = tryfilename.split('./')[1].split('/')[0:-1]
#		path = './'
#		for x in pathDirs:
#			path = path + str(x) + '/'

#		fileparts=string.split(tryfilename.split('./')[1].split('/')[-1],'.')   # split the string to e.g. 'data_0' + 'txt'
#		fileparts2=string.split(fileparts[0],'_') # split the 'data_0' to 'data' + '0'
		fileparts=string.split(tryfilename,'.')   # split the string to e.g. 'data_0' + 'txt'
		fileparts2=string.split(fileparts[0],'_') # split the 'data_0' to 'data' + '0'
		
		if len(fileparts2)==1:   # if no '_N'
			tryfilename=fileparts[0]+'_0'+'.'+fileparts[1]
		else:
			tryfilename=fileparts2[0]+'_'+str(i)+'.'+fileparts[1]

		if i==1000:
			print 'checkIfFileExists():: You should probably delete some of the "'+filename+'" files!!'

	return newfilename


def saveDataArray(filename,dataArray,logfile='control.log',pathname='./data'):
	"""Save array of data to a file"""
#	print filename, xIndex, yIndex, comments
	currDir=os.getcwd()
	os.chdir(pathname)

	newfilename=checkIfFileExists(filename)
	savetxt(newfilename,dataArray)

	os.chdir(currDir)

	logprint(logfile,'Saved data: ' + pathname + '/' + newfilename)
	return newfilename


def loadDataArray(filename,delim='\t',comments='% '):
	"""Load array of data from a file"""
#	print filename, xIndex, yIndex, comments
	data=loadtxt(filename,comments=comments)
	return data


def loadDataOld(filename,delim,xIndex,yIndex):
	"""Load the data from a file - OLD CODE - PRE 23/06/2010"""
	xdata=[]
	ydata=[]
	xdata2=[]
	ydata2=[]
	#### get data:
	f=open(filename,"r")

	line1=f.readline()
	if line1[0] == '%':
		fileType='normal'
	elif line1[0] == '/':
		fileType='LIV'
	else:
		fileType='normal'

	f.close()

	f=open(filename,"r")

	if fileType=='normal':
		for line in f:
			if not line[0] == '%':
				tokens = string.split(line.lstrip(' ').rstrip(' \n'),delim)
#				print tokens, xIndex, yIndex
				try:
					xdata.append(float(tokens[xIndex]))
					ydata.append(float(tokens[yIndex]))
				except ValueError:
					print "fileIO.py::WARNING::loadData could not parse file correctly."
					print xIndex, yIndex, tokens
					f.close()
					return xdata, ydata
	elif fileType=='LIV':
		slashcount=0
		for line in f:
			if line[0] == '/':
				slashcount=slashcount+1

			else:
				tokens = string.split(string.strip(line,'\n'),delim)
				if slashcount==1:
					xdata.append(float(tokens[0]))
					ydata.append(float(tokens[1]))
				elif slashcount==3:
					xdata2.append(float(tokens[0]))
					ydata2.append(float(tokens[1]))

	f.close()


	####
	if fileType=='normal':
		return xdata, ydata
	elif fileType=='LIV':
		return [xdata, xdata2], [ydata, ydata2]


def getColumnDelim(filename=''):
	if not filename=='':
		numCols=0

		#### get axis labels from file:
		f=open(filename,"r")

		# check column names
		line1=f.readline()

		# get delimiter between the columns...
		line2=f.readline()
		f.close()
		line2=line2.lstrip(' ')
		
		if '<?xml' in line1:
			print '**** XML-format X-ray data file detected ****'
			return 'xml',2,['Angle','Intensity']
		else:
			delim, numCols = findDelim(line2)

			if line1[0] == '%':			
				axLabels = string.split(string.strip(line1,'%').strip(),', ')
			elif line1[0] == '/':			
				axLabels = ['Current','Voltage']
			else:
				axLabels = []
				for x in range(numCols):
					axLabels.append('Column '+str(x+1))
				print 'getColumnDelim::Error - file does not start with a % sign'
	else:
		delim=''
		numCols=0
		axLabels=[]
		
	return delim, numCols, axLabels



def timeDateStamp(currentTime):

	dateStamp='%(day)i/%(month)i/%(year)i, ' % {'day':currentTime.day,'month':currentTime.month,'year':currentTime.year}
	minute=currentTime.minute
	if minute < 10:
		minuteStr='0'+str(minute)
	else:
		minuteStr=str(minute)

	second=currentTime.second
	if second < 10:
		secondStr='0'+str(second)
	else:
		secondStr=str(second)
	timeStamp= '%(hour)i:%(minute)s:%(second)s. ' % {'hour':currentTime.hour,'minute':minuteStr,'second':secondStr}

	return timeStamp, dateStamp




def logprint(fileName,lineStr):
	"""Print lineStr to the log file"""
	f=open(fileName,'a')  # append mode

	currentTime=currTime.today()
	dateStamp, timeStamp = timeDateStamp(currentTime)

	writeStr = dateStamp+timeStamp+lineStr
	print writeStr
	f.write(writeStr+'\n')

	f.close()





def readFile(fileName):
	"""Return file contents as list"""
	dataList=[]
	f=open(fileName,'r')

	for line in f:
		dataList.append(line.rstrip())

	f.close()

	return dataList


def expLogUpdate(fileName,lineStr):
	"""Print lineStr to the log file"""
	nameList=[]
	f=open(fileName,'r')

	for line in f:
		nameList.append(line)

	f.close()

	nameList.insert(0,lineStr)
	nameList.pop()

	f=open(fileName,'w')
	for x in range(len(nameList)):
		f.write(nameList[x]+'\n')

	f.close()

	return nameList


def readData(filename):
	"""Return file contents as a list of lists"""
	dataList=[]

	f=open(filename,'r')

	# get delimiter between the columns...
	line=f.readline()			
	tokens = string.split(line,'\t')
	if len(tokens) > 1:  # if found a tab:
		delim='\t'
		numCols=len(tokens)

	tokens = string.split(line,',')
	if len(tokens) > 1:  # if found a comma:
		delim=','
		numCols=len(tokens)

	f.close()

	f=open(filename,'r')
	for line in f:
		tokens=string.split(line,delim)
		data=[]		
		for x in range(len(tokens)):
			data.append(tokens[x].rstrip())

		dataList.append(data)

	f.close()

	return dataList



def saveSetFile(filename,nameList,valueList):
	"""Print list to filename"""

	if len(nameList)==len(valueList):
		f=open(filename,'w')
		for x in range(len(nameList)):
			f.write(str(nameList[x])+'\t'+str(valueList[x])+'\n')

		f.close()
	else:
		print 'fileIO.py:: saveSetFile:: length of nameList and valueList not equal'


def saveBuffer(filename,textbuffer):
	"""Save a text buffer to a file"""
	f = open(filename, "w")
	f.write(textbuffer.get_text(textbuffer.get_start_iter(), textbuffer.get_end_iter(), include_hidden_chars=True))
	f.close()



#### PARAMETER FILE ROUTINES:
def saveParam(prm,filename):
	"""Save the parameters to a file."""
	f=open(filename,'w')

	# GET PARAMETERS:
	scanDescription=prm.scanDescription
	dataFile = prm.dataFile
	vary = prm.vary
	vary2 = prm.vary2
	plotType = prm.plotType

	# WRITE PARAMETERS TO FILE:
	f.write('#\n# scan information:\n# ')
	f.write("\nprm.scanDescription = '"+scanDescription+"'\n")

	f.write('\n# scan options')
	f.write("\nprm.dataFile = '"+dataFile+"'")

	f.write('\n\n#\n# scan parameters:\n#')
	f.write("\nprm.vary       = '" + vary +"'")
	f.write('\nprm.startPos   = ' + str(prm.startPos))
	f.write('\nprm.stopPos    = ' + str(prm.stopPos))
	f.write('\nprm.numPoints  = ' + str(prm.numPoints))
	f.write('\nprm.scans      = ' + str(prm.scans))
	f.write('\nprm.settleTime = ' + str(prm.settleTime))
	
	f.write('\nprm.stageList[prm.stageIndex(prm.vary)].zeroPos = ' + str(prm.stageList[prm.stageIndex(vary)].zeroPos))
	f.write("\nprm.sweepMode = '" + str(prm.sweepMode)+"'")

	f.write('\n\n#\n# experiment setup (other stages, instruments etc.):\n#')
	f.write("\nprm.varType2   = '"+vary2+"'")
	f.write("\nprm.var2       = '"+str(prm.var2)+"'")

	try:
		f.write("\nprm.alsoSetVariable = '" + str(prm.alsoSetVariable)+"'")
		f.write("\nprm.alsoSetValue = " + str(prm.alsoSetValue))
	except:
		pass

	try:
		f.write("\nprm.settingsFile = '" + str(prm.settingsFile)+"'")
	except:
		pass

	f.write("\n\nprm.measure1   = '" + prm.measure1+"'")
	f.write("\nprm.measure2   = '" + prm.measure2+"'")
	f.write("\nprm.measure3   = '" + prm.measure3+"'")
	f.write("\nprm.measure4   = '" + prm.measure4+"'")

	f.write("\n\n# program options")
	f.write("\nprm.calibrateNDwheel = "+str(prm.calibrateNDwheel))
	f.write("\nprm.findPeak = "+str(prm.findPeak))
	f.write("\nprm.findDeltaPeaks = "+str(prm.findDeltaPeaks))
	f.write("\nprm.findPeakGrad = "+str(prm.findPeakGrad))
	f.write("\nprm.findBeamWidth = "+str(prm.findBeamWidth))
	f.write("\nprm.plotType = '"+plotType+"'")

	f.close()


def getParam(filename):
	# create prm class
	prm=SystemPRM()

	# load parameters from .exp file into prm class
	f=open(filename,'r')
	exec(f)
	f.close()

	return prm



def saveClass(className,filename):

	f= open(filename,'w')

	for key in dir(className):
		if not key.startswith('__'):
			value = getattr(className,key)
			if not callable(value):
				if not 'instance' in str(value):
					if type(value)==type(''):
						f.write(key + " = '" + str(value) + "'\n")
					else:
						if value==None:
							f.write(key + " = 'None'\n")
						else:
							f.write(key + " = " + str(value) + "\n")
	f.close()

#	print 'saveClass::saved class to: '+str(filename)

	return


def saveClassOld(className,filename):

	f= open(filename,'w')

	for key in dir(className):
		if not key.startswith('__'):
			value = getattr(className,key)
			if not callable(value):
				if not 'instance' in str(value):
					if type(value)==StringType:
						f.write(key + " = '" + str(value) + "'\n")
					else:
						f.write(key + " = " + str(value) + "\n")

	f.close()

#	print 'saveClass::saved class to: '+str(filename)

	return


# routine to load in a class from a file
def loadClass(filename):
	newClass = dummyClass()

	f= open(filename,'r')

	n=1
	for line in f:
		n=n+1
		if len(line) > 2:
			if not line[0] =='#':
				key = line.split(' = ')[0].rstrip()
				try:
					value = line.split(' = ')[1].rstrip().lstrip("' ").rstrip("' ")
				except IndexError:
					r='fileIO.py::loadClass'
					m='IndexError parsing line ' +str(n)+ ' of file/class ' +str(filename) + ', which reads: ' + line
					e=errorClass(message=m,callingRoutine=r)
					return e

				if '[' in value:
					newList=value.lstrip("[' ").rstrip("]' ").split(',')
					for x in range(len(newList)):
						newList[x]=newList[x].lstrip("' ").rstrip("' ")
					setattr(newClass,key,newList)
				elif ('{' in value) and not ('$' in value):	# not ('$' in value) added for LaTeX string support
#				elif '{' in value:
					newDict={}

					newList=value.lstrip("{' ").rstrip("}' ").split(',')
					if not newList==['']:
						for x in range(len(newList)):
							dictkey   = newList[x].split(':')[0].lstrip("' ").rstrip("' ")
							dictvalue = newList[x].split(':')[1].lstrip("' ").rstrip("' ")
							newDict.update({dictkey:dictvalue})
				
					setattr(newClass,key,newDict)
				else:
					setattr(newClass,key,value)
#		else:
#			print 'WARNING fileIO.py::loadClass:: '
	f.close()

#	print 'loadClass::done'

	return newClass



def appendClass(filename, oldClass):
	newClass = oldClass

	f= open(filename,'r')

	for line in f:
		key = line.split(' = ')[0].rstrip()
		try:
			value = line.split(' = ')[1].rstrip().lstrip("' ").rstrip("' ")
		except IndexError:
			print line

		if '[' in value:
			newList=value.lstrip("[' ").rstrip("]' ").split(',')
			for x in range(len(newList)):
				newList[x]=newList[x].lstrip("' ").rstrip("' ")
			setattr(newClass,key,newList)
		elif '{' in value:
			newDict={}

			newList=value.lstrip("{' ").rstrip("}' ").split(',')
			for x in range(len(newList)):
				dictkey   = newList[x].split(':')[0].lstrip("' ").rstrip("' ")
				try:
					dictvalue = newList[x].split(':')[1].lstrip("' ").rstrip("' ")
				except IndexError:
					print 'could not parse ' + line + '/ dictkey = ' + str(dictkey)
				newDict.update({dictkey:dictvalue})
				
			setattr(newClass,key,newDict)
		else:
			setattr(newClass,key,value)

	f.close()

#	print 'loadClass::done'

	return newClass




######## useful fileIO routines for contour plots:
def getXYdataForContourPlot(expFile):
	xdata=None
	ydata=None
	xlabel=''
	ylabel=''

#	print '.exp:' + expFile
	try:
		p = loadClass(expFile)
	except IOError:
		print 'fileIO.getXYdataForContourPlot():: warning:: "' + expFile + '" not found.'
		return xdata, ydata, xlabel, ylabel

	if p.vary_spacing[0]=='linear':
		xdata=linspace(float(p.vary_startPos[0]),float(p.vary_stopPos[0]),int(p.vary_numPoints[0]))
	elif p.vary_spacing[0]=='log':
		xdata=logspace(float(p.vary_startPos[0]),float(p.vary_stopPos[0]),int(p.vary_numPoints[0]))
	else:
		print 'plotWidget.getXYdataForContourPlot():: WARNING:: unknown spacing type "'+str(p.vary_spacing[0])+'"'

	if p.vary_spacing[1]=='linear':
		ydata=linspace(float(p.vary_startPos[1]),float(p.vary_stopPos[1]),int(p.vary_numPoints[1]))
	elif p.vary_spacing[1]=='log':
		ydata=logspace(float(p.vary_startPos[1]),float(p.vary_stopPos[1]),int(p.vary_numPoints[1]))
	else:
		print 'plotWidget.getXYdataForContourPlot():: WARNING:: unknown spacing type "'+str(p.vary_spacing[1])+'"'

	xlabel = p.vary_property[0]
	ylabel = p.vary_property[1]


	return xdata, ydata, xlabel, ylabel




##### general routine to grab properties from axis instance and save as class to filename
def axisPropToFile(figfilename,axis,datafile='test.txt',prm=None):
#	d=loadClass(filename)	#	load in old file class
	if prm==None:	# if no existing parameter class then make one from defaults
		d=PlotInfo()
	else:
		d=prm
#		print 'using params:'
#		printClass(prm)
#	d=dummyClass()

	# overwrite parameters
	d.filename=datafile

	d.title=axis.get_title()
	d.xlabel=axis.get_xlabel()
	d.ylabel=axis.get_ylabel()
	d.xscale=axis.get_xscale()
	d.yscale=axis.get_yscale()
	d.xmin  =axis.get_xlim()[0]
	d.xmax  =axis.get_xlim()[1]
	d.ymin  =axis.get_ylim()[0]
	d.ymax  =axis.get_ylim()[1]

	h = axis.get_lines()
#	if len(h)>2:
#		if h[-2].get_visible():
#			d.drawx = 1
#		else:
#			d.drawx = 0
#		if h[-1].get_visible():
#			d.drawy = 1
#		else:
#			d.drawy = 0
#	else:
#		d.drawx=0
#		d.drawy=0

	d.lineColours=[]
	d.lineStyles=[]
	d.lineWidths=[]
	d.markers=[]
	for line in h:
		if len(line.get_xdata())>2:
			d.lineColours.append(line.get_color())
			d.lineStyles.append(line.get_linestyle())
			d.lineWidths.append(line.get_linewidth())
			marker=line.get_marker()
			if (marker=='None') or (marker==None):
				d.markers.append('')
			else:
				d.markers.append(marker)
		else:
			pass
#			print 'ignoring line [probably x=0 or y=0 line]'

#	print 'saved ',str(len(h)),' lines.'

	# get legend
	l=axis.get_legend()

	if not l==None:
		d.legendAlpha=l.get_frame().get_alpha()
	
		if l.shadow:
			d.legendShadow=1
		else:
			d.legendShadow=0

		if l.get_frame().get_visible():
			d.legendFrame=1
		else:
			d.legendFrame=0


		legPositions=['no legend','upper right','upper left','lower left','lower right','right','centre left','centre right','lower centre','upper centre','centre']
		d.legendLoc  =legPositions[l._loc]

		handles, legLabels = axis.get_legend_handles_labels()
		d.legendLabels=legLabels
	else:
		d.legendAlpha=0.0
		d.legendLoc='no legend'
		d.legendLabels=['']
		d.legendShadow=0

#	d.gridLinewidth
#	printClass(d)
	
	saveClass(d,figfilename)




def getXMLdata(filename,offset=True):
	xdata=[]
	ydata=[]
	outputLine=False
	output=[]

	f=open(filename)
	for line in f:
		if outputLine:
			output.append(line)

		if '<positions axis="2Theta"' in line:
			outputLine=True
		elif '<startPosition>' in line:
			outputLine=True
		elif '<positions axis="Omega"' in line:
			outputLine=True
		elif '<intensities' in line:
			data=line
			outputLine=False
		else:
			outputLine=False

	f.close()


	if len(output)==4:
		ydataStr=data.lstrip('\t').lstrip('<intensities unit="counts">').rstrip('</intensities>\r\n').split(' ')
		for m in range(len(ydataStr)):
			ydata.append(float(ydataStr[m]))
	else:
		return [],[]

	twothetaMin=float(output[0].lstrip('\t\t\t\t\t<startPosition>').rstrip('</startPosition>\r\n'))
	twothetaMax=float(output[1].lstrip('\t\t\t\t\t<endPosition>').rstrip('</endPosition>\r\n'))

	if offset:
		omegaMin=float(output[2].lstrip('\t\t\t\t\t<startPosition>').rstrip('</startPosition>\r\n'))
		omegaMax=float(output[3].lstrip('\t\t\t\t\t<endPosition>').rstrip('</endPosition>\r\n'))
		offset=twothetaMin/2.0 - omegaMin
#		print 'omega offset=',offset,'deg'


	xdata=linspace(twothetaMin,twothetaMax,len(ydata))



	return xdata, ydata



def getRSMdata(filename,scanningMode=False):
	numScans=0
	numPoints=0


	f=open(filename)
	for line in f:

		if 'No. of scans, ' in line:
			print line
			numScans=int(line.split('No. of scans, ')[1])
		elif 'No. of points per scan, ' in line:
			numPoints=int(line.split('No. of points per scan, ')[1])
	f.close()

	if (numScans==0) and (numPoints==0):
		print 'WARNING: fileIO.getRSMdata() found no data, trying alternative method'

		#<sampleOffset>
		twoThetaPos=[]
		omegaPos=[]

		f=open(filename)
		#for line in f:
		#	if '<scan appendNumber="0" mode="Continuous" scanAxis="2Theta-Omega" status="Completed">' in line:
		
		for line in f:
			if '</measurementStepAxisCenter>' in line:
				break		# scan forwards through file to the start of the interesting bit

		##### get number of scans
		for line in f:
			if '<position axis="2Theta"' in line:
				val=float(line.lstrip('\t\t\t<position axis="2Theta" unit="deg">').split('</pos')[0])
				twoThetaPos.append(val)
			if '<position axis="Omega" unit="deg">' in line:
				val=float(line.lstrip('\t\t\t<position axis="Omega" unit="deg">').split('</pos')[0])
				omegaPos.append(val)
		f.close()
		
		numScans=len(omegaPos)

		##### get number of points in each scan
		f=open(filename)
		for line in f:
			if '<intensities unit="counts">' in line:
				num=line.lstrip().lstrip('<intensities unit="counts">').split('</inten')[0].split(' ')
				numPoints=len(num)
				break
		f.close()
		
		print numScans, numPoints

		f=open(filename)	
		for line in f:
			if '</measurementStepAxisCenter>' in line:
				break		# scan forwards through file to the start of the interesting bit

		scanOmegaMin=[]
		scanOmegaMax=[]
		scanTwoThetaMin=[]
		scanTwoThetaMax=[]
		scanIntensity  =zeros((numScans,numPoints))

		m=-1	# m counts the scan number
		for line in f:
			if '<scan appendNumber="0" mode="Continuous"' in line:
				m=m+1
			if '<positions axis="2Theta" unit="deg">' in line:
				output2Theta=True
				outputOmega =False
			if '<positions axis="Omega" unit="deg">' in line:
				output2Theta=False
				outputOmega =True

			if '<startPosition>' in line:
				if output2Theta:
					scanTwoThetaMin.append(float(line.lstrip().lstrip('<startPosition>').split('</start')[0]))
				elif outputOmega:
					scanOmegaMin.append(float(line.lstrip().lstrip('<startPosition>').split('</start')[0]))
			if '<endPosition>' in line:
				if output2Theta:
					scanTwoThetaMax.append(float(line.lstrip().lstrip('<endPosition>').split('</end')[0]))
				elif outputOmega:
					scanOmegaMax.append(float(line.lstrip().lstrip('<endPosition>').split('</end')[0]))
			if '<intensities unit="counts">' in line:
				intList=line.lstrip().lstrip('<intensities unit="counts">').split('</intensit')[0]
				intensity=intList.split(' ')
				for p in range(numPoints):
					scanIntensity[m,p]=float(intensity[p])
		
		f.close()

		data=zeros((numScans,numPoints,3))
#		data=scanIntensity

		for m in range(numScans):
			omega    = linspace(scanOmegaMin[m],scanOmegaMax[m],numPoints)
			twoTheta = linspace(scanTwoThetaMin[m],scanTwoThetaMax[m],numPoints)
			for n in range(numPoints):
				data[m,n,0]=twoTheta[n]	# twotheta val
				data[m,n,1]=omega[n]	# omega val
				data[m,n,2]=scanIntensity[m,n]


	else:

		data=zeros((numScans,numPoints,3))
	#	print shape(data)
		f=open(filename)
		for m in range(40):
			if '2Theta position, Omega position, Intensity' in f.readline():
				break

		for m in range(numScans):
			for n in range(numPoints):
				line=f.readline()
				data[m,n,0]=float(line.split(',')[0])
				data[m,n,1]=float(line.split(',')[1])
				data[m,n,2]=float(line.split(',')[2])

		f.close()
	

	return data, numScans, numPoints
