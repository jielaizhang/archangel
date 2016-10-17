* ELLIPSE FITTING
*
* this is a reverse enginneered verison of Jedrzejewski's original ellipse
* fitting program which is derived from Cawson's GASP PROF package - original
* programming is in CAPS - original comments lead with C - this has been kludged
* to a large amount, however the pixel extraction section (INTERP2) is still
* faster than any C++ version - once called prof.f, now called efit.f (01 Sep 06)

* note there is a 1/2 pixel shift on output for reasons that were never
* clear (integer problem?), so 0.5 is added to X0 and Y0 on output

* this version contains:

* iterative subtraction option
* verbose option
* centering option
* uses cfitsio to read FITS files

C
C  THIS PROGRAM FITS ELLIPSES TO I*2 (now real*4) FRAMES OF ELLIPTICAL GALAXIES
C
	real PIX(4096,4096)                     ! new variables for additions
      real xdata(4096*4096)
      real inner(36),hold(18),output(900,18)
      character file1*100,file2*100,op*2,strng*10,op2*3

      integer status,unit,readwrite,blocksize,naxes(2),bitpix
      integer naxis,pc,gc
      logical simple,extend   ! block of cfitsio variables

	INTEGER NX, NY, NSAMP, ITER, LINOUT     ! original variables
	INTEGER NUM, NBAD, NB4, NB5
	REAL INTENS, POSANG, UNDWT, MINRES, XITER, YY1, YY2, lastn(18)
	REAL MAJFACT, MINIT, MAXIT, RESTRSH, X0, Y0, SLOPE, STDEV, XNUM 
	REAL RESIDS(4), BEST(18), FOURTH(2), PARAM4(1000), PARAM5(1000)
	REAL PIXVAL(200000),ANGLE(200000),MODEL(200000),INIT(18),WT(1000)
	REAL PI, DTOR, RMSRES, GOOD, THRSH, DX, DY, START, WT5(1000)
	DOUBLE PRECISION DELL, DPA, MAXRES, ELLRES, ANGRES, PARRES, PERPRES
	REAL  DELFACT, RAD, ECC, PA, LASTI, LASTR, MINSLOPE
	REAL XBAR, YBAR, THIRD(2), DMIN
	DOUBLE PRECISION  B(5)
	REAL C(2), S(2), B4(1000), B5(1000)
	REAL OUT(18), ONE, FA, MINSAMP, DATA(18)
	EQUIVALENCE (MAJFACT, INIT(4)), (MINIT, INIT(7)), (RMAX, INIT(6)),
     &	(MAXIT, INIT(8)), (DELFACT, INIT(12)), (RESTRSH, INIT(11)),
     &	(UNDWT, INIT(17)), (MINSLOPE, INIT(3)), (DMIN, INIT(5))
	EQUIVALENCE (RAD, DATA(4)), (X0, DATA(15)), (Y0, DATA(16)),
     &	(INTENS, DATA(1)), (STDEV, DATA(2)), (SLOPE, DATA(3)),
     &	(RMSRES, DATA(5)), (XITER, DATA(7)), (XNUM, DATA(8)),
     &	(RESIDS(1), DATA(9)), (ECC, DATA(13)), (PA, DATA(14))
	COMMON /DIMS/ NX, NY
	COMMON /SAMPS/ NSAMP

C  INITIALISE VARIOUS CONTROL PARAMETERS

      n=iargc()              ! command line read
      call getarg(1,op)
      call getarg(2,file1)
      call getarg(3,file2)
      if(file2(1:1)=='-') then  ! forgot to give an output file name
        file2='junk.prf'
        print*, 'output to junk.prf'
      endif

      if((op.eq.'-h ').or.(op(1:1).ne.'-')  ! do the std help
     *   .or.(file1=='').or.(file2=='')) then
        print*, ' '
        print*, 'Usage: efit option file_name output_file other_ops'
        print*, ' '
        print*, 'Options: -h = this mesage'
        print*, '         -v= output each iteration'
        print*, '         -q = quiet'
        print*, ' '
        print*, 'Other options include:'
        print*, '         -xy = use new xc and yc'
        print*, '         -rx = max radius for fit'
        print*, '         -sg = deletion sigma (0=no dets)'
        print*, '         -ms = min slope (-0.5)'
        print*, '         -rs = stopping radius'
        print*, '         -st = starting radius'
        print*, ' '
        print*, 'when deleting, output to file.jedsub'
        goto 9999
      endif

	ONE = 1.0
	INIT(18) = 1.0  ! init array obsolete as fit parameters no longer
	FA = 0.0        ! written out
	IINT = 1
	LINOUT = 0
	PI = 3.14159265359
	DTOR = PI/180.0
* note, g77 on some systems (like Mac OS X) needs zero initalization
	LASTI = 0.0
	LASTR = 0.0
      SUMX = 0.0
      SUMY = 0.0
      SUM = 0.0
      istart=0 ! flag the starting place

      status=0
      call ftgiou(unit,status)
      call ftopen(unit,file1,readwrite,blocksize,status)
      call ftghpr(unit,3,simple,bitpix,naxis,naxes,pc,gc,extend,status)
      nx=naxes(1)
      ny=naxes(2) ! data in xdata, nx & ny are array size
      x=-1.
      nullval=sqrt(x)
      call ftgpve(unit,1,1,nx*ny,nullval,xdata,anynull,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)

      do j=1,ny
        do i=1,nx
          pix(i,j)=xdata(i+nx*(j-1)) ! pack it into (x,y)
        enddo
      enddo

* std init parameters

      x0=nx/2       ! if x0 & y0 not given
      y0=ny/2
      ecc=0.1       ! start with a near circle
      pa=10.*dtor
	MINSLOPE=-0.5 ! shallowest slope for posn determination
	MAJFACT=1.1   ! ratio between successive major axes
	DMIN=1.0      ! min distance for prof operation
	RMAX=100.     ! max distance for prof operation
	MINIT=8       ! minimum number of iterations
	MAXIT=30      ! maximum number of iterations
	DELFACT=0.2   ! minimum fraction of ellipse inside frame
	RESTRSH=0.04  ! maximum residual factor
	UNDWT=0.      ! weight for undetermined points
	start=5.      ! starting sampling radius
	xsig=4.       ! deletion sigma
      rstop=nx/2.   ! minimum fit radius (combined with minslope)
      nfile=0       ! number of lines (for sorting at end)

      if(n > 3) then ! read through options in cmd line
        loop=3
        do while (loop < n)
          loop=loop+1
          call getarg(loop,op2)
          if(op2 == '-xy') then
            loop=loop+1
            call getarg(loop,strng)
            read(strng,*) x0
            loop=loop+1
            call getarg(loop,strng)
            read(strng,*) y0
          endif
          if(op2 == '-ms') then
            loop=loop+1
            call getarg(loop,strng)
            read(strng,*) minslope
          endif
          if(op2 == '-sg') then
            loop=loop+1
            call getarg(loop,strng)
            read(strng,*) xsig
          endif
          if(op2 == '-st') then
            loop=loop+1
            call getarg(loop,strng)
            read(strng,*) start 
          endif
          if(op2 == '-rs') then
            loop=loop+1
            call getarg(loop,strng)
            read(strng,*) rstop
          endif
          if(op2 == '-rx') then
            loop=loop+1
            call getarg(loop,strng)
            read(strng,*) rmax
          endif
        enddo
      endif

*      write(4,'(18(1pe12.4))') x0,y0,ecc,pa,MINSLOPE,MAJFACT,DMIN,RMAX,
*     *   MINIT,MAXIT,DELFACT,RESTRSH,UNDWT,start,sig,0.,0.,0.

C  AND WRITE THE CONTROL PARAMETERS TO THE FIRST RECORD OF PROFILES FILE

160   xlast=start
      do i=19,36
        inner(i)=init(i-18)
      enddo

1000	RAD = START

C  WRITE IMAGE PARAMETERS AND STARTING RADIUS TO RECORD 2 OF PROFILES FILE

*	WRITE (4,*) FA, FA, FA, RAD, FA, FA, FA, FA, FA, FA, FA, FA,
*     &	ECC, PA, X0, Y0, FA, ONE

C  TRAP THIS ERROR

1050	IF (MAJFACT .EQ. 0) GOTO 996
 	RAD = RAD/MAJFACT

C  NEXT LINE - NEW RADIUS

       if(op.eq.'-v') then
	write(*,*) ' '
	print*, '   #    Inten (A)  RMS   Slope     Rad     XC   ',
     *         '   YC    Ecc    PA   num  A'
	write(*,*) ' '
       endif
 1100	LINOUT = LINOUT + 1

C  NOW HAVE ENOUGH POINTS TO WORK OUT THE X AND Y CENTRE

	IF (LINOUT .EQ. 11) THEN
*	    ILINE = 2
*      sumx and sumy now done as fit is made
*	    SUMX = 0.0
*	    SUMY = 0.0
*	    SUM = 0.0
*	    DO I = 1, 8
*		ILINE = ILINE + 1
*		READ (4'ILINE, ERR=274) (IMAG(J), J = 1, 18)
*		SUMX = SUMX + IMAG(15)
*		SUMY = SUMY + IMAG(16)
*		SUM = SUM + 1.0
*	    END DO
	    XBAR = SUMX/SUM
	    YBAR = SUMY/SUM
*	    print *, 'Mean X & Y Positions are:'
*	    print *, 'X0 = ', XBAR,'   Y0 = ', YBAR
*         print*, sumx,sum,sumy,sum
	END IF

C  NEW RADIUS

	RAD = RAD*MAJFACT

C  WE STOP HERE

	IF (RAD .LT. 0.1) GOTO 999
	IF (RAD .GT. rstop) THEN
	    LINOUT = LINOUT - 1
       if(op.eq.'-v') then
 	    print *, 'Going back to start & working inwards'
	    print*, ' '
       endif
	    RAD = START
	    MAJFACT = 1.0/MAJFACT

C  READ STARTING PARAMETERS

          do i=1,18
            data(i)=inner(i)
          enddo
	    DATA(14) = DATA(14)*DTOR

C  AND CONTROL PARAMETERS

          do i=1,18
            init(i)=inner(i+18)
          enddo
	    MAJFACT = 1.0/MAJFACT
	    GO TO 1100
	END IF
	NB4 = 0
	NB5 = 0
	NSAMP = INT (2*PI*RAD)
	MINRES = 10000.0

C  INITIALISE BEST ARRAY

	DO I = 1, 18
	    BEST(I) = 0.0
	END DO

C  SET NO OF SAMPLES IN SAMPLING ELLIPSE

	IF (NSAMP .LE. 40) NSAMP = 40
	IF (RAD .GE. 20.0) NSAMP = 120

C  AND THE MINIMUM ACCEPTABLE NO TO ATTEMPT A FIT

	MINSAMP = NSAMP*DELFACT
	ITER = 0
	NUM = 0
	IF (RAD .LT. DMIN) GOTO 999

C  NEW ITERATION

 150	ITER = ITER + 1
	XITER = ITER
	YY1 = 10000000.0
	YY2 = 0.0

C  DO AN ITERATION

      if(rad < 20) then         
        if(xsig.eq.0) then
          xxx=0.
        else
          xxx=b(1)+2.*xsig*rmsres
        endif
        csig=rmsres
      else
        if(xsig.eq.0) then
          xxx=0.
        else
          xxx=b(1)+xsig*csig
          if(b(1).eq.0) xxx=lasti+xsig*csig
        endif
        csig=rmsres
      endif

* deletions off for these conditions

      if(rad.le.10 .or. best(1).eq.0 .or. slope < -0.5) then
        jter=0
        xxx=0.
      else
        jter=iter
      endif

* test for wild PA change

      if(abs(pa/dtor-best(14)) .gt. 90. .and. best(14) .ne. 0.
     *   .and. iter > 5) then
        if(op.eq.'-v') then
          print*, 'adjusting wild PA swing',abs(pa/dtor-best(14))
        endif
        pa=best(14)*dtor
      endif

* test for wild eccentricity change

      if(abs(ecc-best(13)) .gt. 0.25 .and. best(13) .ne. 0.
     *   .and. iter > 5) then
        if(op.eq.'-v') then
          print*, 'adjusting wild eccentricity swing',abs(ecc-best(13))
        endif
        ecc=best(13)
      endif

C      if(rad.gt.18.and.rad.lt.22) then
C        print*, '1st',xxx,jter,csig,majfact
C      endif

	CALL NEWIT(PIX,NX,NY,DATA,MAJFACT,ANGLE,PIXVAL,xxx,jter,csig)

C      if(rad.gt.18.and.rad.lt.22) then
C        ndum=0 ; nnan=0
C        do lara=1,250
C          if(pixval(lara).eq.0.) exit
C          if(pixval(lara).eq.pixval(lara)) then
C            ndum=ndum+1
C          else
C            nnan=nnan+1
C          endif
C        enddo
C        print*, 'out of newit list',ndum,nnan
C      endif

* csig is really sigma around ellipse pixels, used for deleting

      if(maxit.eq.1) then ! fitting has stopped, max deletions
        itest=0
        do lara=1,100000
          if(pixval(lara) == 0.) exit
          if(pixval(lara) == pixval(lara)) itest=itest+1
        enddo 
        if(itest < 5) goto 999
        CALL ANALYSE (ANGLE, PIXVAL, UNDWT, B, STDEV, NUM)
        if(rad < 20) then         
          if(xsig.eq.0) then
            xxx=0.
          else
            xxx=b(1)+2.*xsig*rmsres
          endif
          csig=rmsres
        else
          if(xsig.eq.0) then
            xxx=0.
          else
            xxx=b(1)+xsig*csig
            if(b(1).eq.0) xxx=lasti+xsig*csig
          endif
        endif
        if(rad.le.10 .or. best(1).eq.0 .or. slope < -0.5) then
          jter=0
          xxx=0.
        else
          jter=iter
        endif
        CALL NEWIT(PIX,NX,NY,DATA,MAJFACT,ANGLE,PIXVAL,xxx,10,csig)
      endif

 400	CONTINUE

C  AND ANALYSE THE INTENSITY STRING

	CALL ANALYSE (ANGLE, PIXVAL, UNDWT, B, STDEV, NUM)
	XNUM = NUM

C  NOT ENOUGH SAMPLED POINTS TO ATTEMPT A FIT

      IF (NUM .LT. MINSAMP) THEN
        lastn(4)=rad
        xxx=0.
        jter=0
        CALL NEWIT(PIX,NX,NY,lastn,MAJFACT,ANGLE,PIXVAL,xxx,jter,csig)
        CALL ANALYSE (ANGLE, PIXVAL, UNDWT, B, STDEV, NUM)
        LINOUT = LINOUT - 1
        if(op.eq.'-v') then
          print *, 'Not enough galaxy to work on'
          WRITE (*,991) ITER,B(1),RMSRES,SLOPE,RAD,X0,Y0,ECC,POSANG,num
          print*, ' '
          print*, '   #    Inten (B)  RMS   Slope     Rad     XC   ',
     *            '   YC    Ecc    PA   num  B'
          print*, ' '
        endif
	  OUT(1) = B(1)
	  OUT(2) = THIRD(1)/SLOPE/RAD
	  OUT(3) = SLOPE
	  OUT(4) = RAD
	  OUT(5) = RMSRES
	  OUT(6) = FOURTH(1)/SLOPE/RAD
	  OUT(7) = ITER
	  OUT(8) = NUM
	  OUT(9) = RESIDS(1)
	  OUT(10) = RESIDS(2)
	  OUT(11) = RESIDS(3)
	  OUT(12) = RESIDS(4)
	  OUT(13) = ECC
	  OUT(14) = POSANG
	  OUT(15) = X0
	  OUT(16) = Y0
	  OUT(17) = FOURTH(2)/SLOPE/RAD
	  OUT(18) = THIRD(2)/SLOPE/RAD
        nfile=nfile+1
        do j=1,18
          output(nfile,j)=out(j)
        enddo

C  TEST TO SEE WHETHER WE ARE NEAR THE EDGE OF THE FRAME

        IF (MAJFACT .LE. 1.0) GOTO 1100
        BMIN = RAD*(1.0 - ECC)
        IF (BMIN .GT. X0 .OR. BMIN .GT. Y0) GOTO 750
        IF (BMIN .GT. (NX - X0) .OR. BMIN .GT. (NY - Y0)) GOTO 750

*       if radius > rstop must be near edge, just go back to start and do inner
        if((rad > rstop .and. rstop .ne. 0.) .or. (num < 5)) goto 750
        GOTO 1100

C  IF SO, INVERT MAJFACT AND GO BACK THE STARTING RADIUS

750     if(op.eq.'-v') then
          print *, 'Going back to start & working inwards'
	    print*, ' '
        endif
	  RAD = START
	  MAJFACT = 1.0/MAJFACT

C  READ STARTING PARAMETERS

*	    READ (4'3) (DATA(J), J = 1, 18)
        do i=1,18
          data(i)=inner(i)
        enddo
	  DATA(14) = DATA(14)*DTOR

C  AND CONTROL PARAMETERS

*	    READ (4'1) (INIT(J), J = 1, 18)
        do i=1,18
          init(i)=inner(i+18)
        enddo
	  MAJFACT = 1.0/MAJFACT
	  GO TO 1100
	END IF

C  WORK OUT 'MODEL' INTENSITY DISTRIBUTION THAT IS THE BEST FIT

	DO I = 1, NSAMP
	    DO L = 1, 2
		C(L) = COS (L*ANGLE(I))
		S(L) = SIN (L*ANGLE(I))
	    END DO
	    IF(PIXVAL(I).LT.YY1.AND.PIXVAL(I).NE.0) YY1 = PIXVAL(I)
	    IF(PIXVAL(I).GT.YY2.AND.PIXVAL(I).NE.0) YY2 = PIXVAL(I)
	    MODEL(I)=B(1)+B(2)*C(1)+B(3)*S(1)+B(4)*C(2)+B(5)*S(2)
	END DO

C  AND WORK OUT THE RMS DEVIATION OF OBSERVED INTENSITY SAMPLES FROM THIS

	CALL RMSDEV (MODEL, PIXVAL, RMSRES, GOOD)
	INTENS = B(1)
	POSANG = PA / DTOR
	NBAD = NSAMP - NUM

C  WRITE OUT THE INFO FOR THIS ITERATION IN DEMO MODE

       if(op.eq.'-v') then
	WRITE (*,991) ITER,B(1),RMSRES,SLOPE,RAD,X0,Y0,ECC,POSANG,num
       endif
991	FORMAT(I4, F11.3, F8.2, F10.1,f7.2,2F8.2, F6.3, F7.2,3i7)
992	FORMAT(I4,'>', F10.3, F8.2, F10.1,f7.2,2F8.2, F6.3, F7.2,3i7)
993	FORMAT(I4,'*', F10.3, F8.2, F10.1,f7.2,2F8.2, F6.3, F7.2,3i7)

C  EQUATE RESIDUALS

	PARRES = DABS (B(2))
	PERPRES = DABS (B(3))
	RESIDS(1) = B(2)
	RESIDS(2) = B(3)
	ANGRES = DABS (B(5))
	RESIDS(4) = B(5)
	ELLRES = DABS (B(4))
	RESIDS(3) = B(4)

C  FIND MAXIMUM RESIDUAL

	MAXRES = DMAX1 (PARRES, PERPRES, ANGRES, ELLRES)

C  IF THIS IS THE BEST SO FAR, UPDATE BEST STRING

	IF (MAXRES .LT. MINRES) THEN
	    DO I = 1, 18
		BEST(I) = DATA(I)
	    END DO
	    BEST(14) = BEST(14)/DTOR
	    BEST(2) = 0.0
	    BEST(6) = 0.0
	    BEST(17) = 0.0
	    BEST(18) = 0.0
	    MINRES = MAXRES
	END IF

C  SET THRESHOLD

	THRSH = RESTRSH*RMSRES
	BEST(7) = -1.0*ITER

C  IF MAX. RESIDUAL BETTER THAN THIS AND ENOUGH ITERATIONS HAVE BEEN DONE

	IF (MAXRES .LT. THRSH .AND. ITER .GE. MINIT) THEN

C  WRITE OUT TO THE TERMINAL THE ELLIPSE PARAMETERS

       if(op.eq.'-v') then
	    WRITE (*, 992) ITER, B(1), RMSRES, SLOPE, RAD, X0, Y0, ECC, 
     *                     PA / DTOR,num
	print*, ' '
	print*, '   #    Inten (B)  RMS   Slope     Rad     XC   ',
     *         '   YC    Ecc    PA   num  C'
	print*, ' '
       endif
      if(istart.eq.0) then
	  do j=1,18
	    inner(j)=best(j)
	  enddo
        istart=1
      endif

C  WORK OUT 3RD AND 4TH HARMONICS

	    CALL HARMONIC (ANGLE, PIXVAL, NSAMP, 3, THIRD)
	    CALL HARMONIC (ANGLE, PIXVAL, NSAMP, 4, FOURTH)
	    OUT(1) = B(1)
	    LASTI = B(1)
	    OUT(2) = THIRD(1)/SLOPE/RAD
	    OUT(3) = SLOPE

C  IF SLOPE IS TOO SMALL ON THE OUTSIDE OF THE GALAXY

	    OUT(4) = RAD
	    LASTR = RAD
	    OUT(5) = RMSRES
	    OUT(6) = FOURTH(1)/SLOPE/RAD
	    OUT(7) = ITER
	    OUT(8) = NUM
	    OUT(9) = RESIDS(1)
	    OUT(10) = RESIDS(2)
	    OUT(11) = RESIDS(3)
	    OUT(12) = RESIDS(4)
	    OUT(13) = ECC
	    OUT(14) = POSANG
	    OUT(15) = X0
	    OUT(16) = Y0
	    OUT(17) = FOURTH(2)/SLOPE/RAD
	    OUT(18) = THIRD(2)/SLOPE/RAD

	    IF ((SLOPE.GT.MINSLOPE*RMSRES) .and. (rad.ge.rmax)) THEN
		IF (XBAR .GT. 0) THEN
		    X0 = XBAR
		    Y0 = YBAR
		END IF
           if(op.eq.'-v') then
		  print *, 'Keeping ellipse parameters constant now (A)'
	        print*, ' '
            endif
		MAXIT = 1
		MINIT = 1
	    END IF
	    IF (SLOPE .GT. 0.0) SLOPE = -0.001

C  WRITE OUT THE 3RD AND 4TH HARMONICS

*	    WRITE (4'LINOUT) (OUT(J), J = 1, 18)
*         write(4,'(18(1pe12.4))') (out(j),j=1,18)
          nfile=nfile+1
          do j=1,18
            output(nfile,j)=out(j)
          enddo
	    GOTO 1200
	END IF

C  WRITE THE BEST PARAMS OUT TO THE PROFILES FILE

*	WRITE (4'LINOUT) (BEST(J), J = 1, 18)
      do i=1,18
        hold(i)=best(i)
	  lastn(i)=best(i)
      enddo

C  IF MAXIMUM NUMBER OF ITERATION HAVE BEEN PERFORMED

	IF (XITER .GE. MAXIT) THEN
       if(op.eq.'-v') then
	    WRITE (*, 993) ITER,BEST(1),BEST(5),BEST(3),BEST(4),BEST(15),
     &	    BEST(16),BEST(13),BEST(14),num
	print*, ' '
	print*, '   #    Inten (C)  RMS   Slope     Rad     XC   ',
     *         '   YC    Ecc    PA   num  D'
	print*, ' '
       endif
*       write(4,'(18(1pe12.4))') (best(j),j=1,18)
        nfile=nfile+1
        do j=1,18
          output(nfile,j)=best(j)
        enddo
        if(istart.eq.0) then
	    do j=1,18
	      inner(j)=best(j)
	    enddo
          istart=1
        endif
        xlast=best(4)
        SUMX = SUMX + hold(15)
        SUMY = SUMY + hold(16)
        SUM = SUM + 1.0
	    SLOPE = BEST(3)
	    RMSRES = BEST(5)
	    IF ((SLOPE.GT.MINSLOPE*RMSRES) .and. (rad.ge.rmax)) THEN
		IF (XBAR .GT. 0) THEN
		    X0 = XBAR
		    Y0 = YBAR
		END IF
       if(op.eq.'-v') then
		print *, 'Keeping ellipse parameters constant now (B)'
	      print*, ' '
       endif
		ECC = OUT(13)
		PA = OUT(14) * DTOR
		MAXIT = 1
		MINIT = 1
	    END IF
	    LASTI = BEST(1)
	    LASTR = BEST(4)
	    GOTO 1200
	END IF
	IF (SLOPE .GT. -0.1) SLOPE = -0.1

C  TEST FOR WHICH RESIDUAL IS LARGEST

	IF (DABS (PARRES/MAXRES -1.0) .LT. 0.0001) GOTO 501
	IF (DABS (PERPRES/MAXRES -1.0) .LT. 0.0001) GOTO 502
	IF (DABS (ANGRES/MAXRES -1.0) .LT. 0.0001) GOTO 510

C  ALTER ELLIPTICITY

 500	NB4 = NB4 + 1

C  USE LAST 4 RESIDUALS AND FIT A LINE TO CALCULATE INTERCEPT

	IF (NB4 .GT. 4) THEN
	    if(nb4.gt.20) nb4=20
	    NC4 = MOD (NB4, 4) + 1
	    NVAL4 = 4
	ELSE
	    NC4 = NB4
	    NVAL4 = NB4
	END IF
	B4(NC4) = B(4)
	PARAM4(NC4) = ECC
	WT(NC4) = 1.0
	IF (NVAL4 .GT. 1) THEN
	    CALL FITLINE (B4, PARAM4, WT, NVAL4, AA, ECC)

C  UNLESS THIS IS THE FIRST TRY

	ELSE
	    DELLBYDB4 = -2.0*(1.0 - ECC)/RAD/SLOPE
	    DELL = DELLBYDB4*B(4)
	    ECC = ECC + DELL
	END IF

C  IF ELLIPTICITY BECOMES <0, ROTATE POSITION ANGLE BY 90 DEGREES INSTEAD

	IF (ECC .LT. 0.0) THEN
	    ECC = -ECC
	    PA = PA + PI/2.0
	    IF (PA .GT. PI) PA = PA - PI
	END IF

C  CANT LET THE ELLIPTICITY GET AS LARGE AS 0.9, CAN WE?

	IF (ECC .GT. 0.9) ECC = best(13)
	GOTO 150

C  MOVE PARALLEL TO THE MAJOR AXIS

 501	DX = -B(2)/SLOPE*COS(PA)
	DY = -B(2)/SLOPE*SIN(PA)
	DPOS2 = DX*DX + DY*DY

C  IF THE ELLIPSE TRIES TO FALL OFF THE GALAXY

	IF (DPOS2 .GT. 0.4*RAD*RAD) THEN
	    DXNEW = 0.1*RAD*COS (PA)
	    DX = SIGN (DXNEW, DX)
	    DYNEW = 0.1*RAD*SIN (PA)
	    DY = SIGN (DYNEW, DY)
       if(op.eq.'-v') then
	    print *, 'Position shift is too big'
	    print *, 'Try instead'
	    print *, 'dx = ', DX
	    print *, 'dy = ', DY
	    print*, ' '
       endif
	END IF
	X0 = X0 + DX
	Y0 = Y0 + DY
	GOTO 150

C  MOVE PERPENDICULAR TO THE MAJOR AXIS

 502	DX = B(3)*(1.0 - ECC)/SLOPE*SIN (PA)
	DY = -B(3) * (1.0 - ECC) / SLOPE * COS (PA)
	DPOS2 = DX * DX + DY * DY

C  AGAIN, WE CANT LET THE ELLIPSE FALL OFF THE GALAXY

	IF (DPOS2 .GT. 0.4 * RAD * RAD) THEN
	    DXNEW = 0.1 * RAD * COS (PA)
	    DX = SIGN (DXNEW, DX)
	    DYNEW = 0.1 * RAD * SIN (PA)
	    DY = SIGN (DYNEW, DY)
       if(op.eq.'-v') then
	    print *, 'Try instead'
	    print *, 'dx = ', DX
	    print *, 'dy = ', DY
	    print*, ' '
       endif
	END IF
	X0 = X0 + DX
	Y0 = Y0 + DY
	GOTO 150

C   ALTER THE POSITION ANGLE

 510	NB5 = NB5 + 1
	IF (NB5 .GT. 4) THEN
	    NC5 = MOD (NB5, 4) + 1
	    IF (NC5 .EQ. 0) NC5 = 4
	    NVAL5 = 4
	ELSE
	    NC5 = NB5
	    NVAL5 = NB5
	END IF
	B5(NC5) = B(5)
	WT5(NC5) = 1.0
	PARAM5(NC5) = PA
	IF (NVAL5 .GT. 1) THEN
	    CALL FITLINE (B5, PARAM5, WT5, NVAL5, AA, PA)
	    POSANG = PA / DTOR
	ELSE
	    IF (ECC .EQ. 0) THEN
		GOTO 500
	    END IF
	    IF (ECC .EQ. 2.0) ECC = 0.5
	    DPA=-2.0*B(5)*(1.0-ECC)/RAD/ECC/(2.0-ECC)/SLOPE
	    PA = PA + DPA
	END IF

C  MAKE THE POSITION ANGLE SOMEWHERE BETWEEN -PI AND PI

 520	IF (PA .GT. PI) THEN
	    PA = PA - PI
	    GOTO 520
	END IF
 530	IF (PA .LT. -PI) THEN
	    PA = PA + PI
	    GOTO 530
	END IF
	GOTO 150
 1200	CONTINUE
	GOTO 1100

C  THATS IT, NOW ORDER THE PROFILES FILE IN ORDER OF INCREASING RADIUS

 999	continue

      call dump(output,nfile,file2)

      if(xsig.ne.0) then
        do j=1,ny
          do i=1,nx
            xdata(i+nx*(j-1))=pix(i,j)
          enddo
        enddo

        call ftgiou(unit,status)
        do idot=1,80
          if(file1(idot:idot).eq.'.') exit
        enddo
        call ftopen(unit,file1(1:idot)//'jedsub',1,blocksize,status)
        if(status.eq.0) then
* file was opened;  so now delete it
          call ftdelt(unit,status)
        elseif (status .eq. 103) then
* file doesn't exist, so just reset status to zero and clear errors
          status=0
          call ftcmsg
        else
* there was some other error opening the file; delete the file anyway
          status=0
          call ftcmsg
          call ftdelt(unit,status)
        endif
        call ftfiou(unit,status)
        call ftgiou(unit,status)
        call ftinit(unit,file1(1:idot)//'jedsub',1,status)
        call ftphpr(unit,simple,bitpix,naxis,naxes,0,1,extend,status)
        call ftppre(unit,1,1,nx*ny,xdata,status)
        call ftclos(unit,status)
        call ftfiou(unit,status)
        if(status.gt.0) call printerror(status)
      endif

	GOTO 9999
 1	FORMAT (A)
997    if(op.eq.'-v') then
         print *, 'Error: Sum=0'
       endif
	GOTO 9999
996    if(op.eq.'-v') then
         print *, 'Error: Majfact = 0'
       endif
	GOTO 9999
998    if(op.eq.'-v') then
         print *, 'In batch mode output file must already exist'
       endif
9999	END

C  THIS SUBROUTINE ANALYSES THE PIXVAL AND ANGLE ARRAYS FROM SUBROUTINE
C  NEWIT IN PROGRAM RJNPROF.  OUTPUTS THE ARRAY B

	SUBROUTINE ANALYSE (ANGLE, PIXVAL, UNDWT, B, STDEV, NUM)
	REAL ANGLE(200000), PIXVAL(200000), C(2), S(2)
	REAL MEANINT
	DOUBLE PRECISION A(5,5), B(5)
	INTEGER NUM
	COMMON /SAMPS/ NSAMP

C  INITIALISE A MATRIX AND B VECTOR

	DO I = 1, 5
	    B(I) = 0.0
	    DO J = 1, 5
		A (J, I) = 0.0
	    END DO
	END DO

C  INITIALISE ACCUMULATED SUMS

	SUMSQ = 0.0
	SUMVAL = 0.0
	SUM = 0.0
	NUM = 0

C  WORK OUT MEAN AND STANDARD DEVIATION OF PIXVAL VALUES, AS WELL AS MAX AND
C  MINIMUM

	XMAX1 = -100.0
	XMAX2 = -100.0
	XMIN1 = 100000.0
	XMIN2 = 100000.0
	DO I = 1, NSAMP
	    IF (pixval(i).eq.pixval(i)) THEN
		XVAL = PIXVAL(I)
		IF (XVAL .GT. XMAX1) THEN
		    XMAX1 = XVAL
		    NMAX1 = I
		ELSE
		    IF (XVAL .GT. XMAX2) THEN
			XMAX2 = XVAL
			NMAX2 = I
		    END IF
		END IF
		IF (XVAL .LT. XMIN1) THEN
		    XMIN1 = XVAL
		    NMIN1 = I
		ELSE
		    IF (XVAL .LT. XMIN2) THEN
			XMIN2 = XVAL
			NMIN2 = I
		    END IF
		END IF
		SUM = SUM + 1.0
		SUMVAL = SUMVAL + PIXVAL(I)
		SUMSQ = SUMSQ + PIXVAL(I)*PIXVAL(I)
	    END IF
	END DO
	IF (SUM .NE. 0.0) THEN
	    MEANINT = SUMVAL/SUM
	    STDEV = SQRT (ABS (SUMSQ/SUM - MEANINT*MEANINT))
	END IF

C  SET HIGHEST 2 AND LOWEST 2 TO ZERO ALSO

      dumnull=-1.
	PIXVAL(NMAX1) = sqrt(dumnull)
	PIXVAL(NMAX2) = sqrt(dumnull)
	PIXVAL(NMIN1) = sqrt(dumnull)
	PIXVAL(NMIN2) = sqrt(dumnull)

C  NOW ANALYSE THE PIXVAL ARRAY TO DETERMINE FIRST AND SECOND HARMONICS

	DO I = 1, NSAMP
	    DO L = 1, 2
		C(L) = COS (L*ANGLE(I))
		S(L) = SIN (L*ANGLE(I))
	    END DO
	    IF (PIXVAL(I) .ne. pixval(i)) THEN
		WEIGHT = UNDWT
		VALUE = MEANINT
	    ELSE
		WEIGHT = 1.0
		VALUE = PIXVAL(I)
		NUM = NUM + 1
	    END IF
	    A(1,1) = A(1,1) + WEIGHT
	    A(1,2) = A(1,2) + C(1)*WEIGHT
	    A(1,3) = A(1,3) + S(1)*WEIGHT
	    A(1,4) = A(1,4) + C(2)*WEIGHT
	    A(1,5) = A(1,5) + S(2)*WEIGHT
	    B(1) = B(1) + VALUE*WEIGHT
	    A(2,1) = A(1,2)
	    A(2,2) = A(2,2) + C(1)*C(1)*WEIGHT
	    A(2,3) = A(2,3) + C(1)*S(1)*WEIGHT
	    A(2,4) = A(2,4) + C(1)*C(2)*WEIGHT
	    A(2,5) = A(2,5) + C(1)*S(2)*WEIGHT
	    B(2) = B(2) + VALUE*C(1)*WEIGHT
	    A(3,1) = A(1,3)
	    A(3,2) = A(2,3)
	    A(3,3) = A(3,3) + S(1)*S(1)*WEIGHT
	    A(3,4) = A(3,4) + S(1)*C(2)*WEIGHT
	    A(3,5) = A(3,5) + S(1)*S(2)*WEIGHT
	    B(3) = B(3) + VALUE*S(1)*WEIGHT
	    A(4,1) = A(1,4)
	    A(4,2) = A(2,4)
	    A(4,3) = A(3,4)
	    A(4,4) = A(4,4) + C(2)*C(2)*WEIGHT
	    A(4,5) = A(4,5) + C(2)*S(2)*WEIGHT
	    B(4) = B(4) + VALUE*C(2)*WEIGHT
	    A(5,1) = A(1,5)
	    A(5,2) = A(2,5)
	    A(5,3) = A(3,5)
	    A(5,4) = A(4,5)
	    A(5,5) = A(5,5) + S(2)*S(2)*WEIGHT
	    B(5) = B(5) + VALUE*S(2)*WEIGHT
	END DO

C  SOLVE THE 5 X 5 SET OF EQUATIONS

	CALL LINSOLVE (A, B, 5)

C  AND GO HOME

	RETURN
	END

C  THIS SUBROUTINE FITS A STRAIGHT LINE TO THE X AND Y VALUES USING WEIGHT
C  ARRAY WEIGHT.   NPTS POINTS, RETURNED SLOPE A AND INTERCEPT B

	SUBROUTINE FITLINE(X, Y, WEIGHT, NPTS, A, B)
	REAL X(1000), Y(1000), WEIGHT(1000)
	REAL A, B, SUM, SUMX, SUMY, SUMXX, SUMXY, SUMYY, DELTA
	INTEGER NPTS
	SUM = 0.0
	SUMX = 0.0
	SUMY = 0.0
	SUMXX = 0.0
	SUMXY = 0.0
	SUMYY = 0.0
	DO I = 1,NPTS
	    SUM = SUM + WEIGHT(I)
	    SUMX = SUMX + WEIGHT(I)*X(I)
	    SUMY = SUMY + WEIGHT(I)*Y(I)
	    SUMXX = SUMXX + WEIGHT(I)*X(I)*X(I)
	    SUMXY = SUMXY + WEIGHT(I)*X(I)*Y(I)
	    SUMYY = SUMYY + WEIGHT(I)*Y(I)*Y(I)
	END DO
	DELTA = ABS(SUMXX*SUM - SUMX*SUMX)
	IF(DELTA.EQ.0) THEN
	    A = 0.0
	    B = 0.0
	    GOTO 999
	END IF
	A = SUM*SUMXY - SUMX*SUMY
	A = A/DELTA
	B = SUMY*SUMXX - SUMX*SUMXY
	B = B/DELTA
 999	RETURN
	END

	SUBROUTINE HARMONIC(ANGLE,PIXVAL,NSAMP,NHARM,HARMON)
	REAL HARMON(2),ANGLE(200000), PIXVAL(200000)
	DOUBLE PRECISION A(3,3), B(3)
	DO I = 1,3
	    B(I) = 0.
	    DO J = 1,3
		A(J,I) = 0.
	    END DO
	END DO
	DO I = 1,NSAMP
	    IF(pixval(i).eq.pixval(i)) THEN
		CN = COS(NHARM*ANGLE(I))
		SN = SIN(NHARM*ANGLE(I))
		VALUE = PIXVAL(I)
		A(1,1) = A(1,1) + 1.
		A(1,2) = A(1,2) + CN
		A(1,3) = A(1,3) + SN
		B(1) = B(1) + VALUE
		A(2,1) = A(1,2)
		A(2,2) = A(2,2) + CN*CN
		A(2,3) = A(2,3) + CN*SN
		B(2) = B(2) + CN*VALUE
		A(3,1) = A(1,3)
		A(3,2) = A(2,3)
		A(3,3) = A(3,3) + SN*SN
		B(3) = B(3) + SN*VALUE
	    END IF
	END DO
	CALL LINSOLVE(A,B,3)
	HARMON(2) = B(3)
	HARMON(1) = B(2)
	RETURN
	END

	SUBROUTINE INTERP (DATA, NX, NY, X, Y, VALUE, xint, iter)
	real DATA (4096,4096)
	IX0 = NINT (X)
	IY0 = NINT (Y)
	IF(IX0.LE.1.OR.IY0.LE.1.OR.IX0+1.GE.NX.OR.IY0+1.GE.NY)
     &	then
        dumnull=-1.
        value=sqrt(dumnull)
        return
      endif
	DX1 = 0.5 + X - IX0
	DX2 = 0.5 - X + IX0
	DY1 = 0.5 + Y - IY0
	DY2 = 0.5 - Y + IY0
	A11 = DX2*DY2*DATA (IX0, IY0)
	A12 = DX1*DY2*DATA (IX0+1, IY0)
	A21 = DX2*DY1*DATA (IX0, IY0+1)
	A22 = DX1*DY1*DATA (IX0+1, IY0+1)
	IF ((DATA(IX0,IY0).ne.DATA(IX0,IY0)).OR. 
     *    (DATA(IX0+1,IY0).ne.DATA(IX0+1,IY0)).OR.
     *    (DATA(IX0,IY0+1).ne.DATA(IX0,IY0+1)).OR. 
     *    (DATA(IX0+1,IY0+1).ne.DATA(IX0+1,IY0+1))) THEN
          dumnull=-1.
 	    VALUE = sqrt(dumnull)
	    RETURN
	ELSE
	    VALUE = A11 + A12 + A21 + A22
          if(xint.gt.0..and.iter.ge.10.and.value.ge.xint) then
*            print*, 'killing in INTERP',xint,data(ix0,iy0),value,ix0,iy0,iter
             dumnull=-1.
            value=sqrt(dumnull)
            tmp=data(ix0,iy0)
            ik=ix0
            jk=iy0
            if(data(ix0+1,iy0).gt.tmp) then
              tmp=data(ix0+1,iy0)
              ik=ix0+1
            endif
            if(data(ix0,iy0+1).gt.tmp) then
              tmp=data(ix0,iy0+1)
              ik=ix0
              jk=iy0+1
            endif
            if(data(ix0+1,iy0+1).gt.tmp) then
              ik=ix0+1
              jk=iy0+1
            endif
*            data(ik,jk)=sqrt(-1.)
*            call kill_pix(data,nx,ny,ik,jk)
          endif
	END IF
	RETURN
	END

	SUBROUTINE INTERP2(DATA,NX,NY,NBX,NBY,X,Y,DIAG,VALUE,AREA,BAD,
     *                   xint,iter,out_sig)

C  DATA=DATA ARRAY
C  NX, NY = DIMENSIONS OF PIXEL ARRAY
C  NBX,NBY = SIZE OF BOX TO INCLUDE ELLIPSE SEGMENT
C  X,Y = ARRAYS OF X & Y COORDINATES OF SEGMENT CORNERS (DIM=5)
C  DIAG = LOGICAL VARIABLE FOR DIAGNOSTICS
C  VALUE = VALUE OF INTERPOLATED INTENSITY
C  AREA = AREA OF SEGMENT CALCULATED FROM SUMMING PIXEL CONTRIBUTIONS
C  BAD = AREA THAT IS 'BAD' IE OUTSIDE FRAME OR = 0

	real DATA (4096,4096)
	INTEGER N (0:8, 600, 600)

C  N HAS THE NUMBER OF EACH CROSSING POINT: IE FOR PIXEL (J,I), THE
C  CROSSING POINT #R IS N(R,J,I)

	LOGICAL DIAG, LBAD
	INTEGER NCROS(600,600),NIN(600,600),NCORN(600,600),NUMC(600,600)

C  NCROS(J,I) IS THE NUMBER OF CROSSING POINTS IN PIXEL (J,I)
C  NIN(J,I) IS THE NUMBER OF PIXEL CORNERS INSIDE SEGMENT IN (J,I)
C  NCORN(J,I) IS THE NUMBER OF ENCLOSED SEGMENT CORNERS IN (J,I)
C  NUMC(J,I) IS THE NUMBER OF THE CORNER IN (J,I) (1-4)

C  XCROS & YCROS ARE THE X&Y COORDS OF CROSSING POINTS

	REAL X(5), Y(5), C(4), M(4), YCROS(0:400), XCROS(0:400)
      real pix(200000)

C  INITIALISE ARRAYS
      iflag=0

 10	DO I = 1, NBY
	    DO J = 1, NBX
		NIN (J, I) = 0
		NCROS (J, I) = 0
		NCORN (J, I) = 0
		NUMC (J, I) = 0
	    END DO
	END DO

C INITIALISE VARIABLES

	AREA = 0.0
	VALUE = 0.0
	BAD = 0.0
	XM = 100000.0

C  FIND XM = XMIN

	DO I = 1, 4
	    IF (X(I) .LT. XM) THEN
		XM = X(I)
	    END IF
	END DO

C  print X&Y COORDS OF CORNERS IF IN DIAG MODE

	IF (DIAG) THEN
	    print *, (X(J), J = 1, 4), (Y(J), J = 1, 4)
	END IF

C  WORK OUT SLOPES & INTERCEPTS FOR SEGMENT EDGES

	DO I = 1, 4
	    IF (X(I + 1) .EQ. X(I)) THEN
		DENOM = 100000000.0
	    ELSE
		DENOM = 1.0 / (X(I + 1) - X(I))
	    END IF
	    M(I)=(Y(I+1)-Y(I))*DENOM
	    C(I)=(Y(I)*X(I+1)-X(I)*Y(I+1))*DENOM
	END DO

C  print OUT SLOPES & INTCPTS IF DIAG

	IF (DIAG) THEN
	    print *, (M(J), J = 1, 4)
	    print *, (C(J), J = 1, 4)
	END IF
	NUM = 0

C  LOOK FOR ARRAY BOUNDS OUT OF RANGE

	DO I = 1, 4
	    IX = INT (X(I)) - INT (XM) + 1
	    IF (IX .LT. 1) GOTO 999
	    IF (IX .GT. NBX) GOTO 999
	    IY = INT (Y(I)) - INT (Y(1)) + 1
	    IF (IY .LT. 1) GOTO 999
	    IF (IY .GT. NBY) GOTO 999
	    NCORN (IX, IY) = NCORN (IX, IY) + 1
	    NUMC (IX, IY) = I
	END DO

C  WORK OUT CROSSING POINTS

C  START BY ORDERING X PAIRS INTO MAX & MIN OF 2

	DO I = 1, 4
	    IF (X(I) .GT. X(I + 1)) THEN
		XMAX = X(I)
		XMIN = X(I + 1)
	    ELSE
		XMAX = X(I + 1)
		XMIN = X(I)
	    END IF

C  NO OF X CROSSING PTS IS DIFF OF INTEGERISED XMAX & XMIN

	    NPTS = INT (XMAX) - INT (XMIN)

C  X CROSSING PTS ARE THEN FLOAT(INTEGERISED X VALUES BET. XMIN&MAX)
C  Y CROSSING ARE SOLNS OF LINEAR EQUNS FOR EDGES WITH THOSE X VALS
C  IX & IY ARE COORDS IN 'LOCAL' BOX OF DIMENSNS NBX,NBY
C  NCROS(IX,IY) INCREMENTED FOR XING PT IN THAT PIXEL
C  & N(NCROS(IX,IY),IX,IY) STORED

	    DO J = 1, NPTS
		NUM = NUM + 1
		IX = INT (XMIN) + J
		XCROS(NUM) = DFLOAT (IX)
		YCROS(NUM) = M(I) * XCROS(NUM) + C(I)
		IY = INT (YCROS(NUM)) + 1 - INT (Y(1))
		IX = IX - INT (XM)
		NCROS (IX, IY) = NCROS (IX, IY) + 1
		IF(NCROS(IX,IY).LT.0.OR.NCROS(IX,IY).GT.8.OR.IX
     &		.GT. 600 .OR. IY .GT. 600) GOTO 999
		N (NCROS (IX, IY), IX, IY) = NUM
		NCROS (IX + 1, IY)=NCROS(IX+1,IY)+1
		N (NCROS (IX + 1, IY), IX + 1, IY) = NUM
	    END DO

C  DO THE SAME FOR Y CROSSING POINTS

	    IF (Y(I + 1) .GT. Y(I)) THEN
		YMAX = Y(I + 1)
		YMIN = Y(I)
	    ELSE
		YMAX = Y(I)
		YMIN = Y(I + 1)
	    END IF
	    NPTS = INT (YMAX) - INT (YMIN)
	    DO J = 1, NPTS
		NUM = NUM + 1
		IY = INT (YMIN) + J
		YCROS(NUM) = DFLOAT (INT (YMIN) + J)
		IF (M(I) .EQ. 0.0) M(I) = 1.0E-8
		XCROS(NUM) = (YCROS(NUM) - C(I)) / M(I)
		IX = INT (XCROS(NUM)) + 1 - INT (XM)
		IY = IY - INT (Y(1))
		NCROS (IX, IY) = NCROS (IX, IY) + 1
		N (NCROS (IX, IY), IX, IY) = NUM
		NCROS (IX, IY + 1) = NCROS (IX, IY + 1) + 1
		N (NCROS (IX, IY + 1), IX, IY + 1) = NUM
	    END DO
	END DO

C    FOR EACH PIXEL, WORK OUT IF THE CORNERS ARE INSIDE SEGMENT
C   INCREMENT NIN(IX,IY) FOR THE 4 PIXELS WHICH HAVE THAT CORNER IN
C   COMMON

	NCORNTOT = 0
	DO I = 1, NBY - 1
	    IY = NBY - I
	    YC = FLOAT (IY + INT (Y(1)))
	    DO J = 1, NBX - 1
		IX = NBX - J
		XC = FLOAT (IX + INT (XM))
		IF (ABS (M(1)) .LT. 1.0) THEN
		    YIN = M(1) * XC + C(1)
666         format(a,i3,4f6.1,8f8.1)
		    IF (YC .LT. YIN) GOTO 50
		ELSE
		    XIN = (YC - C(1)) / M(1)
		    IF (XC .LT. XIN) GOTO 50
		END IF
		IF (ABS (M(2)) .LT. 1.0) THEN
		    YIN = M(2) * XC + C(2)
		    IF (YC .GT. YIN) GOTO 50
		ELSE
		    XIN = (YC - C(2)) / M(2)
		    IF (XC .LT. XIN) GOTO 50
		END IF
		IF (ABS (M(3)) .LT. 1.0) THEN
		    YIN = M(3) * XC + C(3)
		    IF (YC .GT. YIN) GOTO 50
		ELSE
		    XIN = (YC - C(3)) / M(3)
		    IF (XC .GT. XIN) GOTO 50
		END IF
		IF (ABS (M(4)) .LT. 1.0) THEN
		    YIN = M(4) * XC + C(4)
		    IF (YC .LT. YIN) GOTO 50
		ELSE
		    XIN = (YC - C(4)) / M(4)
		    IF (XC .GT. XIN) GOTO 50
		END IF
		NIN (IX, IY) = NIN (IX, IY) + 1
		NIN (IX + 1, IY) = NIN (IX + 1, IY) + 1
		NIN (IX, IY + 1) = NIN (IX, IY + 1) + 1
		NIN (IX + 1, IY + 1) = NIN (IX + 1, IY + 1) + 1
		NCORNTOT = NCORNTOT + 1
 50	    END DO
	END DO

	IF (NCORNTOT .EQ. 0) THEN
	    XSWAP = X(2)
	    X(2) = X(4)
	    X(4) = XSWAP
	    YSWAP = Y(2)
	    Y(2) = Y(4)
	    Y(4) = YSWAP
          iflag=iflag+1
          if(iflag.ge.5) goto 999
	    GOTO 10
	END IF

C  print OUT NIN,NCROS,NCORN IF IN DIAG MODE

	IF (DIAG) THEN
	    print *, 'nin'
	    DO I = NBY, 1, -1
		print '(14I5)', (NIN (J, I), J = 1, NBX)
	    END DO
	    print *, 'ncros'
	    DO I = NBY, 1, -1
		print '(14I5)', (NCROS (J, I), J = 1, NBX)
	    END DO
	    print *, 'ncorn'
	    DO I = NBY, 1, -1
		print '(14I5)', (NCORN (J, I), J = 1, NBX)
	    END DO
	END IF

C  NOW DO THE HARD WORK
C  FOR EACH PIXEL (IX,IY):

      npts=0
	DO I = NBY, 1, -1
	    IY = INT (Y(1)) +  I
	    DO J = NBX, 1, -1
		IX = INT (XM) + J

C  INITILISE VARIABLES

		LBAD = .FALSE.
		DAREA = 0.0
		DINT = 0.0
		DBAD = 0.0
		PIXVAL = 0.0
		IF(IX.LT.2.OR.IX.GT.(NX-1)) LBAD = .TRUE.
		IF(IY.LT.2.OR.IY.GT.(NY-1)) LBAD = .TRUE.
		IF ( .NOT. LBAD) THEN
              if(data(ix,iy).ge.xint.and.iter.ge.10.and.xint.ne.0.) then
*                print*, 'killing in INTERP2',ix,iy,data(ix,iy),xint
                dumnull=-1.
                pixval=sqrt(dumnull)
                call kill_pix(data,nx,ny,ix,iy)
              else
		    PIXVAL = DATA (IX, IY)
                if(pixval.eq.pixval) then
                  npts=npts+1
                  pix(npts)=data(ix,iy)
                endif     
              endif
		    IF (PIXVAL .ne. pixval) LBAD = .TRUE.
		END IF

C  IF ONE OF SEGMENT CORNERS IN INSIDE GOTO 200

		IF (NCORN (J, I) .NE. 0) GOTO 200

C  ELSE

C   CASE OF NCORN=0, NCROS=2, NIN=1   TRIANGLE

		IF (NCROS (J, I) .EQ. 2 .AND. NIN (J, I) .EQ. 1) THEN
		    DX = XCROS(N (1, J, I)) - XCROS(N (2, J, I))
		    DY = YCROS(N (1, J, I)) - YCROS(N (2, J, I))
		    DAREA = ABS (0.5 * DX * DY)
		    CALL SWAP (DAREA, DBAD, LBAD)
		    GO TO 150
		END IF

C  CASE OF NCORN=0, NCROS=0, NIN=0  OUTSIDE

		IF (NCROS (J, I) .EQ. 0 .AND .NIN (J, I) .EQ. 0) THEN
		    GOTO 150
		END IF

C  CASE OF NCORN=0, NIN=4, NCROS=0  ALL INSIDE

		IF (NCROS (J, I) .EQ. 0 .AND. NIN (J, I) .EQ. 4) THEN
		    DAREA = 1.0
		    CALL SWAP (DAREA, DBAD, LBAD)
		    GOTO 150
		END IF

C  CASE OF NCORN=0, NIN=3, NCROS=2  ALL BUT TRIANGLE

		IF (NCROS (J, I) .EQ. 2 .AND. NIN (J, I). EQ. 3) THEN
		    DX = XCROS (N (1, J, I)) - XCROS(N (2, J, I))
		    DY = YCROS (N (1, J, I)) - YCROS(N (2, J, I))
		    DAREA = 1.0 - ABS (0.5 * DX * DY)
		    CALL SWAP (DAREA, DBAD, LBAD)
		    GO TO 150
		END IF

C  CASE OF NCORN=0, NCROS=2, NIN=2  TRAPEZIUM

		IF (NIN (J, I) .EQ. 2 .AND. NCROS (J, I) .EQ. 2) THEN

C  WORK OUT MEAN X VALUE

		    DX1 = XCROS(N(1,J,I))+XCROS(N(2,J,I))
		    DX1 = 0.5*DX1
		    DX1 = DX1 - INT(DX1)

C  & MEAN Y VALUE

		    DY1 = YCROS(N(1,J,I))+YCROS(N(2,J,I))
		    DY1 = 0.5*DY1
		    DY1 = DY1 - INT(DY1)

C  & AREA = MEANX * MEANY

		    DAREA = 2.0*ABS(DX1*DY1)
		    DAREA = MIN(DAREA,(1.-DAREA))

C  NOW WORK OUT WHETHER ITS MAINLY INSIDE OR OUTSIDE

		    XC = IX - 0.5
		    YC = IY - 0.5
		    IF(ABS(M(1)).LT.1.) THEN
			YIN = M(1)*XC + C(1)
			IF(YC.LT.YIN) GOTO 250
		    ELSE
			XIN = (YC - C(1))/M(1)
			IF(XC.LT.XIN) GOTO 250
		    END IF
		    IF(ABS(M(2)).LT.1.) THEN
			YIN = M(2)*XC + C(2)
			IF(YC.GT.YIN) GOTO 250
		    ELSE
			XIN = (YC - C(2))/M(2)
			IF(XC.LT.XIN) GOTO 250
		    END IF
		    IF(ABS(M(3)).LT.1.) THEN
			YIN = M(3)*XC + C(3)
			IF(YC.GT.YIN) GOTO 250
		    ELSE
			XIN = (YC - C(3))/M(3)
			IF(XC.GT.XIN) GOTO 250
		    END IF
		    IF(ABS(M(4)).LT.1.) THEN
			YIN = M(4)*XC + C(4)
			IF(YC.LT.YIN) GOTO 250
		    ELSE
			XIN = (YC - C(4))/M(4)
			IF(XC.GT.XIN) GOTO 250
		    END IF
		    DAREA = 1. - DAREA
 250		    CALL SWAP(DAREA,DBAD,LBAD)
		    GOTO 150
		END IF

C   CASE OF NCORN=0, NCROS=8, NIN=0  ALL BUT 4 TRIANGLES

		IF(NIN(J,I).EQ.0.AND.NCROS(J,I).EQ.8) THEN
		    DAREA = 1.
		    DO K = 1,4
			K2 = 2*K
			DX =  XCROS(K2-1)-XCROS(K2)
			DY = YCROS(K2-1)-YCROS(K2)
			DAREA = DAREA - 0.5*ABS(DX*DY)
		    END DO
		    CALL SWAP(DAREA,DBAD,LBAD)
		    GOTO 150
		END IF

C  CASE OF NCORN=0, NCROS=4, NIN=2  ALL BUT 2 TRIANGLES

		IF(NIN(J,I).EQ.2.AND.NCROS(J,I).EQ.4) THEN
		    DX = XCROS(N(1,J,I))-XCROS(N(2,J,I))
		    DY = YCROS(N(1,J,I))-YCROS(N(2,J,I))
		    DA1 = 0.5*ABS(DX*DY)
		    DX = XCROS(N(3,J,I))-XCROS(N(4,J,I))
		    DY = YCROS(N(3,J,I))-YCROS(N(4,J,I))
		    DA2 = 0.5*ABS(DX*DY)
		    DAREA = 1.-DA1-DA2
		    CALL SWAP(DAREA,DBAD,LBAD)
		    GOTO 150
		END IF

C   CASE OF NCORN=0, NCROS=4, NIN=1  COMPLICATED ONE
C   TRAPEZIUM WITH TRIANGLE TAKEN OUT
C   (ALTERNATIVELY TRAPEZIUM WITH 2 TRIANGLES TAKEN OUT)
C   THIS ONE'S A TRICKY ONE

		IF(NIN(J,I).EQ.1.AND.NCROS(J,I).EQ.4) THEN

C   WORK OUT AREA OF TRAINGLES

		    DX = XCROS(N(1,J,I))-XCROS(N(2,J,I))
		    DY = YCROS(N(1,J,I))-YCROS(N(2,J,I))
		    DA1 = 0.5*ABS(DX*DY)
		    DX = XCROS(N(3,J,I))-XCROS(N(4,J,I))
		    DY = YCROS(N(3,J,I))-YCROS(N(4,J,I))
		    DA2 = 0.5*ABS(DX*DY)

C  NOW WORK OUT WHETHER TO ADD OR SUBTRACT TRIANGLES FROM TRAPEZIUM

		    XSAME = 0.
		    YSAME = 0.
		    DO K = 1,2
			DIFX=XCROS(N(K,J,I))-XCROS(N(3,J,I))
			DIFY=YCROS(N(K,J,I))-YCROS(N(3,J,I))
			IF(ABS(DIFX).LT.0.0001) THEN
			    XSAME = XCROS(N(K,J,I))
			    GOTO 230
			END IF
			IF(ABS(DIFY).LT.0.0001) THEN
			    YSAME = YCROS(N(K,J,I))
			    GOTO 230
			END IF
			DIFX=XCROS(N(K,J,I))-XCROS(N(4,J,I))
			DIFY=YCROS(N(K,J,I))-YCROS(N(4,J,I))
			IF(ABS(DIFX).LT.0.0001) THEN
			    XSAME = XCROS(N(K,J,I))
			    GOTO 230
			END IF
			IF(ABS(DIFY).LT.0.0001) THEN
			    YSAME = YCROS(N(K,J,I))
			    GOTO 230
			END IF
		    END DO
 230		    DO K=1,2
			DO L=1,2
		    	XCOR = IX+L-2
		    	YCOR=IY+K-2
			IF(ABS(M(1)).LT.1.) THEN
			    YIN = M(1)*XCOR + C(1)
			    IF(YCOR.LT.YIN) GOTO 240
			ELSE
			    XIN = (YCOR - C(1))/M(1)
			    IF(XCOR.LT.XIN) GOTO 240
			END IF
			IF(ABS(M(2)).LT.1.) THEN
			    YIN = M(2)*XCOR + C(2)
			    IF(YCOR.GT.YIN) GOTO 240
			ELSE
			    XIN = (YCOR - C(2))/M(2)
			    IF(XCOR.LT.XIN) GOTO 240
			END IF
			IF(ABS(M(3)).LT.1.) THEN
			    YIN = M(3)*XCOR + C(3)
			    IF(YCOR.GT.YIN) GOTO 240
			ELSE
			    XIN = (YCOR - C(3))/M(3)
			    IF(XCOR.GT.XIN) GOTO 240
			END IF
			IF(ABS(M(4)).LT.1.) THEN
			    YIN = M(4)*XCOR + C(4)
			    IF(YCOR.LT.YIN) GOTO 240
			ELSE
			    XIN = (YCOR - C(4))/M(4)
			    IF(XCOR.GT.XIN) GOTO 240
			END IF
		        XCORIN = XCOR
		        YCORIN = YCOR
			GOTO 245
 240		        END DO
		    END DO
 245		    DMAX = 0.
		    IF(XSAME.GT.0.2) THEN
			DO K = 1,4
			    DIF = ABS(YCROS(N(K,J,I))-YCORIN)
			    IF(DIF.GT.DMAX) DMAX = DIF
			END DO
		    ELSE
			DO K = 1,4
			    DIF = ABS(XCROS(N(K,J,I))-XCORIN)
			    IF(DIF.GT.DMAX) DMAX = DIF
			END DO
		    END IF
		    DAREA = DMAX-DA1-DA2
		    CALL SWAP(DAREA,DBAD,LBAD)
		    GOTO 150
		END IF

C   CASE OF NCORN=0, NCROS=6, NIN=1   ALL BUT 3 TRIANGLES

		IF(NIN(J,I).EQ.1.AND.NCROS(J,I).EQ.6) THEN
		    DX = XCROS(N(1,J,I)) - XCROS(N(2,J,I))
		    DY = YCROS(N(1,J,I)) - YCROS(N(2,J,I))
		    DA1 = ABS(DX*DY)
		    DX = XCROS(N(3,J,I)) - XCROS(N(4,J,I))
		    DY = YCROS(N(3,J,I)) - YCROS(N(4,J,I))
		    DA2 = ABS(DX*DY)
		    DX = XCROS(N(5,J,I)) - XCROS(N(6,J,I))
		    DY = YCROS(N(5,J,I)) - YCROS(N(6,J,I))
		    DA3 = ABS(DX*DY)
		    DA = 0.5*(DA1+DA2+DA3)
		    DAREA = 1. - DA
		    CALL SWAP(DAREA,DBAD,LBAD)
		    GOTO 150
		END IF

C  CASE OF NIN = 0, NCORN = 0, NCROS = 4  LARGE TRIANGLE-SMALL TRIANGLE

		IF(NIN(J,I).EQ.0.AND.NCROS(J,I).EQ.4) THEN
		    DX = XCROS(N(1,J,I)) - XCROS(N(2,J,I))
		    DY = YCROS(N(1,J,I)) - YCROS(N(2,J,I))
		    DA1 = 0.5*ABS(DX*DY)
		    DX = XCROS(N(3,J,I)) - XCROS(N(4,J,I))
		    DY = YCROS(N(3,J,I)) - YCROS(N(4,J,I))
		    DA2 = 0.5*ABS(DX*DY)
		    DAREA = ABS(DA1 - DA2)
		    CALL SWAP(DAREA,DBAD,LBAD)
		    GOTO 150
		END IF

C  NOW FOR THE CASES WITH A SEGMENT CORNER INCLUDED

C  CASE OF NCORN=1, NCROS=2, NIN=2 PENTAGON
C  THIS ONE'S ALSO A BIT OF A BUMMER

 200		IF(NCORN(J,I).EQ.1.AND.NIN(J,I).EQ.2.AND.NCROS(J,I).
     &		EQ.2) THEN
		    DX = XCROS(N(1,J,I))-X(NUMC(J,I))
		    DY = YCROS(N(1,J,I))-Y(NUMC(J,I))
		    DA1 = 0.5*ABS(DX*DY)
		    DX = XCROS(N(2,J,I))-X(NUMC(J,I))
		    DY = YCROS(N(2,J,I))-Y(NUMC(J,I))
		    DA2 = 0.5*ABS(DX*DY)
		    DX = 0.
		    DY = 0.
		    DIF = ABS(XCROS(N(1,J,I))-XCROS(N(2,J,I)))
		    IF(DIF.GT.0.995.AND.DIF.LT.1.005) THEN
			DY = ABS(Y(NUMC(J,I))-INT(Y(NUMC(J,I))))
		    ELSE
			DX = ABS(X(NUMC(J,I))-INT(X(NUMC(J,I))))
		    END IF
		    XC = IX
		    YC = IY
		    IF(ABS(M(1)).LT.1.) THEN
			YIN = M(1)*XC + C(1)
			IF(YC.LT.YIN) GOTO 320
		    ELSE
			XIN = (YC - C(1))/M(1)
			IF(XC.LT.XIN) GOTO 320
		    END IF
		    IF(ABS(M(2)).LT.1.) THEN
			YIN = M(2)*XC + C(2)
			IF(YC.GT.YIN) GOTO 320
		    ELSE
			XIN = (YC - C(2))/M(2)
			IF(XC.LT.XIN) GOTO 320
		    END IF
		    IF(ABS(M(3)).LT.1.) THEN
			YIN = M(3)*XC + C(3)
			IF(YC.GT.YIN) GOTO 320
		    ELSE
			XIN = (YC - C(3))/M(3)
			IF(XC.GT.XIN) GOTO 320
		    END IF
		    IF(ABS(M(4)).LT.1.) THEN
			YIN = M(4)*XC + C(4)
			IF(YC.LT.YIN) GOTO 320
		    ELSE
			XIN = (YC - C(4))/M(4)
			IF(XC.GT.XIN) GOTO 320
		    END IF
		    XC = XC + 1.
		    YC = YC + 1.
 320		    YC = YC - 1.
		    XC = XC - 1.
		    IF(DX.LT.0.0001) THEN
			DY = ABS(Y(NUMC(J,I))-YC)
			DAREA = DY
			DY1 = ABS(YCROS(N(1,J,I))-YC)
			IF(DY1.GT.DY) THEN
			    DAREA = DAREA + DA1
			ELSE
			    DAREA = DAREA - DA1
			END IF
			DY2 = ABS(YCROS(N(2,J,I))-YC)
			IF(DY2.GT.DY) THEN
			    DAREA = DAREA + DA2
			ELSE
			    DAREA = DAREA - DA2
			END IF
		    ELSE
			DX = ABS(X(NUMC(J,I))-XC)
			DAREA = DX
			DX1 = ABS(XCROS(N(1,J,I))-XC)
			IF(DX1.GT.DX) THEN
			    DAREA = DAREA + DA1
			ELSE
			    DAREA = DAREA - DA1
			END IF
			DX2 = ABS(XCROS(N(2,J,I))-XC)
			IF(DX2.GT.DX) THEN
			    DAREA = DAREA + DA2
			ELSE
			    DAREA = DAREA - DA2
			END IF
		    END IF
		    CALL SWAP(DAREA,DBAD,LBAD)
		    GO TO 150
		END IF

C  THIS ONES A BIT EASIER
C  CASE OF NCORN=1, NCROS=2, NIN=0  TRIANGLE

		IF(NCORN(J,I).EQ.1.AND.NIN(J,I).EQ.0.AND.NCROS(J,I).
     &		EQ.2) THEN
		    DX1 = XCROS(N(1,J,I))-XCROS(N(2,J,I))
		    DY1 = YCROS(N(1,J,I))-YCROS(N(2,J,I))
		    DX2 = X(NUMC(J,I))-XCROS(N(1,J,I))
		    DY2 = Y(NUMC(J,I))-YCROS(N(1,J,I))
		    DA1 = 0.5*ABS(DX1*DY2)
		    DA2 = 0.5*ABS(DX2*DY1)
		    DAREA = DA1 + DA2
		    CALL SWAP(DAREA,DBAD,LBAD)
		    GO TO 150
		END IF

C   CASE OF NCORN=1, NCROS=2, NIN=1  QUADRILATERAL

		IF(NCORN(J,I).EQ.1.AND.NIN(J,I).EQ.1.AND.NCROS(J,I).EQ.
     &		2) THEN
		    DIF = ABS(XCROS(N(1,J,I))-NINT(XCROS(N(1,J,I))))
		    DX1 = XCROS(N(1,J,I))-XCROS(N(2,J,I))
		    DY1 = YCROS(N(1,J,I))-YCROS(N(2,J,I))
		    IF(DIF.LT.0.0001) THEN
			XCOR = XCROS(N(1,J,I))
			YCOR = YCROS(N(2,J,I))
		    ELSE
			XCOR = XCROS(N(2,J,I))
			YCOR = YCROS(N(1,J,I))
		    END IF
		    DX2 = X(NUMC(J,I))-XCOR
		    DY2 = Y(NUMC(J,I))-YCOR
		    DA1 = 0.5*ABS(DX1*DY2)
		    DA2 = 0.5*ABS(DX2*DY1)
		    DAREA = DA1 + DA2
		    CALL SWAP(DAREA,DBAD,LBAD)
		    GO TO 150
		END IF

C  CASE OF NCORN=1, NCROS=2, NIN=3  DIFFICULT TO DESCRIBE

		IF(NCORN(J,I).EQ.1.AND.NIN(J,I).EQ.3.AND.NCROS(J,I).
     &		EQ.2) THEN
		    DX1 = XCROS(N(1,J,I))-XCROS(N(2,J,I))
		    DY1 = YCROS(N(1,J,I))-YCROS(N(2,J,I))
		    DIF = ABS(XCROS(N(1,J,I))-NINT(XCROS(N(2,J,I))))
		    DIF = ABS(DIF - NINT(DIF))
		    IF(DIF.LT.0.001) THEN
			XCOR = XCROS(N(1,J,I))
			YCOR = YCROS(N(2,J,I))
		    ELSE
			XCOR = XCROS(N(2,J,I))
			YCOR = YCROS(N(1,J,I))
		    END IF
		    DX2 = X(NUMC(J,I))-XCOR
		    DY2 = Y(NUMC(J,I))-YCOR
		    DA1 = 0.5*ABS(DX1*DY2)
		    DA2 = 0.5*ABS(DX2*DY1)
		    DAREA = 1. - DA1 - DA2
		    CALL SWAP(DAREA,DBAD,LBAD)
		    GOTO 150
		END IF

C  THATS IT  NOW WORK OUT MEAN INTENSITY ETC

 150		CONTINUE
          if(pixval.eq.pixval) then
		DINT = DAREA * PIXVAL
		AREA = AREA + DAREA
		VALUE = VALUE + DINT
		BAD = BAD + DBAD
          endif
 100	    END DO
	END DO
      if(npts>0) then       
        call xits(pix,npts,5.,xmean1,sig1,xmean2,sig2,npts2,its)
        out_sig=sig2
      else
        out_sig=0.
      endif
 	RETURN

C   ERROR CONDITIONS

*999  print *, 'Array bounds out of range'
*     print *, 'NBX = ', NBX, '   NBY = ', NBY
*     print *, 'IX = ', IX, '   IY = ', IY
*     print *, 'NUM = ', NUM
999	VALUE = 0.0
	AREA = 0.0
	RETURN
	END

C  THIS SUBROUTINE DOES AN ITERATION IN RJNPROF

	SUBROUTINE NEWIT(PIX,NX,NY,DATA,MAJFACT,ANGLE,PIXVAL,
     *                 xint,iter,sig)
	real PIX (4096,4096)
	INTEGER NX, NY, NBX, NBY, NSAMP, NANN, iter
	REAL DATA(18), ANGLE(200000), PIXVAL(200000), C(2), S(2)
	REAL X(300), Y(300), XX(8), YY(8), XC(5), YC(5), AVER(2)
	REAL SINPA, MAJFACT, COSPA, ROOTMF, DPHI, MAJSIN, MAJCOS, MINSIN
	REAL MINCOS, ECC, RAD, X0, Y0, RMIN, UNDWT, SLOPE, PA
	COMMON /SAMPS/ NSAMP
	PI = 3.14159265359

C  EQUIVALENCE TO ELEMENTS IN DATA ARRAY

	PA = DATA(14)
	ECC = DATA(13)
	X0 = DATA(15)
	Y0 = DATA(16)
	RAD = DATA(4)
	UNDWT = DATA(17)
	COSPA = COS (PA)
	SINPA = SIN (PA)
	ROOTMF = SQRT (MAJFACT)

      nsig=0 
      sig=0.

C  DEPENDING ON WHETHER R < 20, USE EITHER INTERP OR INTERP2

	IF (RAD .GE. 20.0) THEN
	    NSAMP = 120
	    NANN = 2
	ELSE
	    NSAMP = 2.0 * PI * RAD
	    IF (NSAMP .LE. 40) NSAMP = 40
	    NANN = 1
	END IF

C      if(rad.gt.20.and.rad.lt.22) print*, 'in newit'

C  ANGLE INCREMENT CHOSEN TO MAKE DS = 1 APPROX

	DPHI = 2.0 * PI / FLOAT (NSAMP)
	RAD = RAD / ROOTMF

C  WORK OUT SLOPE BY ITERATING AT INNER AND OUTER RADII

	DO J = 1, 2
	    RMIN = RAD * (1.0 - ECC)
	    MINCOS = RMIN * COSPA
	    MINSIN = RMIN * SINPA
	    MAJCOS = RAD * COSPA
	    MAJSIN = RAD * SINPA
	    SUMVAL = 0.0
	    SUM = 0.0
	    DO I = 1, NSAMP
		ANGLE(I) = (I - 1) * DPHI
		DO L = 1, 2
		    C(L) = COS (L * ANGLE(I))
		    S(L) = SIN (L * ANGLE(I))
		END DO
		K = (J - 1) * NSAMP + I

C  WORK OUT THE INTERPOLATION POINT

		X(K) = X0 + MAJCOS * C(1) - MINSIN * S(1)
		Y(K) = Y0 + MAJSIN * C(1) + MINCOS * S(1)
		X1 = X(K)
		Y1 = Y(K)

C  AND GET THE INTERPOLATED VALUE

		CALL INTERP (PIX, NX, NY, X1, Y1, VALUE, 0., iter)
		IF (VALUE .eq. value) THEN
		    SUMVAL = SUMVAL + VALUE
		    SUM = SUM + 1.0
		END IF
	    END DO
	    IF (SUM .NE. 0.0) AVER(J) = SUMVAL / SUM
	    RAD = RAD * MAJFACT
	END DO
	RAD = RAD / MAJFACT / ROOTMF

C  AND WORK OUT THE SLOPE

	SLOPE=(AVER(2)-AVER(1))*ROOTMF/RAD/(MAJFACT-1.0)
	DATA(3) = SLOPE

C  NOW DO THE ANALYSIS AROUND THE ELLIPSE

	DO I = 1, NSAMP

C  THESE ARE THE ANGLE VARIABLES AT WHICH THE DATA IS SAMPLED

	    ANGLE(I) = (FLOAT(I) - 0.5) * DPHI

C  INNER ELLIPSE

	    XX(1) = X(I)
	    XX(2) = X(I + 1)

C  OUTER

	    XX(3) = X(NSAMP + I + 1)
	    XX(4) = X(NSAMP + I)

C  INNER

	    YY(1) = Y(I)
	    YY(2) = Y(I + 1)

C  AND OUTER

	    YY(3) = Y(NSAMP + I + 1)
	    YY(4) = Y(NSAMP + I)
	    IF (I .EQ. NSAMP) THEN
		XX(1) = X(I)
		XX(2) = X(1)
		XX(3) = X(I + 1)
		XX(4) = X(2 * I)
		YY(1) = Y(I)
		YY(2) = Y(1)
		YY(3) = Y(I + 1)
		YY(4) = Y(2 * I)
	    END IF


C  FOR BILINEAR INTERPOLATION, TAKE C OF G OF 4 POINTS

	    IF (NANN .EQ. 1) THEN
		X1 = (XX(1) + XX(2) + XX(3) + XX(4)) * 0.25
		Y1 = (YY(1) + YY(2) + YY(3) + YY(4)) * 0.25

C  AND INTERPOLATE

		CALL INTERP(PIX,NX,NY,X1,Y1,VALUE,xint,iter)
		PIXVAL(I) = VALUE
*            write(*,'(i3,3f6.1)') i,x1,y1,pixval(i)
		GOTO 200
	    END IF
	    DO K = 1, 4
		YY(K + 4) = YY(K)
		XX(K + 4) = XX(K)
	    END DO

C  SORT OUT THE X AND Y VALUES

	    CALL SORT (XX, YY, XC, YC)
*	    IXMAX = JMAX1 (XC(1), XC(2), XC(3), XC(4))
	    IXMAX = MAX (XC(1), XC(2), XC(3), XC(4))
	    IF (IXMAX .GE. NX) then
            dumnull=-1.
            pixval(i)=sqrt(dumnull)
            GOTO 100
          endif
*	    IXMIN = JMIN1 (XC(1), XC(2), XC(3), XC(4))
	    IXMIN = MIN (XC(1), XC(2), XC(3), XC(4))
	    IF (IXMIN .LE. 1) then
            dumnull=-1.
            pixval(i)=sqrt(dumnull)
            GOTO 100
          endif
	    NBX = IXMAX - IXMIN + 1
*	    IYMAX = JMAX1 (YC(1), YC(2), YC(3), YC(4))
	    IYMAX = MAX (YC(1), YC(2), YC(3), YC(4))
	    IF (IYMAX .GE. NY) then
            dumnull=-1.
            pixval(i)=sqrt(dumnull)
            GOTO 100
          endif
*	    IYMIN = JMIN1 (YC(1), YC(2), YC(3), YC(4))
	    IYMIN = MIN (YC(1), YC(2), YC(3), YC(4))
	    IF (IYMIN .LE. 1) then
            dumnull=-1.
            pixval(i)=sqrt(dumnull)
            GOTO 100
          endif
	    NBY = IYMAX - IYMIN + 1

C  AND CALL THE MORE COMPLICATED INTERPOLATION SUBROUTINE FOR R>20

	    CALL INTERP2(PIX,NX,NY,NBX,NBY,XC,YC,.FALSE.,VALUE,AREA,BAD,
     *                 xint,iter,out_sig)
          if(out_sig.ne.0) then      
            nsig=nsig+1   
            sig=sig+out_sig
          endif

C  WORK OUT WHAT THE AREA SHOULD BE

	    A1 = YC(2) * XC(3) - XC(2) * YC(3)
	    A2 = YC(3) * XC(4) - XC(3) * YC(4)
	    A3 = YC(1) * XC(2) - XC(1) * YC(2)
	    A4 = YC(4) * XC(1) - XC(4) * YC(1)
	    CALC = 0.5 * (A1 + A2 + A3 + A4)

C  AND THE % DIFFERENCE BETWEEN THIS AND THAT CALCULATED IN INTERP2

	    IF (CALC .NE. 0.0) THEN
		PDIF = (CALC - AREA - BAD) / CALC * 100.0
	    END IF
C          if(abs(pdif).gt.0.5) print*, i,calc,area,(calc-area)/calc,pdif
C          if(rad.gt.20.and.rad.lt.22) then
C            print*, 'pdif',i,pdif,calc,area,bad
C          endif

C  IF NOT TOO BIG

C	    IF (ABS (PDIF) .LT. 0.5 .AND. AREA .NE. 0.0) THEN
C new gludge to get more pixels near 20 radius
	    IF (ABS (PDIF) .LT. 1.5 .AND. AREA .NE. 0.0) THEN
*            print*, 'OK ',calc,area,bad,pdif
		PIXVAL(I) = VALUE / AREA
C            if(rad.gt.20.and.rad.lt.22) then
C              print*, 'pixval',i,pdif,pixval(i),value,area
C            endif

C  OTHERWISE WRITE OUT THE OFFENDING COORDINATES TO FILE SO PROGRAM TEST
C  CAN SEE WHAT WENT WRONG

	    ELSE IF (ABS (PDIF) .GT. 0.5 .AND. AREA .NE. 0.0) THEN
*	DO L = 1, 4
*	    WRITE (*, *) XX(L), YY(L)
*		    WRITE (8, *) XX(L), YY(L) <-error file
*	END DO
*            print*, 'BAD',calc,area,bad,pdif
*		PIXVAL(I) = VALUE / AREA
            dumnull=-1.
 		PIXVAL(I) = sqrt(dumnull)
	    END IF
100       continue
	    APB = AREA + BAD
	    IF (APB .NE. 0.0) THEN
		IF (BAD/APB .GT. 0.05) then
              dumnull=-1.
 		  PIXVAL(I) = sqrt(dumnull)
            endif
	    END IF

 200	END DO

C  WELL THATS IT - WASNT TOO BAD WAS IT?

      sig=sig/nsig
	RETURN
	END

	SUBROUTINE RMSDEV(MODEL,PIXVAL,RMSRES,GOOD)
	REAL MODEL(200000),PIXVAL(200000)
	COMMON /SAMPS/ NSAMP
	GOOD = 0.
	SUMSQ = 0.
	DO I = 1,NSAMP
	    IF(PIXVAL(I).eq.pixval(i)) THEN
		DEV = MODEL(I)-PIXVAL(I)
		DEV = DEV*DEV
		SUMSQ = SUMSQ + DEV
		GOOD = GOOD + 1.
	    END IF
	END DO
	RMSRES = SQRT(SUMSQ/GOOD)
	RETURN
	END

	SUBROUTINE LINSOLVE(A,B,N)
	DOUBLE PRECISION A(N,N), B(N), PIVOT,X(10), AIJCK
	INTEGER IROW(10),JCOL(10)
	THRESH = 0.00001
	DO K = 1,N
	    KM1 = K - 1
	    PIVOT = 0.0
	    DO I = 1,N
		DO J = 1,N
		    IF(K.EQ.1) GOTO 100
		    DO ISCAN = 1,KM1
			IF(I.EQ.IROW(ISCAN)) GOTO 200
		    END DO
		    DO JSCAN = 1,KM1
			IF(J.EQ.JCOL(JSCAN)) GOTO 300
		    END DO
 100		    IF(DABS(A(I,J)).GT.DABS(PIVOT)) THEN
			PIVOT = A(I,J)
			IROW(K) = I
			JCOL(K) = J
		    END IF
 300		END DO
 200	    END DO
	    IROWK = IROW(K)
	    JCOLK = JCOL(K)
	    IF(PIVOT.NE.0.) THEN
		THRESH = THRESH/PIVOT
	    ELSE
*           print *, 'PIVOT = 0'
		RETURN
	    END IF
	    IF(PIVOT.LE.THRESH) THEN
*           print *, 'SET OF EQUATIONS IS ILL-FORMED'
		RETURN
	    END IF
	    DO J = 1,N
		A(IROWK,J) = A(IROWK,J)/PIVOT
	    END DO
	    B(IROWK) = B(IROWK)/PIVOT
	    DO I = 1,N
		IF(I.NE.IROWK) THEN
		    AIJCK = A(I,JCOLK)
		    DO J = 1,N
			A(I,J) = A(I,J) - AIJCK*A(IROWK,J)
		    END DO
		    B(I) = B(I) - AIJCK*B(IROWK)
		END IF
	    END DO
	END DO
	DO I = 1,N
	    IROWI = IROW(I)
	    JCOLI = JCOL(I)
	    X(JCOLI) = B(IROWI)
	END DO
	DO I = 1,N
	    B(I) = X(I)
	END DO
	RETURN
	END

	SUBROUTINE SWAP(DAREA,DBAD,LBAD)
	REAL DAREA,DBAD
	LOGICAL LBAD
	IF(LBAD) THEN
	    DBAD = DAREA
	    DAREA = 0.
	END IF
	RETURN
	END
	SUBROUTINE SORT (X, Y, XX, YY)
	REAL X(8), Y(8), XX(5), YY(5)
	YMIN = 100000.0
	DO I = 1, 4
	    IF (Y(I) .LT. YMIN) THEN
		YMIN = Y(I)
		NYMIN = I
	    END IF
	END DO
	IF (X(NYMIN + 1) .GT. X(NYMIN + 3)) THEN
	    XX(2) = X(NYMIN + 3)
	    XX(4) = X(NYMIN + 1)
	    YY(2) = Y(NYMIN + 3)
	    YY(4) = Y(NYMIN + 1)
	ELSE
	    XX(2) =  X(NYMIN + 1)
	    YY(2) =  Y(NYMIN + 1)
	    XX(4) =  X(NYMIN + 3)
	    YY(4) =  Y(NYMIN + 3)
	END IF
	XX(3) = X(NYMIN + 2)
	YY(3) = Y(NYMIN + 2)
	XX(1) = X(NYMIN)
	YY(1) = YMIN
	YY(5) = YY(1)
	XX(5) = XX(1)
	RETURN
	END

      subroutine kill_pix(data,nx,ny,ik,jk)
      real data(4096,4096)

      i1=ik-1
      if(i1.le.0) i1=1
      i2=ik+1
      if(i2.ge.nx) i2=nx
      j1=jk-1
      if(j1.le.0) j1=1
      j2=jk+1
      if(j2.ge.ny) j2=ny
      dumnull=-1.
      do j=j1,j2
        do i=i1,i2
          data(i,j)=sqrt(dumnull)
        enddo
      enddo
      return
      end

      subroutine dump(output,nfile,file)
	real output(900,18)
      character file*100

      open(unit=1,file=file)
      xmin=1.e99
      xold=0.
      do i=1,nfile
        do l=1,nfile
          if(output(l,4) < xmin .and. output(l,4) > xold) then
            xmin=output(l,4)
            iout=l
          endif
        enddo
        if(output(iout,7).eq.-1) output(iout,7)=1.
* reserve -1 flag for cleaned ellipses
* kludge here
        output(iout,15)=output(iout,15)+0.5
        output(iout,16)=output(iout,16)+0.5
        write(1,10) (output(iout,j),j=1,18)
10      format(18(1pe16.8))
        xold=xmin
        xmin=1.e99
      enddo

999	return
      end

      subroutine printerror(status)  
      integer status
      character errtext*30,errmessage*80     

      call ftgerr(status,errtext)
      print *,'FITSIO Error Status =',status,': ',errtext
      call ftgmsg(errmessage) 
      do while (errmessage .ne. ' ')
          print *,errmessage
          call ftgmsg(errmessage)
      end do
      end

      subroutine xits(data,npts,xsig,xmean1,sig1,xmean2,sig2,npts2,its)
*
*     data = data points, npts = # of data, xsig = # of sigmas for delete
*     xmean1 = first mean, xsig1 = first sigma
*     xmean2 = final mean, xsig2 = final sigma
*     npts2 = final # of data used, its = # of iterations on mean
*
      real data(npts)

      xmean1=0.
      sig1=0.
      n=0
      do i=1,npts
        if(data(i).eq.data(i)) then
          n=n+1
          xmean1=xmean1+data(i)
        endif
      enddo
      xmean1=xmean1/n
      do i=1,npts
        if(data(i).eq.data(i)) sig1=sig1+(data(i)-xmean1)**2
      enddo
      sig1=(sig1/(n-1))**.5

      sig2=sig1
      xmean2=xmean1
      xold=xmean2+0.001*sig1
      its=0
      do while (xold.ne.xmean2)
        xold=xmean2
        its=its+1
        dum=0.
        npts2=0
        dumnull=-1.
        do j=1,npts
          if(data(j).eq.data(j)) then
            if(abs(data(j)-xold).gt.xsig*sig2) then
              data(j)=sqrt(dumnull)
            else
              npts2=npts2+1
              dum=dum+data(j)
            endif
          endif
        enddo
        xmean2=dum/npts2
        dum=0.
        do j=1,npts
          if(data(j).eq.data(j)) dum=dum+(data(j)-xmean2)**2
        enddo
        sig2=(dum/(npts2-1))**.5
      enddo
      return
      end
