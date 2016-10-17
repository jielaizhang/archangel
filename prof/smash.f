	real data(4098*4098),images(18),pix(100000)
      integer*2 xp(100000),yp(100000)
	character file*80,out*80

      integer status,unit,readwrite,blocksize,naxes(2),bitpix
      integer naxis,pc,gc
      logical simple,extend

      n=iargc()
      call getarg(1,out)

      if(out=='-h' .or. n < 1) then
        print*, ' '
        print*, 'Usage: smash data_file prf_file max_radius sigma grow'
        print*, ' '
        print*, 'do isophotes for outer halos'
        print*, 'max_radius = where to stop (nx/2)'
        print*, 'sigma = cleaning sigma (5)'
        print*, 'grow = 0.10 * radius'
        goto 999
      endif

      status=0
      call ftgiou(unit,status)
      call ftopen(unit,out,readwrite,blocksize,status)
      call ftghpr(unit,3,simple,bitpix,naxis,naxes,pc,gc,extend,status)
      nx=naxes(1)
      ny=naxes(2)
      xdum=-1.
      nullval=sqrt(xdum)
      call ftgpve(unit,1,1,nx*ny,nullval,data,anynull,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)
      if(status.gt.0) call printerror(status)

      call getarg(2,file)
	open(unit=1,file=file)
      do while (.true.)
        read(1,*,end=100) images
        write(*,200) images
      enddo
100   start=images(4)
      close(unit=1)
*	open(unit=1,file=file,access='append')

      if(n > 2) then
        call getarg(3,file)
        read(file,*) rx
        call getarg(4,file)
        read(file,*) sig
        call getarg(5,file)
        read(file,*) grow
      else
        rx=nx/2
        sig=5.
        grow=0.10
      endif
      xstep=10.-10.*grow

	pi=3.1415926536
      d=-1.*pi*images(14)/180.
      do while (start.lt.rx)
        npts=0
        xstep=xstep+xstep*grow
        start=start+xstep
        a1=start-xstep/2
	  a2=a1+xstep
	  b1=((1.-images(13))*a1)**2
	  b2=((1.-images(13))*a2)**2
        istrt=images(15)-a2-1
        if(istrt < 1) istrt=1
        jstrt=images(16)-a2-1
        if(jstrt < 1) jstrt=1
        iend=images(15)+a2+1
        if(iend > nx) iend=nx
        jend=images(16)+a2+1
        if(jend > ny) jend=ny
	  a1=a1**2
	  a2=a2**2
	  do j=jstrt,jend
	    y=j-images(16)
	    do i=istrt,iend
	      x=i-images(15)
            r=(x**2+y**2)**0.5
	      if(x.ne.0) then
	        t=atan(y/x)
	      else
	        t=pi/2.
	      endif
	      c1=b1*(cos(t))**2+a1*(sin(t))**2
	      c2=(a1-b1)*2*sin(t)*cos(t)
	      c3=b1*(sin(t))**2+a1*(cos(t))**2
	      c4=a1*b1
	      r1=(c4/(c1*(cos(d))**2+c2*sin(d)*cos(d)+c3*(sin(d))**2))**.5
	      c1=b2*(cos(t))**2+a2*(sin(t))**2
	      c2=(a2-b2)*2*sin(t)*cos(t)
	      c3=b2*(sin(t))**2+a2*(cos(t))**2
	      c4=a2*b2
	      r2=(c4/(c1*(cos(d))**2+c2*sin(d)*cos(d)+c3*(sin(d))**2))**.5
	      if(r.ge.r1.and.r.le.r2) then
              if(data((j-1)*nx+i).eq.data((j-1)*nx+i)) then
                npts=npts+1
                pix(npts)=data((j-1)*nx+i)
                xp(npts)=i
                yp(npts)=j
              endif
            endif
	    enddo
	  enddo
        call xits(pix,npts,sig,xmean1,sig1,xmean2,sig2,npts2,its)
        do l=1,npts
          if(pix(l).ne.pix(l)) call kill_pix(data,nx,ny,xp(l),yp(l))
        enddo
        images(1)=xmean2
        images(3)=sig2
        images(4)=start
        images(7)=-its
        write(*,200) images
200     format(18(1pe16.8))
      enddo
      close(unit=1)

      call ftgiou(unit,status)
      do idot=1,80
        if(out(idot:idot).eq.'.') exit
      enddo
      call ftopen(unit,out(1:idot)//'smash',1,blocksize,status)
      if(status.eq.0) then
          call ftdelt(unit,status) 
      elseif (status .eq. 103) then
          status=0
          call ftcmsg
      else   
          status=0
          call ftcmsg
          call ftdelt(unit,status)
      endif
      call ftfiou(unit,status)
      call ftgiou(unit,status)
      call ftinit(unit,out(1:idot)//'smash',1,status)
      call ftphpr(unit,simple,bitpix,naxis,naxes,0,1,extend,status)
      call ftppre(unit,1,1,nx*ny,data,status)
      call ftclos(unit,status)     
      call ftfiou(unit,status)
      if(status.gt.0) call printerror(status)

999	end

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
        do j=1,npts
          if(data(j).eq.data(j)) then
            if(abs(data(j)-xold).gt.xsig*sig2) then
              data(j)=sqrt(xdum)
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

      subroutine kill_pix(data,nx,ny,ik,jk)
      integer*2 ik,jk
      real data(nx,ny)

      xdum=-1.
      i1=ik-1       
      if(i1.le.0) i1=1
      i2=ik+1
      if(i2.ge.nx) i2=nx
      j1=jk-1     
      if(j1.le.0) j1=1
      j2=jk+1
      if(j2.ge.ny) j2=ny
      do j=j1,j2
        do i=i1,i2
          data(i,j)=sqrt(xdum)
        enddo
      enddo
      return
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
      enddo
      end
