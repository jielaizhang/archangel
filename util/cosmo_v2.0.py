#!/usr/bin/env python
#
# http://www.astro.ucla.edu/~wright/CC.python
# written by James Schombert, jschombe@uoregon.edu, based on http://www.astro.ucla.edu/~wright/CosmoCalc.html
#
  
import sys
from math import *

try:
  if sys.argv[1] == '-h':
    print '''Cosmology calculator ala Ned Wright (www.astro.ucla.edu/~wright)
input values = redshift, Ho, Omega_m, Omega_vac
output values = age at z, distance in Mpc, kpc/arcsec, apparent to abs mag conversion

Options:   -h for this message 
           -v for verbose response '''
    print '-----------------------'
    print 'comoving radial distance of the source goes into Hubbles law'
    print 'comoving radial distance/(1+z) gives the distance of the source when the light was emitted (Prof. Edward L. Wright, UCLA, 2014.04.20)'
    print 'In an expanding and curved universe, (a universe that has curved 4-D spacetime, but flat 3-D space),'
    print 'angular-diameter distance has a remarkable property: it is always equal to the true or proper distance of the emitter at the time of emission.'
    print 'Gravitation and Spacetime, Hans C. Ohanian, Remo Ruffini, Cambridge University Press, Apr 8, 2013, p. 394'
    print '-----------------------'
    sys.exit()
  if sys.argv[1] == '-v':
    verbose=1
    length=len(sys.argv)-1
  else:
    verbose=0
    length=len(sys.argv)

# if no values, assume Benchmark Model, input is z
  if length == 2:
    redshift = float(sys.argv[1+verbose])
    scale_factor = 1/(redshift + 1.0)
    z=float(sys.argv[1+verbose])            # redshift
##
##
##    if float(sys.argv[1+verbose]) > 100:
##      z=float(sys.argv[1+verbose])/299790.    # velocity to redshift
##    else:
##     z=float(sys.argv[1+verbose])            # redshift
##
##
## Wilkinson Microwave Anisotropy Probe (WMAP), 2.2.3. Hubble Parameter
##    H0 = 73.8      # Hubble constant
## http://www.astro.ucla.edu/~wright/cosmolog.htm#News
## 06 June 2014 - Bennett et al. give a concordance value for the Hubble
## constant with a precision of one percent: Ho = 69.6 +/- 0.7 km/sec. This
## is based on CMB data, BAO data, and direct measurements of the Hubble
## constant. They also find the matter density M = 0.286 +/- 0.008. The
## Cosmology Calculator has been updated to use these as default values.
    H0 = 69.6       # Hubble constant
    WR = 0.         # Omega(radiation)
# Hubble constant per Wilkinson Microwave Anisotropy Probe (WMAP)
## http://lambda.gsfc.nasa.gov/product/map/current/params/lcdm_wmap9_spt_act_snls3.cfm
## WMAP Cosmological Parameters
##      WM = 0.270                      # Omega(matter)
##
    WM = 0.286                      # Omega(matter)
##    WV = 1.0 - WM - 0.4165/(H0*H0)  # Omega(vacuum) or lambda # original values
    WV = 0.714                      # Omega(vacuum) or lambda

# if one value, assume Benchmark Model with given H0
  elif length == 3:
    z=float(sys.argv[1+verbose])    # redshift
    H0 = float(sys.argv[2+verbose]) # Hubble constant
    WM = 0.3                        # Omega(matter)
    WV = 1.0 - WM - 0.4165/(H0*H0)  # Omega(vacuum) or lambda

# if Univ is Open, use Ho, Wm and set Wv to 0.
  elif length == 4:
    z=float(sys.argv[1+verbose])    # redshift
    H0 = float(sys.argv[2+verbose]) # Hubble constant
    WM = float(sys.argv[3+verbose]) # Omega(matter)
    WV = 0.0                        # Omega(vacuum) or lambda

# if Univ is General, use Ho, Wm and given Wv
  elif length == 5:
    z=float(sys.argv[1+verbose])    # redshift
    H0 = float(sys.argv[2+verbose]) # Hubble constant
    WM = float(sys.argv[3+verbose]) # Omega(matter)
    WV = float(sys.argv[4+verbose]) # Omega(vacuum) or lambda

# or else fail
  else:
    print 'need some values or too many values'
    sys.exit()

# initialize constants
#
# A Map of the Universe, J. Richard Gott III et al.,
# http://arxiv.org/abs/astro-ph/0310571, gives 14,300 Mpc, equation 11, 
# "This is the effective particle horizon, where we are seeing particles at the moment of the Big Bang."
# 4300*3.26 = 46.618 Gly
#
  size_universe  = (14300*3.26/1000)     # 46.618 Gly; see above
  WR = 0.        # Omega(radiation)
  WK = 0.        # Omega curvaturve = 1-Omega(total)
  c = 299792.458 # velocity of light in km/sec
## Tyr = 977.3    # coefficent for converting 1/H into Gyr
## 299972*3.262 = 978509, that is, speed of light X lightyears/parsec X 10**6
  Tyr = 978.509  # coefficent for converting 1/H into Gyr
  DTT = 0.5      # time from redshift z to now in units of 1/H0
  DTT_Gyr = 0.0  # value of DTT in Gyr == light travel time
  age = 0.5      # age of Universe in units of 1/H0
  age_Gyr = 0.0  # value of age in Gyr
  zage = 0.1     # age of Universe at redshift z in units of 1/H0
  zage_Gyr = 0.0 # value of zage in Gyr
  DCMR = 0.0     # comoving radial distance in units of c/H0
  DCMR_Mpc = 0.0 
  DCMR_Gyr = 0.0
  DA = 0.0       # angular size distance
  DA_Mpc = 0.0
  DA_Gyr = 0.0
  kpc_DA = 0.0
  DL = 0.0       # luminosity distance
  DL_Mpc = 0.0
  DL_Gyr = 0.0   # DL in units of billions of light years
  V_Gpc = 0.0
  a = 1.0        # 1/(1+z), the scale factor of the Universe
  az = 0.5       # 1/(1+z(object))

  h = H0/100.
  WR = 4.165E-5/(h*h)   # includes 3 massless neutrino species, T0 = 2.72528
  WK = 1-WM-WR-WV
  az = 1.0/(1+1.0*z)
  age = 0.
  n=10000        # number of points in integrals
  for i in range(n):
    a = az*(i+0.5)/n
    adot = sqrt(WK+(WM/a)+(WR/(a*a))+(WV*a*a))
    age = age + 1./adot

  zage = az*age/n
  zage_Gyr = (Tyr/H0)*zage
  DTT = 0.0
  DCMR = 0.0

# do integral over a=1/(1+z) from az to 1 in n steps, midpoint rule
  for i in range(n):
    a = az+(1-az)*(i+0.5)/n
    adot = sqrt(WK+(WM/a)+(WR/(a*a))+(WV*a*a))
    DTT = DTT + 1./adot
    DCMR = DCMR + 1./(a*adot)

  DTT = (1.-az)*DTT/n
  DCMR = (1.-az)*DCMR/n
  age = DTT+zage
  age_Gyr = age*(Tyr/H0)
  DTT_Gyr = (Tyr/H0)*DTT
  DCMR_Gyr = (Tyr/H0)*DCMR
  DCMR_Mpc = (c/H0)*DCMR

# tangential comoving distance

  ratio = 1.00
  x = sqrt(abs(WK))*DCMR
  if x > 0.1:
    if WK > 0:
      ratio =  0.5*(exp(x)-exp(-x))/x 
    else:
      ratio = sin(x)/x
  else:
    y = x*x
    if WK < 0: y = -y
    ratio = 1. + y/6. + y*y/120.
  DCMT = ratio*DCMR
  DA = az*DCMT
  DA_Mpc = (c/H0)*DA
  kpc_DA = DA_Mpc/206.264806
  DA_Gyr = (Tyr/H0)*DA
  DL = DA/(az*az)
  DL_Mpc = (c/H0)*DL
  DL_Gyr = (Tyr/H0)*DL

# comoving volume computation

  ratio = 1.00
  x = sqrt(abs(WK))*DCMR
  if x > 0.1:
    if WK > 0:
      ratio = (0.125*(exp(2.*x)-exp(-2.*x))-x/2.)/(x*x*x/3.)
    else:
      ratio = (x/2. - sin(2.*x)/4.)/(x*x*x/3.)
  else:
    y = x*x
    if WK < 0: y = -y
    ratio = 1. + y/5. + (2./105.)*y*y
  VCM = ratio*DCMR*DCMR*DCMR/3.
  V_Gpc = 4.*pi*((0.001*c/H0)**3)*VCM

  if verbose == 1:
    print 'For H_o = ' + '%1.3f' % H0 + ', Omega_M = ' + '%1.3f' % WM + ', Omega_vac = ',
    print '%1.3f' % WV + ', redshift z = ' + '%1.3f' % redshift
    print 'scale_factor of universe ' + '%1.3f' % scale_factor
    print ' '
    print 'NOW is the time when we observe the light; THEN is the time when the light was emitted'
    print 'Gyr = billions of years, Gly = billions of light years, Mpc = megaparsecs'
    print 'Hubble\'s Law uses comoving radial distance of the source'
    print ' '
    print 'Now: age of the universe (since the Big Bang)  = ' + '%2.3f' % age_Gyr + ' Gyr.'
    print 'Now: comoving horizon (size) of the universe   = ' + '%2.3f' % size_universe + ' Gly.'
##
## Distance measures in cosmology, David W. Hogg (IAS)
## (Submitted on 11 May 1999 (v1), last revised 16 Dec 2000 (this version, v4))
## http://arxiv.org/abs/astro-ph/9905116
## In terms of cosmography, the cosmological redshift is directly related
## to the scale factor a(t), or the "size" of the Universe. 
## For an object at redshift z, 1+z = a(to)/a(te) [equation 12]
## where a(to) is the size of the Universe at the time the light from the
## object is observed, and a(te) is the size at the time it was emitted.
## to means "time when light was observed"
## te means "time when light was emitted"
##
    print 'Then: comoving horizon (size) of the universe  = ' + '%2.3f' % (size_universe * scale_factor) + ' Gly.'
    print 'Then: age of the universe (since the Big Bang) = ' + '%2.4f' % (age_Gyr - DTT_Gyr) + ' Gyr.'
    print '   '

    print 'Now: comoving radial distance of the source    = ' + '%2.3f' % DCMR_Gyr + ' Gly. (' + '%2.2f' % DCMR_Mpc + ' Mpc)'
    D_emission = DCMR_Gyr * scale_factor
    print 'Then: comoving radial distance of the source   = ' + '%2.3f' % D_emission + ' Gly.'
    print '   '
    print 'The light travel time or lookback time         = ' + '%2.4f' % DTT_Gyr + ' Gyr.'
##
##
## Expanding Confusion: common misconceptions of cosmological horizons and
## the superluminal expansion of the universe; Davis and Lineweaver
## (Submitted on 28 Oct 2003 (v1), last revised 13 Nov 2003 (this version, v2))
## http://arxiv.org/abs/astro-ph/0310808v2
## Equation 18, vrec (t,z) = H(t) D(t)
## calc ( 13* ( 10**9 ) *69.6/ ( 3.26*1000000 ) ) = 277546
## 
    v_rec_now = ( ( (DCMR_Gyr * (10**9)) * H0)/ (3.26* (10**6)) )
    v_rec_now = v_rec_now/c
    print '   '
##  from Expanding Confusion: ... Davis, equation 25:
##  H(z) = H0 (1 + z) [1 + omega_m*z + omega_vac ( (1/ ((1 + z)**2)) - 1)]**.5
    H_then = H0 * (1 + z) * sqrt (1 + (WM * z) + WV * ( (1/ ((1 + z)**2)) - 1) )
    print 'Now: recession velocity                        = ' + '%2.3f' % v_rec_now + 'c'
    v_rec_then = ( ( (D_emission * (10**9)) * H_then)/ (3.26* (10**6)) )
    v_rec_then = v_rec_then/c
    print 'Then: recession velocity                       = ' + '%2.3f' % v_rec_then + 'c'
    print 'Now:  Hubble constant                          = ' + '%2.3f' % H0
    print 'Then: Hubble constant                          = ' + '%2.3f' % H_then
    print '   '
##
## Note:
## In a universe that has curved 4-D spacetime, but flat 3-D space, the comoving distance of the source when it emitted the light is equal to DA, the angular diameter distance
## 'Gravitation and Spacetime, Hans C. Ohanian, Remo Ruffini, Cambridge University Press, Apr 8, 2013, p. 394'

    print 'Angular Diameter distance (D_A)                = ' + '%2.3f' % DA_Mpc + ' Mpc or ' + '%2.2f' % DA_Gyr + ' Gly.'
    print 'The comoving volume within redshift z          = ' + '%2.3f' % V_Gpc + ' Gpc^3.'
    print 'The luminosity distance D_L                    = ' + '%1.3f' % DL_Mpc + ' Mpc or ' + '%1.2f' % DL_Gyr + ' Gly.'
    print 'The distance modulus, m-M,                     = ' +'%1.3f' % (5*log10(DL_Mpc*1e6)-5)
  else:
    print '%1.2f' % (age_Gyr - DTT_Gyr),
    print '%1.2f' % DCMR_Mpc,
    print '%1.2f' % kpc_DA,
    print '%1.2f' % (5*log10(DL_Mpc*1e6)-5)

except IndexError:
  print 'need some values or too many values'
except ValueError:
  print 'nonsense value or option'
##
## 3% Solution: Determination of the Hubble Constant with the Hubble Space Telescope and Wide Field Camera 3
## http://arxiv.org/abs/1103.2976v1
## Adam G. Riess (JHU, STScI), Lucas Macri (Texas A&M), Stefano Casertano
## (STScI), Hubert Lampeitl (U of Portsmouth), Henry C. Ferguson (STScI),
## Alexei V. Filippenko (UCB), Saurabh W. Jha (Rutgers), Weidong Li (UCB),
## Ryan Chornock (Harvard CfA) (Submitted on 15 Mar 2011)
## ...
## Our best estimate uses all three calibrations but a larger
## uncertainty afforded from any two: H0 = 73.8 +/- pm 2.4 km s- 1 Mpc-1
## including systematics, a 3.3% uncertainty.
## Subjects:	Cosmology and Nongalactic Astrophysics (astro-ph.CO)
## Journal reference:	ApJ, 730, 119, 2011
## Cite as:	arXiv:1103.2976 [astro-ph.CO]
## (or arXiv:1103.2976v1 [astro-ph.CO] for this version)
