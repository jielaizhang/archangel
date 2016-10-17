*
*  this program makes galaxies that resemble ccd frames
*  options to make either king laws,devauc r**1/4 laws,gaussian
*  (star) profiles,cones (zero profile curvature) or reading from
*  a prof output file to make a noise-free simulation of a real galaxy
*  option to patch over regions of a real data frame using the prof output
*  file.

	real*8 psf(100,100),iprf(300),rprf(300),pixval
	real*8 ellprf(300),paprf(300),x0prf(300),y0prf(300)
	real prof(18),nel,ron,noise 
	real int(512),patint(512,512)
      real data(4096,4096),pix(4096*4096)
	real*8 dpa,sigma,a1,ratio
	real*8 ecc,pa,re,i0,x0,y0,x,y,rc,cpar,ec,c
	real*8 papsf,ecpsf,sigpsf,rad2
      real*8 rdrop,rchange,rpsfch,ylo,yup
      integer list(2)
	logical conv,patch
	character*20 file,prfile,mode*1,cprof*1
	character cconv*1,patfile*20,delfil*20
	complex cd
	common /geom/ ec,pa
	common /geompsf/ ecpsf,papsf
	common /varpsf/ sigpsf,rpsfch
	common /const/ c
	common /lower/ ylo
	common /scale/ rdrop
	common /upper/ yup
	common /rads/ rc
	common /varnc/ sigma,rchange
	external devauc,king,y1,y2,gauss,cone,seeing
	conv=.false.
	patch=.false.
	dtor=3.14159265359/180.0

*  set up mode of use

*	write(*,'($,a)') 'Mode: 1.normal 2.patch: '
*	read(*,'(a)') mode
*	if(mode.eq.'2') patch=.true.
      mode='1'
	line=0

*  open output file

100   ifid=imopen('galaxy.fits','R')
      istat=imrkeyi(ifid,nx,'NAXIS1')
      istat=imrkeyi(ifid,ny,'NAXIS2')
      nt=imrpixr(ifid,pix,4096*4096)

* 100	write(*,'($,a)') 'name of output file:    '
*	read(*,'(a)') file
*	write(*,'($,a)') 'size of file    nx*ny:    '
*	read(*,*) nx,ny
*	len=nx*4/2
*	open(unit=1,file=file,access='direct',recl=len,err=100)
*	if(patch) then
*        cprof='5'
*        goto 150
*      endif

*  set up type of profile

 200	print*, 'type of galaxy profile'
*	print*, '1:  de vaucouleurs  r**1/4'
*	print*, '2:  "king" (1962) law '
*	print*, '3:  2-d gaussian'
*	print*, '4:  cone'
*	write(*,'($,a)') '5:  read from prof file:    '
*	read(*,'(a)') cprof
      cprof='5'
150	if(cprof.eq.'5') then
 	    write(*,'($,a)') 'name of prof output file:    '
*	    read(*,'(a)') prfile
          prfile='tmp.prf'
	    open(unit=2,file=prfile)

*  read ratio between successive major axes from record 1

*	    read(2,rec=1) (prof(j),j=1,18)
*	    ratio=prof(4)
	    ratio=1.44
	    linprf=2
	    index=1
	    rprf(1)=0.0

*    fill arrays for intensity, radius, ellipticity, pa, x0 and y0

	    do i=1,300
		linprf=linprf+1
		read(2,*,end=300) (prof(j),j=1,18)

*  only use records where the params were calculated

		if(prof(3).ne.0.0) then
		    index=index+1
		    rprf(index)=prof(4)
		    if(index.ne.2) then
			thisratio=rprf(index)/rprf(index-1)
			ratdiff=thisratio-ratio
			fracdiff=ratdiff/ratio
			if(fracdiff.gt.0.001) then
			    print*, 'successive major axes have ratio ',
     &			    'different from that in the header'
			    print*, 'this r=',rprf(index)
			    print*, 'last r=',rprf(index-1)
			    print*, 'ratio=',thisratio
			    print*, 'ratio in header=',ratio
			    ratio=0.0
			endif
		    endif
		    iprf(index)=prof(1)
		    ellprf(index)=prof(13)
		    paprf(index)=prof(14)
		    x0prf(index)=prof(15)
		    y0prf(index)=prof(16)
		endif
	    enddo
 300	    ellprf(1)=0.0
	    paprf(1)=0.0
	    x0prf(1)=x0prf(2)
	    y0prf(1)=y0prf(2)
	    iprf(1)=iprf(2)
	    rmax=rprf(index)
	    goto 625
 160	endif

*  now do the hard work

 625	do i=1,ny
          if(ipast.eq.ihold) then
            accept '(i1)', ihold
          else
            if(idum.eq.0) then
              idum=1
            else
              idum=0
            endif
            ipast=0
            ihold=0
            print*, 'toggle',idum
          endif
	    line=line+1
	    if(line.gt.ny) goto 999

*  set up initial values at the start of each line

	    x0=x0prf(index)+0.5
	    y0=y0prf(index)+0.5
	    ecc=ellprf(index)
	    ecc=1.0-ecc
	    ec=1.0/ecc/ecc-1.0
	    pa=paprf(index)
	    pa=pa*dtor
	    do j=1,nx
		if(patch.and.patint(j,i).ne.0) goto 750
 630		niter=0
		anslast=0.0
 650		y=float(line)-y0
		x=float(j)-x0
		rad2=x*x+y*y
		rad1=sqrt(rad2)

*  central pixels-integrating

            if(dabs(x).le.5.0.and.dabs(y).le.5.0.and.
     &        icent.eq.2) then
              ylo=y-0.5
              yup=ylo+1.0
              x1=x-0.5
		  x2=x1+1.0
		  if=1
		  absacc=1.0d-6
		  pixval=sky+i0*ans
		  data(j,line)=pixval
		else

*  main body of the galaxy

		  theta=datan2(y,x)
		  a=rad2 *(1.0+ec *(dsin(theta-pa)) ** 2)
 700		  if(itwist.eq.1) then
		    call twist(rad2,theta,pa,dpa,itwtype,ec,a)
		  endif
		  pixval=i0*pixval+sky
		  data(j,line)=pixval

*  using prof file

		  if(cprof.eq.'5'.or.patch) then
		    a1=sqrt(a)

*  so we dont bother iterating when we are outside the galaxy

              if(idum.eq.0) print*, a1,rmax,iprf(index)
		    if(a1.gt.rmax) then
			int(j)=iprf(index)
			goto 750
		    endif
		    call interpolate(rprf,iprf,index,a1,ans,ratio)
              if(idum.eq.0) print*, ans,ratio
		    error=ans-anslast
		    errmax=0.001*ans
                if(error.gt.errmax) then
			anslast=ans
			niter=niter+1
			if(niter.gt.10) then
			  print*, 'no convergence, i= ',line, 
     &				' j=',j
			  goto 750
			endif
			call interpolate(rprf,x0prf,index,a1,x0,ratio)

			x0=x0+0.5
			call interpolate(rprf,y0prf,index,a1,y0,ratio)

			y0=y0+0.5
			call interpolate(rprf,ellprf,index,a1,ecc,
     &			    ratio)
			ecc=1.0-ecc
			ec=1.0/ecc/ecc-1.0
			call interpolate(rprf,paprf,index,a1,pa,ratio)

			pa=pa*dtor
			goto 650
		    endif
		    int(j)=ans
		    if(patch) patint(j,i)=ans
		    goto 750
		  endif
		endif

*  add noise

		if(.not.conv) then
		    if(nel.gt.0.0) then
			noise =(sqrt(data(j,line)*nel+ron*ron)
     &			)/nel
			call gnd(iseed,cd)
			data(j,line)=data(j,line)+nint(noise*real(cd))
		    endif
		    int(j)=data(j,line)
		endif
 750	    enddo
	    if(.not.conv.and..not.patch) then
*		write(1,rec=line)(int(j),j=1,nx)
		type*, line,int(1),int(100),int(200)
            do ii=1,nx
              data(ii,line)=int(ii)
            enddo
	    endif
*	    if(patch) write(1,rec=line)(patint(j,i),j=1,nx)
	    if(patch) type*, line,i,patint(100,i)
	enddo
	if(conv) then
	    write(*,'($,a)') 'size of box about centre to do convolution:    '
	    read(*,*) nbox
	    call convolve(data,nx,ny,psf,nxp,nxp,x0,y0,nbox)
	endif
	if(conv) then
	    do i=1,ny
		do j=1,nx
		    if(nel.gt.0.0) then
			noise =(sqrt(data(j,i)*nel+ron*ron))/nel
			call gnd(iseed,cd)
			data(j,i)=data(j,i)+nint(noise*real(cd))
		    endif
		    int(j)=data(j,i)
		enddo
		if(i/10.gt.(i-1)/10) write(*,'(1h+,i6)') i
		write(1,rec=i) (int(j),j=1,nx)
	    enddo
	endif
 999	ifid2=imopen('clean.fits','W')
      type*, 'open output file'
      list(1)=ifid
      list(2)=0
      istat=imhdr(ifid2,list,op)
      do j=1,ny
        do i=1,nx
          pix(i+nx*(j-1))=data(i,j)
        enddo
      enddo
      nt=imwpixr(ifid2,pix,4096*4096)
      istat=imclose(ifid2)

      end

*  function for r**1/4 law

	real*8 function devauc(x,y)
	real*8 x,y,c,ec,ang,theta,r
	common /const/ c
	common /geom/ ec,ang
	r=x*x+y*y
	theta=datan2(y,x)+ang
	theta=1.57079632679-theta
	r=r *(1.0+ec *(dsin(theta) ** 2))
	devauc=10.0 **(c *(r ** 0.125))
	return
	end

*  function for king law

	real*8 function king(x,y)
	real*8 x,y,rc,c,ec,ang,r,theta
	common /rads/ rc
	common /geom/ ec,ang
	common /const/ c
	r=x*x+y*y
	if(x.eq.0.0) then
	    theta=ang
	else
	    theta=datan(y/x)+ang
	    theta=1.57079632679-theta
	endif
	r=r *(1.0+ec *(dsin(theta) ** 2))
	king=1.0 /(dsqrt(1.0+r/rc ** 2)-c) ** 2
	return
	end

*  function for gaussian

	real*8 function gauss(x,y)
	real*8 x,y,sigma,ang,r,theta,ec,rchange
	common /geom/ ec,ang
	common /varnc/ sigma,rchange
	r=x*x+y*y
	theta=datan2(y,x)+ang
	theta=1.57179632679-theta
	r=r *(1.0+ec *(dsin(theta) ** 2))
	rootr=sqrt(r)
	sig2=sigma*sigma
	z2=0.5*r/sig2
	if(rootr.le.rchange.or.rchange.le.0.0) then
	    gauss=exp(-z2)
	    return
	endif
	z1=0.5*rchange*rchange/sig2
	gauss=exp(z1 *(1.0-2.0*rootr/rchange))
	return
	end

*   gaussian+exponential wings psf function

	function gpexp(y)
      real*8 sigma,rchange
	common /varnc/ sigma,rchange
	sig2=sigma*sigma
	yy=y*y
	rc2=rchange*rchange
	z2=0.5*yy/sig2
	if(rchange.le.0.0.or.y.le.rchange) then
	    gpexp=exp(-z2)
	    return
	endif
	z1=0.5*rc2/sig2
	gpexp=exp(z1 *(1.0-2.0*y/rchange))
	return
	end

*  cone function

	real*8 function cone(x,y)
	real*8 x,y,rdrop,ang,r,theta,ec
	common /geom/ ec,ang
	common /scale/ rdrop
	r=x*x+y*y
	theta=datan2(y,x)+ang
	theta=1.57179632679-theta
	r=r *(1.0+ec *(dsin(theta) ** 2))
	cone=1.0-sqrt(r)*rdrop
	return
	end

*  point-spread function

	real*8 function seeing(x,y)
	real*8 x,y,ecpsf,papsf,rad2,theta,sigpsf,rpsfch
	common /geompsf/ ecpsf,papsf
	common /varpsf/ sigpsf,rpsfch
	rad2=x*x+y*y
	sigpsf2=sigpsf*sigpsf
	theta=datan2(y,x)-papsf
	rad2=rad2 *(1.0+ecpsf *(dsin(theta) ** 2))
	z2=0.5*rad2/sigpsf2
	rad=sqrt(rad2)
	if(rad.lt.rpsfch.or.rpsfch.eq.0.0) then
	    seeing=exp(-z2)
	else
	    z1=0.5*rpsfch*rpsfch/sigpsf2
	    seeing=exp(z1 *(1.0-2.0*rad/rpsfch))
	endif
	return
	end

*  function for nag routine

	real*8 function y1(y)
	real*8 y,yy1
	common /lower/ yy1
	y1=yy1
	return
	end

*  another function for the nag routine

	real*8 function y2(y)
	real*8 y,yy2
	common /upper/ yy2
	y2=yy2
	return
	end

*  this works out which ellipse we are on if there is a twist

	subroutine twist(r,theta,pa,dpa,ilog,ec,a)
	real*8 b(10),r,theta,pa,dpa,ec,a,panew
	n=2
	r=dsqrt(r)
	b(1)=r*dsqrt(1.0+ec *(dsin(theta-pa)) ** 2)
	b(2)=b(1)
	if(b(2).le.1.0d1) goto 100
 200	if(ilog.eq.1) panew=pa+dpa *(b(n)-10.0)/100.0
	if(b(n).le.10.0) b(n)=20.0-b(n)
	if(b(n).eq.10.0) b(n)=10.0+r/10.0
	if(ilog.eq.2) panew=pa+dpa *(dlog10(b(n))-1.0)
	b(n)=r*dsqrt(1.0+ec *(dsin(theta-panew)) ** 2)
	if(b(n)-b(n-1).le.0.00001*b(n)) goto 100
	if(n.ge.10) goto 300
	n=n+1
	goto 200
 300	print*, 'solution does not converge'
 100	a=b(n)*b(n)
	return
	end

*  this does the interpolating for making noise-free reconstructions
*  lets try and make it a bit quicker

	subroutine interpolate(x,y,n,x1,yy,ratio)
	real*8 x(n),y(n),x1,yy,ratio
	integer n
	if(ratio.eq.0.0) then
	    do i=1,n
		if(x(i).ge.0.0) then
		    if(x1.lt.x(i)) then
			ilo=i-1
		    endif
		    yy=y(i)
		endif
	    enddo
	    return
	else
	    if(x1.gt.x(2)) then
		ilo=int(dlog10(x1/x(2))/dlog10(ratio))+2
	    else
		ilo=1
	    endif
	endif
	yy=y(ilo) *(x(ilo+1)-x1)+y(ilo+1) *(x1-x(ilo))
	if(x(ilo+1).eq.x(ilo)) then
	    print*, 'subroutine interpolate error'
	    print*, 'x(i+1)=x(i)'
	    return
	endif
	yy=yy/(x(ilo+1)-x(ilo))
	return
	end

*  schechters gaussian normal distribution, returns a complex
*  number whose real and imaginary parts are normally distributed
*  around zero with variance 1

	subroutine gnd(i,cd)
	complex cexp,cmplx,cd
	data twopi /6.283185308/
	j=i
 100	t=rand(j)
	if(t.le.0.0.or.t.ge.1.0) goto 100
	t=alog(t)
	t=sqrt(-2.0*t)
	cd=t*cexp(cmplx(0.0,twopi*rand(j)))
	i=j
	return
	end

*  this subroutine convolves the array pixin(nx,ny) with the psf array
*  psf(npx,npy). only nbox x nbox around(x0,y0) is convolved

	subroutine convolve(pixin,nx,ny,psf,npx,npy,x0,y0,nbox)
	real*8 psf(100,100)
	real*8 tot,x0,y0
	integer*2 pixin(512,512),pixout(512,512)
	iy0=dnint(y0)
	ix0=dnint(x0)
	nbox2=nbox/2

*  have another look at psf

	do i=1,npy
	    write(*,100) (1000.0*psf(j,i),j=1,npx)
	enddo
 100	format(11f5.1)
	write(*,'('' convolving'',/)')
	do i=iy0-nbox2,iy0+nbox2
*	    write(*,'(1h+,i6)') i
	    do j=1,nx
		pixout(j,i)=pixin(j,i)
	    enddo
	    do j=ix0-nbox2,ix0+nbox2
		tot=0.0
		do ip=1,npy
		    imin=i-npy/2+ip
		    if(imin.lt.1) imin=1
		    if(imin.gt.ny) imin=ny
		    do jp=1,npx
			jmin=j-npx/2+jp
			if(jmin.lt.1) jmin=1
			if(jmin.gt.nx) jmin=nx
			tot=tot+float(pixin(jmin,imin))*psf(jp,ip)
		    enddo
		enddo
		pixout(j,i)=tot
	    enddo
	enddo
	do i=iy0-nbox2,iy0+nbox2
	    do j=ix0-nbox2,ix0+nbox2
		pixin(j,i)=pixout(j,i)
	    enddo
	enddo
	return
	end

*  this subroutine deletes bits from an i*2 array data(nx,ny) that
*  the fortran unit iun tells it to.ndel objects removed

	subroutine delpix(data,nx,ny,iun,ndel)
	real data(4096,4096)
	real del(6)
	ndel=0
	pi=3.14159265359
	lindel=0
	do nline=1,1000
	    lindel=lindel+1

*  read line from deletions file

	    read(unit=iun,rec=lindel,err=100) (del(j),j=1,6)

*  radius of deletion circle

	    rad=sqrt(del(1)/pi)
	    ir=nint(rad)

*  x and y coordinates of deletions circle centre

	    ix0=int(del(4))
	    iy0=int(del(5))

*  do the deletions

	    do k=1,2*ir
		do l=1,2*ir
		    i=ix0-ir+l
		    j=iy0-ir+k
		    xk=k
		    xl=l
		    xd2 =(xk-rad) *(xk-rad) +(xl-rad) *(xl-rad)
		    if(xd2.le.rad*rad) then
			if(i.ge.1.and.i.le.nx.and.j.ge.1.and.j
     &			.le.ny) then
			    data(i,j)=0
			endif
		    endif
		enddo
	    enddo
	    ndel=ndel+1
	enddo
 100	return
	end
