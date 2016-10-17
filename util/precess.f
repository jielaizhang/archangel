* finit-local-zero
      character file*20
      real*8 ra0,dec0,ra,dec,epoch,year

      n=iargc()
      if(n.lt.4) then
        print*, 'enter decimal ra, dec, epoch, year to precess to'
        goto 999
      endif
      pi=2.*acos(0.)
      call getarg(1,file)
      read(file,*) ra0
      call getarg(2,file)
      read(file,*) dec0
      call getarg(3,file)
      read(file,*) epoch
      call getarg(4,file)
      read(file,*) year
      call precess(epoch,year,pi*ra0/180.,pi*dec0/180.,ra,dec)
      print*, 180.*ra/pi,180.*dec/pi
999   end

	SUBROUTINE PRECESS(EPOCH,YEAR,RA0,DEC0,RA,DEC)
* RA0 and DEC0 are the coodinates at EPOCH (radians)
* RA and DEC are the coordinates at YEAR (radians)
	IMPLICIT REAL*8 (A-H,O-Z)
	REAL*8 EPOCH, YEAR, OLDEP /1./, OLDYR /1./
	REAL*8 ROTMAT(3,3), DIR0(3), DIR(3)
	REAL*8 KAPPA, OMEGA, NU
*	IF(YEAR.EQ.OLDYR.AND.EPOCH.EQ.OLDEP) GO TO 10
* Compute precession constants
	TAU = (EPOCH - 1900) * 1E-3
	T = (YEAR - EPOCH) * 1E-3
	KAPPA = T*(23042.53+TAU*(139.73+.06*TAU) +
	1	T*(30.23-.27*TAU) + T*T*18.)*3.1415926535/180/3600
	OMEGA = T*T*(79.27+.66*TAU+.32*T)*3.1415926535/180/3600 + KAPPA
	NU = T*(20046.85+TAU*(-85.33-.37*TAU) +
	1	T*(-42.67-.37*TAU) - T*T*41.80)*3.1415926535/180/3600
	CKA = DCOS(KAPPA)
	SKA = DSIN(KAPPA)
	COM = DCOS(OMEGA)
	SOM = DSIN(OMEGA)
	CNU = DCOS(NU)
	SNU = DSIN(NU)
	ROTMAT(1,1) = CKA*COM*CNU - SKA*SOM
	ROTMAT(2,1) = -SKA*COM*CNU - CKA*SOM
	ROTMAT(3,1) = -COM*SNU
	ROTMAT(1,2) = CKA*SOM*CNU + SKA*COM
	ROTMAT(2,2) = -SKA*SOM*CNU + CKA*COM
	ROTMAT(3,2) = -SOM*SNU
	ROTMAT(1,3) = CKA*SNU
	ROTMAT(2,3) = -SKA*SNU
	ROTMAT(3,3) = CNU
	OLDEP = EPOCH
	OLDYR = YEAR
*	WRITE(6,1000) ROTMAT
1000  FORMAT(' Test... precession constants computed',3F12.5)
10	CONTINUE
	DIR0(1) = DCOS(RA0) * DCOS(DEC0)
	DIR0(2) = DSIN(RA0) * DCOS(DEC0)
	DIR0(3) = DSIN(DEC0)
	DO 20 J = 1,3
	DIR(J) = 0
	DO 20 I = 1,3
20	DIR(J) = DIR(J) + DIR0(I) * ROTMAT(I,J)
	RA = DATAN2(DIR(2),DIR(1))
	IF(RA.LT.0) RA = RA + 2 * 3.1415926535
	DEC = DASIN(DIR(3))
	RETURN
	END
