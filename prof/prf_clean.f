	real data(4098*4098),images(18),pix(4098*4098)
      integer*2 xp(4098*4098),yp(4098*4098)
	character file*80,out*80,op*2

      integer status,unit,readwrite,blocksize,naxes(2),bitpix
      integer naxis,pc,gc
      logical simple,extend

      n=iargc()
      call getarg(1,op)

      if(op =='-h' .or. n < 1) then
        print*, ' '
        print*, 'Usage: prf_clean op data_file prf_file sigma no_clean'
        print*, ' '
        print*, 'clean using .prf file, no clean inside no_clean_radius'
        print*, ' '
        print*, 'options -h = this message'
        print*, '        -f = full frame clean'
        print*, '        -s = stop at outer ellipse'
        goto 999
      endif
      call getarg(2,out)

      status=0
      call ftgiou(unit,status)
      call ftopen(unit,out,readwrite,blocksize,status)
      call ftghpr(unit,3,simple,bitpix,naxis,naxes,pc,gc,extend,status)
      nx=naxes(1)
      ny=naxes(2)
      dumnull=-1.
      nullval=sqrt(dumnull)
      call ftgpve(unit,1,1,nx*ny,nullval,data,anynull,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)
      if(status.gt.0) call printerror(status)

      call getarg(3,file)
      open(unit=1,file=file)
      do while (.true.)
        read(1,*,end=100) images
        if(images(4).gt.5) goto 100
      enddo
100   last=images(4)

      call getarg(4,file)
      read(file,*) sig
      call getarg(5,file)
      read(file,*) clean_rad
	pi=3.1415926536
      do while (.true.)
        read(1,*,end=888) images
        if(images(4).le.clean_rad) goto 777
        d=pi*(-images(14)/180.)
        npts=0
        xstep=images(4)-last
        a1=images(4)-xstep/2
	  a2=images(4)+xstep/2
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
          if(pix(l).ne.pix(l)) then
            call kill_pix(data,nx,ny,xp(l),yp(l))
          endif
	  enddo
        images(1)=xmean2
        images(5)=sig2
        images(7)=-its
200     format(18(1pe16.8))
777     last=images(4)
      enddo
888   close(unit=1)

      if(op == '-f') then
	  do j=1,ny
	    y=j-images(16)
	    do i=1,nx
	      x=i-images(15)
            r=(x**2+y**2)**0.5
	      if(x.ne.0) then
	        t=atan(y/x)
	      else
	        t=pi/2.
	      endif
	      c1=b2*(cos(t))**2+a2*(sin(t))**2
	      c2=(a2-b2)*2*sin(t)*cos(t)
	      c3=b2*(sin(t))**2+a2*(cos(t))**2
	      c4=a2*b2
	      r2=(c4/(c1*(cos(d))**2+c2*sin(d)*cos(d)+c3*(sin(d))**2))**.5
	      if(r.ge.r2) then
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
          if(pix(l).ne.pix(l)) then
            call kill_pix(data,nx,ny,xp(l),yp(l))
          endif
	  enddo
      endif

      call ftgiou(unit,status)
      do idot=1,80
        if(out(idot:idot).eq.'.') exit
      enddo
      call ftopen(unit,out(1:idot)//'prf_clean',1,blocksize,status)
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
      call ftinit(unit,out(1:idot)//'prf_clean',1,status)
      call ftphpr(unit,simple,bitpix,naxis,naxes,0,1,extend,status)
      call ftppre(unit,1,1,nx*ny,data,status)
      call ftclos(unit,status)     
      call ftfiou(unit,status)
      if(status.gt.0) call printerror(status)

999   end

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
      dumnull=-1.
      do while (xold.ne.xmean2)
        xold=xmean2
        its=its+1
        dum=0.
        npts2=0
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

      subroutine kill_pix(data,nx,ny,ik,jk)
      integer*2 ik,jk
      real data(nx,ny)

      i1=ik-2
      if(i1.le.0) i1=1
      i2=ik+2
      if(i2.ge.nx) i2=nx
      j1=jk-2
      if(j1.le.0) j1=1
      j2=jk+2
      if(j2.ge.ny) j2=ny
      dumnull=-1.
      do j=j1,j2
        do i=i1,i2
          data(i,j)=sqrt(dumnull)
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
