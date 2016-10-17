	character op*20

      n=iargc()              ! command line read
      call getarg(1,op)
      if(op == '-h') then
	  print 70
70	format(' Helio       Galactic       flow   Hubble   ',
     *    'D      mag     vg'/'  vel     l     b    corr    ',
     *    'vel    vel                  radius')
        call getarg(2,op)
        read(op,*) ra
        call getarg(3,op)
        read(op,*) dec
        call getarg(4,op)
        read(op,*) v
      else
        call getarg(1,op)
        read(op,*) ra
        call getarg(2,op)
        read(op,*) dec
        call getarg(3,op)
        read(op,*) v
      endif
	pi=2.0*asin(1.)
	c=299790.
	xho=75.
*	  ra=(ih+xm/60.)*pi/12.
*	  if(sign.eq.'-') then
*	    dec=-pi*(id+xs/60.)/180.
*	  else
*	    dec=pi*(id+xs/60.)/180.
*	  endif
	  call velocity(v,ra/pi,dec/pi)
999	end

	subroutine velocity(v,ra,dec)

*	v = heliocentric velocity in km/s
*	ra, dec in radians
*	Ho=85, Virgo distance=15.02 Mpc, Virgo infall=300 km/s

	real*4 l,b,ra,dec
	pi=3.1415926536
	c=299790.

*** compute Galactic coords
      x1=pi*282.25/180.
      x2=pi*62.6/180.
      b=sin(dec)*cos(x2)-cos(dec)*sin(ra-x1)*sin(x2)
      b=asin(b)
      l=(cos(dec)*cos(ra-x1))/cos(b)
      l=acos(l)
      sx=(cos(dec)*sin(ra-x1)*cos(x2)+sin(dec)*sin(x2))/cos(b)
      sx=asin(sx)
      sec=l
      if(sec.gt.0.and.sx.gt.0) l=l+pi*33./180.
      if(sec.lt.0.and.sx.gt.0) l=pi*213./180.-l
      if(sec.lt.0.and.sx.lt.0) l=l+pi*213./180.
      if(sec.gt.0.and.sx.lt.0) l=pi*393./180.-l
      l=l*180./pi
      b=180.*b/pi
	if(l.ge.360.) l=l-360.
      if(l.lt.0.) l=l+360.

	call hoffman(v,ra,dec,l,b)
999	return
	end

*	PROGRAM INFALL

*     Purpose:  This program is designed to compute the distance to
*               a galaxy which deviates from Hubble flow because of
*               the gravitational infall component to the Virgo Cluster.
*               written by H. Williams 1988; modified by L. Hoffman 1990

	subroutine hoffman(vx,ra,dec,xl,xb)
	implicit real*8(a-h,o-z)
	real*4 xl,xb,xmag,c,vx,ra,dec,h0
	common pi,rlg,rlg2,fn,qpisq

	c=299790.
	pi=2.0*dasin(1d0)
	fn=4.0/9.0
	qpisq=0.25*pi** 2
	p180=pi/180.0
	p12=pi/12.0
	v=vx

*     RA and DEC of the Virgo Core - Huchra 1981

	alv=(12.0+27.6/60.0)*p12
	dlv=(12.0+56.0/60.0)*p180
	cdlv=dcos(dlv)
	sdlv=dsin(dlv)

*1     write(*,6001)
*6001  format('		  Virgocentric Infall'//
*     *' Please input the Virgocentric distance, velocity of the'/
*     *' Virgo core (heliocentric), and the value of Omega:'/
*     *' (If distance is less than zero, the program stops and if'/
*     *' it is zero the program computes its own value for this var.)'/
*     *'=Program now expects heliocentric velocities. =')
*	read(*,*) rlg,vlg,om
*	write(*,129) rlg,vlg,om
*129   format('input: RLG=',F7.1,'VLG=',F7.1,'OM=',F4.2)

*	locking values of Virgo distance (13.2 Mpc) and Virgo heliocentric
*	velocity of 1094 km/s (Binggeli etal 1980) - Oemga is set to make
*	the infall velocity equal to 300 km/s - this produces Ho=85

	rlg=15.02
* Virgo heliocentric - 117 Gal rot
	vlg=977.
* Omega needed to get infall = 300
	om=.12395
	if(rlg.gt.0.0) goto 2

*     Find distance to Virgo Cluster from Local Group using our own 
*     deviation from Hubble flow and then use V/H naught as an initial
*     guess for the iteration procedure. This branch of the program is
*     called if the distance to the local group is not given.

*     Hubble constant assumed = 85 unless both distance and velocity
*     are given for Virgo.

	rlg=vlg/h0
	rlg2=rlg*rlg
	d=0.0
	cth=0.0
	do it=1,20
	  call delv(d,cth,om,rvlg,vbvh,cp,izv)
        if(izv.eq.1) then
	    write(*, 6599)
6599      format('first guess inside the zero velocity surface')
	    dnew=v/h0
	    goto 520
	  endif 
	  rlg0=rlg
	  dvlg=-h0*rlg*(vbvh-1.0)*cp
	  rlg=(vlg+dvlg)/h0
	  rlg2=rlg*rlg
	  if(dabs((rlg-rlg0)/rlg0).lt.1e-3) goto 30
	enddo
	write(*,*) 'No distance to local group; program stopped'
	return

*     Local Group distance was inputted.

2     d=0.0 
	rlg2=rlg*rlg
	cth=1.0
	call delv(d,cth,om,rvlg,vbvh,cp,izv)
      if(izv.eq.1) then 
	  write(*,6599)
	  dnew=v/h0
	  goto 520
	endif
	h0=vlg/(vbvh*rlg)
	dvlg=(1.0/vbvh-1.0)*vlg
30	continue
*	write(*,35) rlg, dvlg, h0
35	format('Virgo Distance = ',F4.1,' Mpc Infall Vel = ',F5.1,' Ho = ',F5.1)

*     Input velocity and coordinates for galaxy whose distance is
*     sought.

*10	write(*,*) 'Input v,alh,alm,dld,dlm:'
*	read(*,*,err=999) v,alh,alm,dld,dlm

*     Virgocentric velocity changed to Heliocentric.

*	al=(float(alh)+alm/60.0)*p12
*	dl=(float(dld)+float(dlm)/60.0)*p180
	al=ra
	dl=dec
	cdl=dcos(dl)
	sdl=dsin(dl)
	call cvrt(al,dl,cdl,sdl,bch,velcor)
	v=v+velcor
	cth=cdl*cdlv*dcos(al-alv)+sdl*sdlv
	d=(v+dvlg*cth)/h0
	du=10.0*d
	dl=0.0
	itry=0

*     Beginning of the loop

500   itry=itry + 1
	call delv(d,cth,om,rv,vbvh,cp,izv)
	vbvh0=vbvh
	rv0=rv
	if(itry.eq.1) then
	  izvh=izv
	  if(izvh.eq.1) then
	    astep=5.0 * d / 200.0
	    dum=0.0
	    call delv(astep,cth,om,rv,vbvh,vp,izv)
	    ym=v-(astep*h0-dvlg*cth-h0*rv*(vbvh-1.0)*vp)
	    xym=astep
	    do 151 a1=astep*2.0, 5.0*d, astep
		call delv(a1,cth,om,rv,vbvh,vp,izv)
		yr=v-(h0*a1-dvlg*cth-h0*rv*(vbvh-1.0)*vp)
		if(ym*yr.lt.0.0.and.dum.eq.2.0) then
		  x3l=xym
		  x3r=a1
		  dum=3.0
*		  write(*,601) dum,ym,yr,x3l,x3r
		endif
		if(ym*yr.lt.0.0.and.dum.eq.1.0) then
		  x2l=xym
		  x2r=a1
		  dum=2.0
*		  write(*,601) dum,ym,yr,x2l,x2r
		endif
		if(ym*yr.lt.0.0.and.dum.eq.0.0) then
		  x1l=xym
		  x1r=a1
*		  write(*,601) dum,ym,yr,x1l,x1r
		  dum=1.0
		endif
601		format(' ',f2.0,4f9.3)
		xym=a1
		ym=yr
151	    continue
	  endif
	endif
	vbvh=vbvh0
	rv=rv0
	dv=-h0*rv*(vbvh-1.0)*cp
	dnew=(v-dv+dvlg*cth)/h0
*	write(*,*) 'Trial ',itry,d,dnew
	if(dabs((dnew-d)/d).lt.1e-3) goto 520
	if(itry.eq.20) goto 590
	if(dnew.gt.d) dl=d
	if(dnew.lt.d) du=d
	if(dnew.ge.du.or.dnew.le.dl) dnew=0.5*(du+dl)
	d=dnew
	goto 500

590   print*, ' '
	print*, '*** failed ***'
	print*, ' '
	dnew=0.5*(d+dnew)
520   d=dnew
70	format(' Helio       Galactic       flow   Hubble   ',
     *    'D      mag     vg'/'  vel     l     b    corr    ',
     *    'vel    vel                  radius')
6520  format(f7.1,2f6.1,2f7.1,f8.1,f6.1,f8.2,f7.1,i5,i7)
	if(izvh.eq.1) then
	  print*, '*** triple point distance ***'
	  print*, ' '
	  print 70
	  x1=x1l
	  x2=x1r
	  d=rtbis(x1,x2,d,cth,om,rvlg,vbvh,cp,izv,v,h0,dvlg,rv)
	  vx=d*h0
	  xmag=-5.*alog10(vx*(1.+vx/(2.*c)))+5.*alog10(h0)-25.
	  write(*,6520) v-velcor,xl,xb,velcor,vx-v,vx,d,xmag,rv
	  x1=x2l
	  x2=x2r
	  d=rtbis(x1,x2,d,cth,om,rvlg,vbvh,cp,izv,v,h0,dvlg,rv)
	  vx=d*h0
	  xmag=-5.*alog10(vx*(1.+vx/(2.*c)))+5.*alog10(h0)-25.
	  write(*,6520) v-velcor,xl,xb,velcor,vx-v,vx,d,xmag,rv
	  x1=x3l
	  x2=x3r
	  d=rtbis(x1,x2,d,cth,om,rvlg,vbvh,cp,izv,v,h0,dvlg,rv)
	  vx=d*h0
	  xmag=-5.*alog10(vx*(1.+vx/(2.*c)))+5.*alog10(h0)-25.
	  write(*,6520) v-velcor,xl,xb,velcor,vx-v,vx,d,xmag,rv
	  print '(a,$)', 'Choose 1,2 or 3 solution: '
	  read(*,*) ipick
	  if(ipick.eq.1) then
          x1=x1l
          x2=x1r
	  endif
	  if(ipick.eq.2) then
          x1=x2l
          x2=x2r
	  endif
	  if(ipick.eq.3) then
          x1=x3l
          x2=x3r
	  endif
        d=rtbis(x1,x2,d,cth,om,rvlg,vbvh,cp,izv,v,h0,dvlg,rv)
        vx=d*h0
	else
	  vx=d*h0
	  xmag=-5.*alog10(vx*(1.+vx/(2.*c)))+5.*alog10(h0)-25.
	  write(*,6520) v-velcor,xl,xb,velcor,vx-v,vx,d,xmag,rv
	endif
999	return
	end

*     SUBROUTINE DELV.  This subroutine will calculate the Virgocentric
*     velocity / Hubble constant.
*     The variables used in the subroutine are:

*     INPUT
*     =====
*     D	Distance to the galaxy from the Local Group.
*     CTH    Cos of angle from Virgo to the Galaxy.
*     OM     Cosmological Constant Omega.

*     OUTPUT
*     ======
*     R	Distance to galaxy from Virgo.
*     VBVH   Virgocentric velocity/Hubble Velocity.
*     CP     Cos of the angle between the distance to the Virgo cluster
*		and the distance to the local group from that galaxy.
*     IZV    Flag indicating whether or not the galaxy is inside
*		the zero velocity surface (1=Yes, 0=No).

	SUBROUTINE DELV(D, CTH, OM, R, VBVH, CP, IZV)
	IMPLICIT REAL*8(A-H, O-Z)
	COMMON PI, RLG, RLG2, FN, QPISQ
	IZV=0
	D2=D*D
	R=DSQRT(RLG2 + D2 - 2.0 * RLG * D * CTH)
	R2=R * R
	IF (D .EQ. 0.0) CP=1.0
	IF (D .NE. 0.0) CP=(RLG2 - R2 - D2) / (2.0 * R * D)
	DEL1=OD(R,OM)
	DF=DEL1 * OM * FUNC(OM) ** 2
	I=0
	IF (DF .GT. QPISQ) GOTO 9999
	IF (DABS(DF - FN) .LT. 0.01) GOTO 100
	IF (DF .GT. FN) GOTO 200
C
C     Average value of omega inside shell on which galaxy resides
C     is less than 1.
C
	OM1=0.5
10    I=I + 1
	FOM1=FUNC(OM1)
	FCN=OM1 * FOM1 ** 2
	SQOM=DSQRT(1.0 - OM1)
	ARG=(2.0 / OM1) * (1.0 + SQOM) - 1.0
	ALARG=DLOG(ARG)
	FCNP=FCN*(1.0/OM1+3.0/(1.0-OM1)-ALARG/(FOM1*SQOM**3))
	OMN=OM1 - (FCN - DF) / FCNP
	IF (OMN .GT. 1.0) OMN=OM1 + 0.5 * (1.0 - OM1)
	IF (OMN. LT. 0.0) OMN=0.5 * OM1
	IF (DABS((OMN-OM1)/OM1) .LT. 1E-4) GOTO 900
	IF (I .GT. 10) write(*, *) OMN, OM1, FCN, FCNP
	IF (I .EQ. 20) GOTO 999
	OM1=OMN
	GOTO 10
C
C     Here Omega is close to 1, so this approximation is valid.
C
100   OMN=1.0 - 45.0 * (FN - DF)/52.0
	GOTO 900
C
C     Here Omega is greater that 1.
C
200   OM1=200.0
	IF (DF .GT. 2.2) OM1=2000.0
210   I=I + 1
	FOM1=FUNC(OM1)
	FCN=OM1 * FOM1 ** 2
	OMM1=OM1 - 1.0
	SQOM=DSQRT(OMM1)
	FCNP=FCN * (3.0/OM1 - 3.0/OMM1 + 2.0/(OM1 * OMM1 * FOM1))
	OMN=OM1 - (FCN - DF) / FCNP
	IF (OMN .LT. 1.0) OMN=OM1 - 0.5 * (OM1 - 1.0)
	IF ((ABS((OMN-OM1)/OM1)) .LT. 1E-4) GOTO 900
	IF (I .GT. 80) write(*,*) OMN, OM1, FCN, FCNP
	IF (I .EQ. 100) GOTO 999
	OM1=OMN
	GOTO 210
900   OM1=OMN
	VBVH=FUNC(OM1)/FUNC(OM)
	RETURN
999   write(*, 6999) DF, OMN
6999  FORMAT(' OMN FAILED',2(1PE12.4))
	VBVH=1E20
	RETURN
C
C     Root computation inside the zero velocity surface.
C
9999  OM1=200.0
	IF (DF .LT. 2.8) OM1=2000.0
	IZV=1
10010 I=I + 1
	OMM1=OM1 - 1.0
	FOM1=FUNC(OM1)
	SQOM3=DSQRT(OMM1)**3
	FF=FOM1 - PI * OM1 / SQOM3
	FCN=OM1 * FF ** 2
	FCNP=FCN * (2.0 / (OM1 * OMM1 * FF) - 3.0 / (OMM1 * OM1))
	OMN=OM1 - (FCN - DF) / FCNP
	IF (OMN .LT. 1.0) OMN=OM1 - 0.5*(OM1 - 1.0)
	IF (DABS((OMN - OM1)/OM1) .LT. 1E-4) GOTO 10900
	IF (I .GT. 80) write(*, *) OMN, OM1, FCN, FCNP
	IF (I .EQ. 100) GOTO 999
	OM1=OMN
	GOTO 10010
10900 OM1=OMN
	VBVH=(FUNC(OM1)-PI*OM1/DSQRT(OM1-1.0)**3)/FUNC(OM)
	RETURN
	END
C
C     Function returns the value of a convenient function of Omega
C     of the system.
C
	FUNCTION FUNC(O)
	IMPLICIT REAL*8(A-H, O-Z)
	OMM1= O - 1.
	IF (DABS(OMM1) .LT. 0.01) GOTO 100
	IF (O .GT. 1.0) GOTO 200
	OMO=1. - O
	SQOM=DSQRT(OMO)
	FUNC=(1.0 - 0.5*O*DLOG(2.0 * (1.0 + SQOM)/O - 1.0)/SQOM)/OMO
	RETURN
100   FUNC=2.0 / 3.0 + 2.0 * (1.0 - O) / 15.0
	RETURN
200   OMO=O - 1.0
	SQOM=DSQRT(OMO)
	TOM1=2.0/O - 1.0
	FUNC=0.5 * O * (DACOS(TOM1) - 2.0*SQOM/O)/SQOM**3
	RETURN
	END
C
C     This subroutine will convert velocities from Heliocentric to
C     velocities relative to the barycenter of the Local Group which 
C     the program expects.
C
C     The routine inputs the right ascension (AL), the 
C     declination (DL) and returns the heliocentric velocity 
C     correction (V) and the galactic lattitude.
C
	SUBROUTINE CVRT(AL, DL, CDL, SDL, BCH, VELCOR)
	IMPLICIT REAL*8(A-H, O-Z)
	COMMON PI, RLG, RLG2, FN, QPISQ
	REAL*8 L, LLG, L0
C
C     Initialize constants.
C
	PI2=PI * 2.0
	P12=PI / 12.0
	P180=PI / 180.0
	L0=33.0 * P180
	LLG=105.0 * P180
	BLG=-7.0 * P180
	CBLG=COS(BLG)
	SBLG=SIN(BLG)
	DL1=62.6 * P180
	AL1=282.25 * P180
	SD1=SIN(DL1)
	CD1=COS(DL1)
	DL0=(27.0 + 24.0 / 60.0) * P180
	AL0=(12.0 + 49.0 / 60.0) * P12
	SD0=SIN(DL0)
	CD0=COS(DL0)
C
C     Do Calculations necessary.
C
	CAA0=COS(AL - AL0)
	SB=SDL * SD0 + CDL * CD0 * CAA0
	B=ASIN(SB)
	BCH=B/P180
	CB=COS(B)
	SLL0=(CDL * SIN(AL - AL1) *  CD1 + SDL*SD1) / CB
	CLL0=CDL * COS(AL - AL1) / CB
	ANG1=ASIN(SLL0)
	IF (CLL0 .LT. 0) ANG1=PI - ANG1
	L=L0 + ANG1
	CTH=SB * SBLG + CB*CBLG*COS(L - LLG)
	VELCOR=308.0 * CTH
C	WRITE(*,10) BCH, VELCOR
C10    FORMAT(' ==> Local Group velocity correction:'/
C     *'     ',F7.2,' Galactic latitude, and a velocity'/
C     *'	 correction of:',F10.1/)
	RETURN
	END
C
C     Function for bisection method to find roots; in Numerical Rec.
C     p.247.
C
	FUNCTION RTBIS(X1,X2,D,CTH,OM,RVLG,VBVH,CP,IZV,V,H0,DVLG,RV)
	IMPLICIT REAL*8(A-H,O-Z)
      real*4 H0
	COMMON PI, RLG, RLG2, FN, QPISQ
	PARAMETER (JMAX=40, XACC=1.0E-5)
	CALL DELV(X2,CTH,OM,RV,VBVH,CP,IZV)
	FMID=V-(H0*X2-DVLG*CTH-H0*RV*(VBVH-1.0)*CP)
	CALL DELV(X1,CTH,OM,RV,VBVH,CP,IZV)
	F=V-(H0*X1-DVLG*CTH-H0*RV*(VBVH-1.0)*CP)
	if(f*fmid.ge.0.) then
	  write(*,*) 'Root not bracketed'
	  write(*,*) x1,f
	  write(*,*) x2,f
	endif
	IF (F .LT. 0.0) THEN
	   RTBIS=X1
	   DX=X2 - X1
	ELSE
	   RTBIS=X2
	   DX=X1 - X2
	ENDIF
	DO 11 J=1,JMAX
	  DX=DX * 0.5
	  XMID=RTBIS + DX
	  CALL DELV(XMID,CTH,OM,RV,VBVH,CP,IZV)
	  FMID=V-(H0*XMID-DVLG*CTH-H0*RV*(VBVH-1.0)*CP)
	  IF(FMID.LT.0) RTBIS=XMID
	  IF(ABS(DX) .LT. XACC .OR. FMID .EQ.0.0) RETURN
11    CONTINUE
	WRITE(*,*) 'TOO MANY BISECTIONS'
	RETURN
	END
C
C
C     LEAST - SQUARES FIT TO LUMINOSITY OVERDENSITY.
C
	FUNCTION OD(R,OM)
	IMPLICIT REAL*8(A-H, O-Z)
	COMMON PI, RLG, RLG2, FN, QPISQ
	RLGR=RLG / R
	RLGR2=RLGR ** 2
C===========
C	OLD OMEGA=0.2 FUNCTION
C	OD=0.475 * RLGR2 * RLGR - 0.549 * RLGR2 + 5.752*RLGR - 3.218
C	IF (R .GT. RLG) OD=1.46 * RLGR2 * RLGR + 1.0
C===========
C
C     OMEGA=1
C
	IF(OM.GT.0.9) THEN
	  IF(RLGR.GE.0.8721) THEN
	    OD=0.858988 + 0.0611668*RLGR + 0.306581 * RLGR2 +
     *	   0.417099*RLGR*RLGR2
	  ELSE
	    OD=1.0 + 0.63647*RLGR*RLGR2
	  ENDIF
	ENDIF
C
C     OMEGA GREATER THAN 0.1 BUT LESS THAN 0.9, INPUTTED AS 0.2
C
	IF(OM.GT.0.1 .AND. OM.LE.0.9 .AND. R.LT.2*RLG)
     *     OD=1.162*RLGR2*RLGR-1.786*RLGR2+6.838*RLGR-1.815
	IF(OM.GT.0.1 .AND. OM.LE.0.9 .AND. R.GT.2*RLG)
     *     OD=1.0+2.424*RLGR*RLGR2
	IF(OM.GT.0.1 .AND. OM.LE.0.9 .AND. R.EQ.2*RLG) OD=1.303
C
C     OMEGA VERY SMALL,  INPUTTED AS 0.02
C
	IF(OM.LE.0.1)THEN
	    OD=1.0 + RLGR*RLGR2*344.0/(OM*RLG**3)
	ENDIF
	RETURN
	END

	subroutine strip(strng,nlen,icol)
	character*(*) strng
        do i=nlen,1,-1
          if(strng(i:i).ne.' ') then
            icol=i
            return
          endif
        enddo
	return
	end
