from numpy import arctan, argmax, argmin, array, fft, imag, log, pi, real, sqrt, zeros

i = complex(0, 1)

# Takes a data and reference data set and uses them to calculate a transmision spectra
# Can linearly interpolate reference values for comparison with experimental data
# Methods can be called to perform various pieces of spectral analysis
class TransSpectraAnalysis():

	def __init__(self, time, signal, refTime, refSignal, doRefracIndexThin, doRefracIndexThick):

		self.time = time
		self.y = signal
		self.refTime = refTime
		self.refY = refSignal

		self.calcThickness(self.time, self.y, self.refTime, self.refY)

		cutoff = self.isolateFirstMaxima(self.y)
		self.cutoff = cutoff		
	
		self.calcTransSpectra(dataX=self.time[:cutoff], dataY=self.y[:cutoff],
		                      refDataX=self.refTime[:cutoff], refDataY=self.refY[:cutoff])

		self.phaseTrans = self.calcdelta(self.transSpectrum)
		self.linPhase = self.linearisePhase(self.phaseTrans, 2*pi, 0.75*2*pi)

		if doRefracIndexThin:
			self.refracIndexThin(self.freq, self.absTransSpectrum, self.thickness)

		if doRefracIndexThick:
			self.refracIndexThick(self.freq, self.linPhase, self.absTransSpectrum, self.thickness)


	# Calculate transmission for each frequency component by dividing the Fourier transform
	# of the data by the Fourier transform of a reference data set.
	def calcTransSpectra(self, dataX, dataY, refDataX, refDataY):

		fftdata = fft.ifft(dataY)
		fftlen = len(fftdata)
		self.cfield = fftdata[0:(fftlen/2+1)]
		timestep = abs(dataX[fftlen-1]-dataX[0])/(fftlen-1)
		self.freq = array(range(fftlen/2+1))/timestep/fftlen

		fftdata = fft.ifft(refDataY)
		fftlen = len(fftdata)
		self.refCField = fftdata[0:(fftlen/2+1)]
		timestep = abs(refDataX[fftlen-1]-refDataX[0])/(fftlen-1)
		self.refFreq = array(range(fftlen/2+1))/timestep/fftlen

		self.absCField = abs(self.cfield)
		self.refAbsCField = abs(self.refCField)

		self.transSpectrum = self.cfield / self.refCField
		self.absTransSpectrum = abs(self.transSpectrum)


	# Assumes maximum of first pulse of laser comes before the mimimum.
	# Can estimate the refractive index for a one-layer material from its spectrum as well
	# (not for multi-layer material due to multiple possible reflections of pulse inside)
	def calcThickness(self, dataX, dataY, refDataX, refDataY):

		# Find positions of the max value of both data sets
		maxData = argmax(dataY)
		maxRefData = argmax(refDataY)

		# Find maximum value in the experimental data set after the first minimum
		minData = argmin(dataY)
		maxData2 = argmax(dataY[minData:])

		# Calculate material thickness
		self.thickness = -299792458.0 * ((dataX[maxData2+minData]-dataX[maxData])/2 - (dataX[maxData]-refDataX[maxRefData]))*1e-12

		# Output indices for maxima locations
		self.maxima1 = maxData
		self.maxima2 = maxData2 + minData
		self.refMaxima1 = maxRefData


	# Relies on calcThickness() having been called first. It truncates the data
	# just before the second maxima (due to  reflected laser pulse)
	def isolateFirstMaxima(self, dataY):

		i = self.maxima2
		while dataY[i] > 0:
			i -= 1
		
		# Return the index to truncate the data at
		return i

	# Calculate refractive index from transmission spectrum in thick film approximation
	def refracIndexThick(self, freq, phaseOfTrans, absTransSpectrum, thickness, tol=0.001):

		self.refIndexThick = zeros(freq.size) + i*zeros(freq.size)   # Define array to be complex

		real = 1.0 + 299792458.0*phaseOfTrans*1e-12/(2*pi*freq*thickness)

		# Iteratively solve to find the imaginary component of the refractive index
		imag = zeros(freq.size)
		for j in range(freq.size):
			# Guess a starting point for iteration
			imag[j] = 0
			temp = 1

			while abs(imag[j] - temp) > tol:
				imag[j] = temp

				temp = -299792458.0*1e-12/(2*pi*freq[j]*thickness) * (log(absTransSpectrum[j]/4) + \
			        	                              log((1+real[j])*(1+real[j])+imag[j]*imag[j]))
			imag[j] = temp
			
			self.refIndexThick[j] = real[j] + i*imag[j]

		
	# Calculate refractive index from transmission spectrum in thin film approximation
	def refracIndexThin(self, freq, transmission, thickness):

		self.refIndexThin = zeros(freq.size)

		for j in range(freq.size):
			self.refIndexThin[j] = i*sqrt(1+(2-2/transmission[j])*i*299792458.0/(2*pi*freq[j]*1e12*thickness))


	# Returns the argument (phase) of the complex number rho
	def calcdelta(self, rho):

		delta=zeros(len(rho))

		for m in range(len(rho)):
			rrho=real(rho[m])
			irho=imag(rho[m])
			if rho[m]>0.0:
				delta[m]=arctan(irho/rrho)
			else:
				if irho>=0.0:
					delta[m]=arctan(irho/rrho)+pi
				else:
					delta[m]=arctan(irho/rrho)-pi

			# make delta range from 0<delta<360deg
			if delta[m]<0.0:
				delta[m]=delta[m]+2*pi

		return delta

	# Takes phases in interval and  changes them from being cyclic to continuous
	def linearisePhase(self, phases, intervalSize, maxDiscont):
		
		offset = 0

		for j in range(len(phases)-1):
			if abs(phases[j+1] - phases[j]+offset) > maxDiscont:
				offset += intervalSize	
			phases[j+1] += offset

		return phases











