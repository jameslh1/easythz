from pylab import angle as calcangle

from physconst import *
from plotSettings import *

from src.generic import printClass
from drude import *
from magnon import *
from fitEps import taucLorentz, calcModel
from phonon import Phonon


# Represents layer of material in a structure
class layer():

	def __init__(self, omega, thickness=1.0e-3, num=1.0e18, tau=100.0, material='air', Bfield=0.0,
	                                                     meff=1.0, epsS=1.0, epsI=1.0, fTO=0.0e12):

		#self.material = materialclass createHeterostructure():
	
		self.ar = []
		self.num = num * 1e6		# electron density (m-3)
		self.tau = tau * 1e-15		# scattering time (s)
		self.d = thickness		# thickness (m)
		self.mu = 1.0			# default to permeability = 1.0

		if material in ALLOWED_MATERIAL_LIST and self.validInput:
			if material=='air':
				n = 1.0 * ones(len(omega))
				k = 0.0

			elif material=='genericDrude':
				D=Drude(N=num, tau=self.tau, material='generic', meff=meff, epsS=epsS, epsI=epsI,
					Bfield=Bfield, model='Drude', overrideOmega=True, newOmega=omega)
				self.cond=D.cond

				n = D.realn
				k = D.imagn

			elif material=='singlePhonon':
				omTO = 2*pi*2.4e12
				gam = 1.0/200e-15
				eI = 10.0
				eS = 12.0
				p=Phonon(material='generic', overrideOmega=True, newOmega=omega, epsI=eI,
					                                          omegaTO=omTO, Gamma=gam)
				n = p.realn
				k = p.imagn

			elif material=='SiN':
				n = 1.5 * ones(len(omega))
				k = 0.0

			elif material=='GaAs':
#				n = 3.6 * ones(len(omega))
#				k = 0.0

				data = loadtxt(MATERIALS_PATH+'GaAs.nk',comments='%')
				om=2*pi*c/(data[:,0]*1e-10)	# angular frequency of data
				nt=data[:,1]	# real part of n
				kt=data[:,2]	# imag part of n
				om=flipud(om)
				nt=flipud(nt)
				kt=flipud(kt)
			
				n = interp(omega,om,nt)
				k = interp(omega,om,kt)

			elif material=='ZnO':
				n = 1.96 * ones(len(omega))
				k = 0.0

			elif material=='ZnOTHz':
				n = 3.3 * ones(len(omega))
				k = 0.0

			elif material=='SrTiO3':
				p=Phonon(material='SrTiO3',overrideOmega=True,newOmega=omega)
				n = p.realn
				k = p.imagn

			elif material=='LaAlO2':
				p=Phonon(material='LaAlO3-Calvani-300K',overrideOmega=True,newOmega=omega)
				n = p.realn
				k = p.imagn


			elif material=='LaAlO':
				n = Cauchy(omega,2.119,0.01384*(1e-6)**2,-0.0001*(1e-6)**4)
#				n = 2.119 * ones(len(omega))
				k = 0.0 * ones(len(omega))

			elif material=='Ag':
				data = loadtxt(MATERIALS_PATH+'Ag-nk.txt',comments='%')

				om=data[:,0]*eV/hbar	# angular frequency of data
				nt=data[:,1]		# real part of n
				kt=data[:,2]		# imag part of n
			
				n = interp(omega,om,nt)
				k = interp(omega,om,kt)

			elif (material=='Cu2O') or (material=='CuO'):
				data = loadtxt(MATERIALS_PATH+material+'-nk.txt',comments='%',delimiter=',')

				om=2*pi*c/(data[:,0]*1e-6)	# angular frequency of data
				nt=data[:,1]		# real part of n
				kt=data[:,2]		# imag part of n

				n = interp(omega,om,nt)
				k = interp(omega,om,kt)

			elif material=='InP':
#				n = 3.1 * ones(len(omega))
#				k = 0.0

				data = loadtxt(MATERIALS_PATH+'InP.nk',comments='%')
				om=2*pi*c/(data[:,0]*1e-10)	# angular frequency of data
				nt=data[:,1]	# real part of n
				kt=data[:,2]	# imag part of n
				om=flipud(om)
				nt=flipud(nt)
				kt=flipud(kt)

				n = interp(omega,om,nt)
				k = interp(omega,om,kt)

			elif material=='BiFeO3-rhombohedral':
				data = loadtxt(MATERIALS_PATH+'BiFeO3-rhombo-eps.txt',comments='%')
				eps=data[:,1]+i*data[:,2]
				eps=eps/1.12
				om=data[:,0]*eV/hbar	# angular frequency of data
				nt=real(sqrt(eps))	# real part of n
				kt=imag(sqrt(eps))	# imag part of n
		
				n = interp(omega,om,nt)
				k = interp(omega,om,kt)

			elif material=='BiFeO3-tetragonal':
				data = loadtxt(MATERIALS_PATH+'BiFeO3-tetragonal-eps.txt',comments='%')
				eps=data[:,1]+i*data[:,2]
				om=data[:,0]*eV/hbar	# angular frequency of data
				nt=real(sqrt(eps))	# real part of n
				kt=imag(sqrt(eps))	# imag part of n
			
				n = interp(omega,om,nt)
				k = interp(omega,om,kt)

			elif material=='sapphire':
				n = 1.76 * ones(len(omega))
				k = 0.0

			elif material=='ITO':
				n = 1.85 * ones(len(omega))	# at 800nm, from Luxpop website
				k = 0.012 * ones(len(omega))

			elif material=='ITOthz':
				eI=4.0
				sig0=5.8e5
				gamma=50e12

				eps=eI + i * sig0 / (e0*omega*(1-i*omega/gamma))

				n = real(sqrt(eps))
				k = imag(sqrt(eps))

			elif material=='constant':
				n = 3.00 * ones(len(omega))	# 
				k = 0.000 * ones(len(omega))

			elif material=='TiO2':
				n = 2.79 * ones(len(omega))	# at 800nm, from Palik
				k = 0.000 * ones(len(omega))

			elif material=='TiO2thz':
				n = 12.0 * ones(len(omega))	
				k = 0.000 * ones(len(omega))

			elif material=='PET':
				n = 1.70 * ones(len(omega))	# from JOURNAL OF APPLIED PHYSICS 99, 066101 (2006)
				k = 0.00 * ones(len(omega))

			elif material=='PETthz':
#				n = 1.70 * ones(len(omega))	# from J. Kor. Phys. Soc. 49 513 (2006)
#				k = 0.00 * ones(len(omega))
				fExp  = array([0.25,1.5,2.75])
				omExp = 2*pi*fExp*1e12

				nExp  = array([1.75,1.68,1.64])
				alpha = array([500 ,4000,7000])/2.0
				
				kExp = c*alpha/(2*omExp)

				n=interp(omega,omExp,nExp)
				k=interp(omega,omExp,kExp)


			elif material=='magnonTest':
				m=MagnonRI(omega,fMagnon=0.7e12)

				n=real(m.n)
				k=imag(m.n)
	
				self.mu=m.mu			

			elif material=='MgO':
#				n = 3.1 * ones(len(omega))
#				k = 0.0

				data = loadtxt(MATERIALS_PATH+'MgO.nk',comments='%')
				om=2*pi*c/(data[:,0]*1e-10)	# angular frequency of data
				nt=data[:,1]	# real part of n
				kt=data[:,2]	# imag part of n
				om=flipud(om)
				nt=flipud(nt)
				kt=flipud(kt)
			
#				print all(diff(om)>0)
				n = interp(omega,om,nt)
				k = interp(omega,om,kt)

			elif material=='BFO-T':
				E=hbar*omega/eV   # energy in eV
				tc=taucLorentz(E)

				EPSI=2.24	# epsilon infinity
				EG  =2.14*eV

				# A = amplitude (energy), Gamma = width (energy),
				# E0 = centre of peak (energy), Eg=band gap (energy)
				osc1 = taucLorentz(E,A=1.05*eV, Gamma=0.24*eV, E0=3.01*eV, Eg=EG, epsI=EPSI)
				osc2 = taucLorentz(E,A=33.5*eV, Gamma=0.98*eV, E0=3.37*eV, Eg=EG, epsI=EPSI)
				osc3 = taucLorentz(E,A=47.03*eV, Gamma=1.77*eV, E0=4.91*eV, Eg=EG, epsI=EPSI)
				osc4 = taucLorentz(E,A=6.04*eV, Gamma=0.1*eV, E0=6.5*eV, Eg=EG, epsI=EPSI)
				model=[osc1,osc2,osc3,osc4]

				bdfo=calcModel(model,epsI=EPSI)

				n = real(bdfo.n)
				k = imag(bdfo.n)

			elif material=='TL2':
				E=hbar*omega/eV   # energy in eV
				tc=taucLorentz(E)

				# A = amplitude (energy), Gamma = width (energy), 
				# E0 = centre of peak (energy), Eg=band gap (energy)
				### PTFO-100
#				EPSI = 3.07	# epsilon infinity
#				EG   = 0.95*eV
#				osc1 = taucLorentz(E,A=2.82*eV, Gamma=0.31*eV, E0=3.14*eV, Eg=EG, epsI=EPSI)
#				osc2 = taucLorentz(E,A=22.76*eV, Gamma=1.85*eV, E0=4.42*eV, Eg=EG, epsI=EPSI)

				### PTFO-300
				EPSI = 3.3	# epsilon infinity
				EG   = 1.97*eV
				osc1 = taucLorentz(E,A=39.12*eV, Gamma=1.64*eV, E0=3.58*eV, Eg=EG, epsI=EPSI)
				osc2 = taucLorentz(E,A=16.73*eV, Gamma=1.45*eV, E0=4.72*eV, Eg=EG, epsI=EPSI)

				model=[osc1,osc2]

				bdfo=calcModel(model,epsI=EPSI)

				n = real(bdfo.n)
				k = imag(bdfo.n)

			else:	# default to vacuum
				print 'simTrans.layer():: unknown material "'+material+'", defaulting to vacuum'
				n = 1.00 * ones(len(omega))
				k = 0.0
		

			self.n   = n + i * k
			self.alpha = 2 * omega * k / c
			self.eps = self.n**2
