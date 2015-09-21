from numpy import exp
import string


##### GENERIC HELPER FUNCTIONS:
class dummyClass():
	def __init__(self):
		pass


class errorClass():
	def __init__(self,message='Error raised',callingRoutine='unknown',showError=True):
		self.message=message
		self.callingRoutine=callingRoutine

		if showError:
			print 'ERROR::',callingRoutine,'::',message


def add_to_dict(dictionary, key, value):
	dictionary.setdefault(key,[]).append(value)
#	dictionary.update(key=value)


def print_dict(dictionary):
	for x, y in dictionary.iteritems():
		print x, y


def iter_list_items(list_name):
	"""Iterates the items in a list."""
	list_item=list_name.pop(0)
	list_name.append(list_item)


def findDelim(line2):

	tokens = string.split(string.strip(line2,'\n'),'\t')
	if len(tokens) > 1:  # if found a tab:
		delim='\t'
		numCols=len(tokens)
		return delim, numCols

	tokens = string.split(string.strip(line2,'\n'),',')
	if len(tokens) > 1:  # if found a comma:
		delim=','
		numCols=len(tokens)
		return delim, numCols

	tokens = string.split(string.strip(line2,'\n'),'   ')
	if len(tokens) > 1:  # if found 3 spaces:
		delim='   '
		numCols=len(tokens)
		return delim, numCols

	tokens = string.split(line2.lstrip(' ').rstrip(' \n'),' ')
	if len(tokens) > 1:  # if found 3 spaces:
		delim=' '
		numCols=len(tokens)
		return delim, numCols


def ExpDecay(x,params):
    return(exp(-x/params[0]))


def residualsExpDecay(params,x1,y1):
	err = abs(y1 - ExpDecay(x1,params))
	#err = sqrt(abs(y1*y1-Gaussian(x1,params)*Gaussian(x1,params)))
	return err


def Gaussian(x,params):
    return(exp(-(x-params[0])*(x-params[0])/(2*params[1]*params[1])))


def residualsGaussian(params,x1,y1):
	err = abs(y1 - Gaussian(x1,params))
	#err = sqrt(abs(y1*y1-Gaussian(x1,params)*Gaussian(x1,params)))
	return err


# print out the class info:
def printClass(className):
	for key in dir(className):
		if not key.startswith('__'):
			value = getattr(className,key)
			if not callable(value):
				print key + ' = ' + str(value)

	return


# print list of classes:
def printClassList(classList):
	for className in classList:
		printClass(className)

	return


# print out one class attribute in a list containing classes:
def printClassListAttr(classList,key):
	for className in classList:
		if not key.startswith('__'):
			try:
				value = getattr(className,key)
				if not callable(value):
					print key + ' = ' + str(value)
			except AttributeError:
				print 'generic.py::printClassListAttr::Warning:: unknown attribute '+str(key)+ ' for class '+str(className)

	return



# search list of classes for each time class has key matching searchFor:
def searchClassList(classList,key,searchFor):
	result = []   # number of times "searchFor" matches the value of classList[x].key
	for x in range(len(classList)):
#		print className, key, searchFor
		if not key.startswith('__'):
			try:			
				value = getattr(classList[x],key)
				if not callable(value):
					if value == searchFor:
						result.append(x)
				else:
					result.append(-1)
			except AttributeError:
				pass

	return result



# search list of classes for one attribute matching:
def countClassList(classList,key,searchFor):
	result = 0   # number of times "searchFor" matches the value of classList[x].key
	for className in classList:
#		print className, key, searchFor
		if not key.startswith('__'):
			try:			
				value = getattr(className,key)
				if not callable(value):
					if value == searchFor:
						result = result + 1
				else:
					result = -1
			except AttributeError:
				pass

	return result



#### class prototype for all the information about a (single-axis) plot 
class PlotInfo():
	def __init__(self, **kwargs):

		# defaults:
		self.filename = 'newfigure.dat'
#		self.fromPickle = True			# if true then filename is a pickle dump of data, otherwise it is a text array

		self.dpi = '100'
		self.drawx = 0
		self.drawy = 1
		self.figsize = [5.0, 4.0]
		self.figureLineWidth = 2
		self.figureFontSize = 16
		self.figureFontFamily = 'serif'
		self.grid = 0
		self.gridColour = (0,0,0)
		self.gridLinestyle = ':'
		self.gridLinewidth = '0.5'
		self.labelx=0
		self.labely=0
		self.labelFontSize=12
		self.labelText=''
		self.legendAlpha = 1.0
		self.legendFontSize = '14'
		self.legendFrame = 1
		self.legendLabels = []
		self.legendLoc = 'no legend'
		self.legendShadow = 0
		self.lineColours = []
		self.lineStyles = []
		self.lineWidths = []
		self.lineMarkers = []
		self.rect = [0.2, 0.2, 0.75, 0.75]
		self.subplot = '111'
		self.title = ''
		self.xlabel = 'x'
		self.xmax = None
		self.xmin = None
		self.xscale = 'linear'
		self.ylabel = 'y'
		self.ymax = None
		self.ymin = None
		self.yscale = 'linear'

		# take params from kwargs (overwrites defaults)
		for x,y in zip(kwargs.keys(),kwargs.values()):
			setattr(self,x,y)



def getRange(xarray,minVal,maxVal):
	xmin=0
	xmax=len(xarray)

	for m in range(len(xarray)):
		if xarray[m]>minVal:
			if m>1:
				xmin=m
			else:
				xmin=0
			break

	for m in range(len(xarray)):
		if xarray[m]>maxVal:
			if m>1:
				xmax=m-1
			else:
				xmax=len(xarray)
			break

	return xmin,xmax

