import os
import string

from numpy import fft,array,gradient, append,insert
from pylab import find, pi
from scipy.optimize import leastsq
from generic import *

################################################

C = 299792458.0
PS_TO_MM = 0.1499

hbar = 1.05457266E-34
h = hbar * 2 * pi
eV = 1.60217733E-19



def getSampleThickness(xdata, xunit, refydata, samydata, peakWidth=20): 
	refmaxVal=max(refydata)
	refmaxPos=find(refydata==refmaxVal)[0]
	maxVal=max(samydata)
	maxPos=find(samydata==maxVal)[0]
	maxPos2=maxPos

	if (maxPos+peakWidth)<len(samydata):
		maxVal2=max(samydata[maxPos+peakWidth:])
		maxPos2=find(samydata==maxVal2)[0]

	if xunit=='mm':
		t0=xdata[refmaxPos]/PS_TO_MM/1e12
		t1=xdata[maxPos]/PS_TO_MM/1e12
		t2=xdata[maxPos2]/PS_TO_MM/1e12
	elif xunit=='ps':
		t0=xdata[refmaxPos]/1e12
		t1=xdata[maxPos]/1e12
		t2=xdata[maxPos2]/1e12
	else:
		t0=xdata[refmaxPos]
		t1=xdata[maxPos]
		t2=xdata[maxPos2]

	#print t0, t1, t2
	dt1 = t1-t0
	dt2 = t2-t1

	if dt2>0:   # if found a second peak in data
		ns = dt2/(dt2-2*dt1)
		d = C * (dt2 - 2*dt1) / 2.0
	else:   # assume some values
		d = 400e-6
		ns = 3.5

	return ns, d		#	returns real part of refractive index and d (m)


# extend length of "xdata" & "ydata" by a scale factor of "expansion"
def zeropad(xdata,ydata,expansion=2):
	if expansion>1:
		print 'zeropadded'
		spacing=xdata[2]-xdata[1]
		newx = xdata
		newy = ydata

		lastPoint=len(xdata)
		x0=xdata[-1]

		for x in range(expansion*len(xdata)):
			newx=append(newx,x0+x*spacing)
			newy=append(newy,0.0)

	else:
		newx = xdata
		newy = ydata


	return newx, newy


# extend length of "xdata" & "ydata" by a scale factor of "expansion"
def zeropadStart(xdata,ydata,expansion=2):
	if expansion>1:
		print 'zeropadded start'
		spacing=xdata[1]-xdata[2]
		newx = xdata
		newy = ydata

		lastPoint=len(xdata)
		x0=xdata[0]

		for x in range(expansion*len(xdata)):
			newx=insert(newx,0,x0+x*spacing)
			newy=insert(newy,0,0.0)

	else:
		newx = xdata
		newy = ydata


	return newx, newy



# set region around second peak to zero
def zeroSecondPeak(ydata,peakWidth=25):
	maxVal=max(ydata)
	maxPos=find(ydata==maxVal)[0]
	maxPos2=maxPos

	if (maxPos+peakWidth)<len(ydata):
		maxVal2=max(ydata[maxPos+peakWidth:])
		maxPos2=find(ydata==maxVal2)[0]

	if ((maxPos2-peakWidth)>0) and ((maxPos2 + peakWidth)<len(ydata)):
		for m in range(maxPos2-peakWidth,maxPos2+peakWidth):
			ydata[m]=0.0
		return ydata
	elif ((maxPos2-peakWidth)>0):
		for m in range(maxPos2-peakWidth,maxPos2+peakWidth):
			ydata[m]=0.0

	return ydata


# take the Fourier transform of "ydata", calculate the frequency axis using "xdata" and "xunit"
def takeFFT(xdata, ydata, xunit='s'):
	fftdata=fft.fft(ydata)

	fftlen=len(fftdata) #fftdata.shape[0]

	if xunit=='mm':
		sf=0.1499
		xlabel='Frequency (THz)'
	elif xunit=='ps':
		sf=1
		xlabel='Frequency (THz)'
	else:
		sf=1
		xlabel='Frequency (Hz)'

	timestep=abs(xdata[fftlen-1]-xdata[0])/(fftlen-1)/sf
	frequency=array(range(fftlen/2+1))/timestep/fftlen

#	lineStr = 'Spectral resolution = %(x)5.4fTHz, bandwidth = %(y)5.4fTHz\n' % {'x':(frequency[1]-frequency[0]), 'y':frequency[-1]}
#	print lineStr

#		shortfilename=self.pageTree.prefilename+'.fft'
#		dataArray=row_stack((frequency,abs(fftdata[0:(fftlen/2+1)]),unwrap(angle(fftdata[0:(fftlen/2+1)]))))
#		savedata(prm.plotDir,shortfilename,'% Frequency, |FFT|, <FFT \n',dataArray)

	return frequency, fftdata[0:(fftlen/2+1)], xlabel


# take the Inverse Fourier transform of "ydata", calculate the frequency axis using "xdata" and "xunit"
def takeIFFT(xdata, ydata, xunit='s'):
	fftdata=fft.ifft(ydata)

	fftlen=len(fftdata) #fftdata.shape[0]

	if xunit=='mm':
		sf=0.1499
		xlabel='Frequency (THz)'
	elif xunit=='ps':
		sf=1
		xlabel='Frequency (THz)'
	else:
		sf=1
		xlabel='Frequency (Hz)'

	timestep=abs(xdata[fftlen-1]-xdata[0])/(fftlen-1)/sf
	frequency=array(range(fftlen/2+1))/timestep/fftlen

#	lineStr = 'Spectral resolution = %(x)5.4fTHz, bandwidth = %(y)5.4fTHz\n' % {'x':(frequency[1]-frequency[0]), 'y':frequency[-1]}
#	print lineStr

#		shortfilename=self.pageTree.prefilename+'.fft'
#		dataArray=row_stack((frequency,abs(fftdata[0:(fftlen/2+1)]),unwrap(angle(fftdata[0:(fftlen/2+1)]))))
#		savedata(prm.plotDir,shortfilename,'% Frequency, |FFT|, <FFT \n',dataArray)

	return frequency, fftdata[0:(fftlen/2+1)], xlabel


def fitExpDecay(xdata,ydata,useWholeRange=False):
	x1=array(xdata)
	y1=array(ydata)

	maxVal=max(y1)
	maxPos=find(y1==maxVal)[0]

	if useWholeRange:
		xRange=x1[:]-x1[maxPos]
		yRange=y1[:]/maxVal
	else:
		xRange=x1[maxPos:]-x1[maxPos]
		yRange=y1[maxPos:]/maxVal


	p0 = [100] # initial guesses

	pbest = leastsq(residualsExpDecay,p0,args=(xRange,yRange),full_output=1)
	fitparams = pbest[0]

	legStr = 'decay time = %(tau)4.3f' % {'tau':fitparams}
	print legStr

	simDecay = ExpDecay(xRange,[fitparams])
	simDecay = simDecay * maxVal

	return xRange+x1[maxPos], simDecay


def findBeamwidth(xdata,ydata) :
	x1=array(xdata)
	y1=array(ydata)

	grady1=abs(gradient(y1))
	maxGradVal=max(grady1)
	maxGradPos=find(grady1==maxGradVal)[0]

	if maxGradPos>len(x1):
		maxGradPos=len(x1)-1

	if y1[maxGradPos+1]>y1[maxGradPos]:
		slope='+'
	else:
		slope='-'
#	print 'Max. gradient: (' + str(x1[maxGradPos]) + ',' + slope + str(maxGradVal) + ')'

	p0 = [x1[maxGradPos],0.1] # initial guesses

	beamShape=grady1/maxGradVal
	pbest = leastsq(residualsGaussian,p0,args=(x1,beamShape),full_output=1)
	fitparams = pbest[0]
	fitparams[1]=abs(fitparams[1])

	simBeamShape = Gaussian(x1,fitparams)
	simBeamShape = simBeamShape * max(y1)

	return simBeamShape, beamShape, fitparams




def findFWHM(xdata, ydata):
	x1=array(xdata)
	y1=array(ydata)


	maxVal=max(y1)
	maxPos=find(y1==maxVal)[0]

	minVal=min(y1)
	HMheight = (maxVal+minVal)/2.0

#	print maxPos, maxVal, minVal, HMheight
	mPos1 = 1
	mPos2 = 2
	for m in range(len(y1)):
		if y1[m]>HMheight:
			mPos1 = m
			break

	for m in range(maxPos,len(y1)):
		if y1[m]<HMheight:
			mPos2 = m
			break


	dx=xdata[mPos2]-xdata[mPos1]

	return dx, (xdata[mPos1],ydata[mPos1]), (xdata[mPos2],ydata[mPos2])



#### routine to convert xunits from one unit to another
def convertXunit(oldXdata,oldXunit,newXunit):

	if (oldXunit=='THz'):
		x_THz=oldXdata
		x_J  =h*x_THz*1e12
		x_eV =x_J/eV
		x_meV=x_eV/1e-3
		x_icm=x_THz*33.3
		x_nm =(h*c/x_J)/1e-9
		x_um =(h*c/x_J)/1e-6 

	elif (oldXunit=='nm'):
		x_nm =oldXdata
		x_um =oldXdata/1e3
		x_THz=(c/(x_nm*1e-9))/1e12
		x_J  =h*x_THz*1e12
		x_eV =x_J/eV
		x_meV=x_eV/1e-3
		x_icm=x_THz*33.3

	elif (oldXunit=='um'):
		x_um =oldXdata
		x_nm =x_um*1e3
		x_THz=(c/(x_nm*1e-9))/1e12
		x_J  =h*x_THz*1e12
		x_eV =x_J/eV
		x_meV=x_eV/1e-3
		x_icm=x_THz*33.3

	elif (oldXunit=='icm'):
		x_icm=oldXdata
		x_THz=x_icm/33.3
		x_J  =h*x_THz*1e12
		x_eV =x_J/eV
		x_meV=x_eV/1e-3
		x_nm =(h*c/x_J)/1e-9
		x_um =(h*c/x_J)/1e-6 


	if (newXunit=='eV'):
		return x_eV
	elif (newXunit=='meV'):
		return x_meV
	elif (newXunit=='THz'):
		return x_THz
	elif (newXunit=='icm'):
		return x_icm
	elif (newXunit=='nm'):
		return x_nm
	elif (newXunit=='um'):
		return x_um
	else:
		return oldXdata
