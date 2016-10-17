* -finit-local-zero

	real radius(500),sr(500),rf(500),sf(500),prf(18)
	real a(10),lx(500),ly(500),yfit(500),re
	integer*2 kill(500)
	character name*20,char,rply,strng*20
      common xmin,xmax,ymin,ymax,nt

	n=iargc()
	call getarg(1,name)

      open(unit=1,file=name,status='old',err=999)
      read(1,*) cstore,alpha,se,re,sky
      ifit=4
      sstore=1.0857/alpha
	do while (.true.)
        npts=npts+1
	  read(1,*,end=200) radius(npts),sr(npts),kill(npts)
	enddo
      
200   close(unit=1)
      if(radius(npts) == 0) npts=npts-1  ! kludge for do while read???

	do i=1,npts
	  if(kill(i).ne.1) then
          nf=nf+1
          rf(nf)=radius(i)
          sf(nf)=sr(i)
        endif
      enddo
*      print*, '0th',se,re,sstore,cstore,nf
*      call fitx(nf,rf,sf,se,re,sstore,cstore,chisqr,2)
*      print*, '1st',se,re,sstore,cstore
      call fitx(nf,rf,sf,se,re,sstore,cstore,chisqr,4)
      print*, '2nd',se,re,sstore,cstore

999	end

	subroutine fitx(npts,r,s,ie,re,sstore,cstore,chsqr,nt)

***	r,s = arrays of radius and surface brightness
***	npts = number of points
***	ie = eff. surface brightness
***	re = eff. radius
***	sstore = disk scale length
***	cstore = disk surface brightness (see format below for conversion 
***              to astrophysically meaningful values)
***   nt = number of parameters to fit (2 for r^1/4, 4 for B+D)
***	program would like some first guess to speed things up

	real ie
	real sigmay(1000),dela(10),sigma(10),yfit(1000),
     .	r(npts),s(npts),edge(10,2),a(10)

*** set sigmay
	do j=1,npts
	  sigmay(j)=1.
	enddo

*** intialize parameters
	nitlt=500
	if(nt.eq.3.and.sstore.eq.0) then
*	  xrint*, 'Disk slope required for three parameter fits'
	  return
	endif

*** computer guess if no input
	if(ie.eq.0) then
	  a(1)=22.
	  a(2)=10.
	  a(3)=22.
	  a(4)=3.e-2
	  if(nt.eq.2) then
          a(3)=cstore
	    a(4)=sstore
        endif
	else
	  a(1)=ie
	  a(2)=re
	  a(3)=cstore
	  a(4)=sstore
	endif

*** initialize step size
	dela(1)=0.1
	dela(2)=0.1
	dela(3)=0.1
	dela(4)=1.e-4

*** set edges of fit
	edge(1,1)=5.
	edge(1,2)=35.
	edge(2,1)=.5
	edge(2,2)=200.
	edge(3,1)=10.
	edge(3,2)=30.
	edge(4,1)=1.e-8
	edge(4,2)=.5

*** show fits to terminal
	nit=0
*	xrint*, ' '
*	xrint 90, npts,r(1),r(npts)
*90	format(' # of points = ',i4,' range = ',1pe8.2,' to ',1pe8.2)
*	xrint*, ' '
*	xrint*, '              -- Initial guess --'
*	xrint*, ' '
        alpha = 1.0857/a(4)
        xbm = a(1) - 5.*alog10(a(2)) - 40.0
        xdm = a(3) - 5.*alog10(alpha) - 38.6
        bdratio = 10.**(-0.4*(xbm - xdm))
*	xrint 100, nit,bdratio,(a(i),i=1,3),alpha,chsqr
*	xrint*, ' '
*	xrint*, ' '

*** call for grid search
300	call gridls(r,s,sigmay,npts,nt,1,a,dela,sigma,yfit,chsqr,edge)
	if(nt.eq.3) chsqr=chsqr*(npts-3)/(npts-4)
	nit=nit+1
      alpha = 1.0857/a(4)
      if(nit .gt. 5) Then
        xbm = a(1) - 5.*alog10(a(2)) - 40.0
        xdm = a(3) - 5.*alog10(alpha) - 38.6
        bdratio = 10.**(-0.4*(xbm - xdm))
      endif

*** compare to old fit for convergence test
	dif1=abs(a(1)-olda1)
	dif2=abs(a(2)-olda2)
	dif3=abs(a(3)-olda3)
	dif=dif1+dif2+dif3
	if(nt.eq.4) then
	  dif=(dif+10*olda4)/4
	else
	  dif=dif/3
	endif
	if((dif.lt.1e-7).and.(nit>50)) then
*	  xrint*, ' '
*	  xrint*, ' Parameters unchanged at the 0.1% level',nit,dif
	  goto 400
	endif
	olda1=a(1)
	olda2=a(2)
	olda3=a(3)
	olda4=a(4)

*** ever 20th step - reset step size
	if(mod(nit,20).eq.0) then
	   dela(1)=0.1
	   dela(2)=0.1
	   dela(3)=0.1
	   dela(4)=1.e-4
	endif
	if(nit.lt.nitlt) go to 300

*** query for more fits
400	xbm = a(1) - 5.*alog10(a(2)) - 40.0
      xdm = a(3) - 5.*alog10(alpha) - 38.6
      bdratio = 10.**(-0.4*(xbm - xdm))
*	xrint*, ' B/D   Ie   Re    B(0)    Alpha    chisqr'
*	xrint 100, bdratio,a(1),a(2),a(3),alpha,chsqr
100	format(f5.2,1x,f5.2,1x,f4.1,1x,f4.1,1x,1pe9.3,1x,1pe9.3)

*** set to meaningful values
	ie=a(1)
	re=a(2)
	cstore=a(3)
	sstore=a(4)
	return
	end

      subroutine gridls (x,y,sigmay, npts,nterms, mode, a, deltaa,
     1 sigmaa, yfit, chisqr,edge)
      dimension x(1),y(1),sigmay(1),a(1),deltaa(1),sigmaa(1),yfit(1)
     .,edge(10,2)
   11 nfree=npts - nterms
      chisqr =0.
      free=nfree
      if (nfree) 100,100,20
   20 do 90 j=1,nterms
***** evaluate chi square at first two seach points
   21 do 22 i=1,npts
   22 yfit(i)=airy(x,i,a,NTERMS)
   23 chisq1=fchisq(y,sigmay,npts,nfree,mode,yfit)
      fn=0.
      delta=deltaa(j)
   41 a(j)=a(j)+delta
      if(a(j) .lt. edge(j,1) .or. a(j) .gt. edge(j,2)) go to 82
      do 43 i=1,npts
   43 yfit(i)=airy(x,i,a,NTERMS)
   44 chisq2=fchisq(y,sigmay,npts,nfree,mode,yfit)
      if(chisq1-chisq2)51,61,61
***** reverse direction of search if chi square is increasing
   51 delta=-delta
      a(j)=a(j)+delta
      do 54 i=1,npts
   54 yfit(i)=airy(x,i,a,NTERMS)
      save=chisq1
      chisq1=chisq2
   57 chisq2=save
***** increnemt a(j) until chi square increases
   61 fn=fn+1.0
      a(j)=a(j)+delta
      if(a(j) .lt. edge(j,1) .or. a(j) .gt. edge(j,2)) go to 81
      do 64 i=1,npts
   64 yfit(i)=airy(x,i,a,NTERMS)
      chisq3=fchisq(y,sigmay,npts,nfree,mode,yfit)
   66 if(chisq3-chisq2) 71,81,81
   71 chisq1 = chisq2
      chisq2 = chisq3
      go to 61
***** find minimum of parpbola defined by last three points
   81 FIX=CHISQ3-CHISQ2
	IF(FIX.EQ.0) FIX=1.E-8
      delta=delta*(1./(1.+(chisq1-chisq2)/FIX)+0.5)
	FIX=FREE*(CHISQ3-2.*CHISQ2+CHISQ1)
	IF(FIX.EQ.0) FIX=1.E-8
   83 sigmaa(j)=deltaa(j)*sqrt(2./FIX)
   82 a(j)=a(j)-delta
   84 deltaa(j)=deltaa(j)*fn/3.
   90 continue
***** evaluate fit an chi square for final parameters
   91 do 92 i=1,npts
   92 yfit(i)=airy(x,i,a,NTERMS)
   93 chisqr=fchisq(y,sigmay,npts,nfree,mode,yfit)
  100 return
      end

***** chisqr subroutine *****
	function fchisq(s,sigmay,npts,nfree,mode,yfit)
	dimension s(1),sigmay(1),yfit(1)
	chisq=0.
	do 30 j=1,npts
30	chisq=chisq+((s(j)-yfit(j))**2)/sigmay(j)**2
	fchisq=chisq/nfree
	return
	end

***** fitting functions *****
	function airy(r,i,a,nterms)
	dimension r(1),a(4)
	common ie,re,sstore,cstore,chsqr
	xnt = a(1) + 8.325*((r(i)/a(2))**0.25 - 1.0)
	xnt = -0.4*xnt
	xnt1 = 10**xnt
	xnt =  a(3) + a(4)*r(i)
	if(nterms.eq.4) xnt = a(3) + a(4)*r(i)
	xnt = -0.4*xnt
	xnt2 = 10**(xnt) 
	xnt3 = xnt1 + xnt2
	airy = -2.5*(alog10(xnt3))
	return
	end

	subroutine linfit(x,y,npt,a,chisqr)
	real x(1),y(1),a(10),yfit(500),sigmay(500)
	sum=0.
	sumx=0.
	sumy=0.
	sumx2=0.
	sumy2=0.
	sumxy=0.
	do i=1,npt
	  x1=x(i)
	  y1=y(i)
*	  weight=1./sigmay(i)**2
	  weight=1.
	  sum=sum+weight
	  sumx=sumx+weight*x1
	  sumy=sumy+weight*y1
	  sumx2=sumx2+weight*x1*x1
	  sumy2=sumy2+weight*y1*y1
	  sumxy=sumxy+weight*x1*y1
	enddo
	delta=sum*sumx2-sumx*sumx
	a(1)=(sumx2*sumy-sumx*sumxy)/delta
	a(2)=(sumxy*sum-sumx*sumy)/delta
	nfree=npt-2
	do i=1,npt
	  yfit(i)=a(2)*x(i)+a(1)
        sigmay(i)=1.
	enddo
	chisqr=fchisq(y,sigmay,npt,nfree,mode,yfit)
	return
	end
