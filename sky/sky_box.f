      real data(8192*8192),pix(8192*8192),prf(18)
      real array(5000),sky(10000),skysig(10000)
      character file*100,op*2

      integer status,unit,unit2,readwrite,blocksize,naxes(2),nfound,bitpix
      integer naxis,pc,gc
      logical simple,extend

      n=iargc()
      call getarg(1,op)
      if((op.eq.'-h') .or. (op(1:1).ne.'-')) then
        print*, ' '
        print '(a)', 'Usage: sky_box option file_name box_size prf_file'
        print*, '      or'
        print '(a)', '       sky_box -c file_name x1 x2 y1 y2'
        print*, ' '
        print '(a)', 'Options: -h = this message'
        print '(a)', '         -f = first guess of border'
        print '(a)', '         -r = full search, needs box_size'
        print '(a)', '              and prf_file'
        print '(a)', '         -t = full search, needs box_size'
        print '(a)', '         -c = find sky for inner region (flats)'
        print '(a)', '              needs x1,x2,y1,y2 boundarys'
        print '(a)', '         -s = full search, all pixels'
        print '(a)', '         -x = use sky boxes (sky.tmp)'
        print*, ' '
        print '(a)', 'Output: mean, sig, iter mean, iter sig, npts, its'
        print*, ' '
        goto 999
      endif
      call getarg(2,file)

      do ic=1,80
        if(file(ic:ic).eq.'.') exit    
      enddo
      if(ic == 81) then
        print*, 'no file suffix, aborting'
        goto 999
      endif

      status=0
      call ftgiou(unit,status)
      call ftopen(unit,file,readwrite,blocksize,status)
      call ftghpr(unit,3,simple,bitpix,naxis,naxes,pc,gc,extend,status)
      nx=naxes(1)
      ny=naxes(2)
      dumnull=-1.
      nullval=sqrt(dumnull)
      call ftgpve(unit,1,1,nx*ny,nullval,pix,anynull,status)

      if(op == '-r') open(unit=1,file=file(1:ic)//'prf')

      if(op == '-c') then
        call getarg(3,file)
        read(file,*) ix1
        if(ix1.le.0) ix1=1
        call getarg(4,file)
        read(file,*) ix2
        if(ix2.ge.nx) ix2=nx
        call getarg(5,file)
        read(file,*) iy1
        if(iy1.le.0) iy1=1
        call getarg(6,file)
        read(file,*) iy2
        if(iy2.ge.ny) iy2=ny
      else
        ix1=1
        ix2=nx
        iy1=1
        iy2=ny
        call getarg(3,file)
        if(file.ne.' ') then
          read(file,*) ibox
        else
          ibox=10
        endif
      endif

      if(op == '-c') then
        npts=0
        do j=iy1,iy2
          do i=ix1,ix2
            npts=npts+1
            data(npts)=pix((j-1)*nx+i)
          enddo
        enddo
        call xits(data,npts,3.,xmean1,sig1,xmean2,sig2,npts2,its)
        if(sig2 < 0.01 .or. xmean2 > 1.e3) then
          print '(4(1pe12.4),2i8)', xmean1,sig1,xmean2,sig2,npts2,its
        else
          print '(4f10.2,2i8)', xmean1,sig1,xmean2,sig2,npts2,its
        endif
        goto 999
      endif

      if(op == '-s') then
         npts=0
         do j=1,ny
           do i=1,nx
             npts=npts+1
             data(npts)=pix((j-1)*nx+i)
           enddo
         enddo
        call xits(data,npts,3.,xmean1,sig1,xmean2,sig2,npts2,its)
        if(sig2 < 0.01 .or. xmean2 > 1.e3) then
          print '(4(1pe12.4),2i8)', xmean1,sig1,xmean2,sig2,npts2,its
        else
          print '(4f10.2,2i8)', xmean1,sig1,xmean2,sig2,npts2,its
        endif
        goto 999
      endif

      if(op == '-f') then
         npts=0
         do j=10,20
           do i=10,nx-10
             npts=npts+1
             data(npts)=pix((j-1)*nx+i)
           enddo
         enddo
         do j=10,ny-10
           do i=10,20
             npts=npts+1
             data(npts)=pix((j-1)*nx+i)
           enddo
         enddo
         do j=10,ny-10
           do i=nx-20,nx-10
             npts=npts+1
             data(npts)=pix((j-1)*nx+i)
           enddo
         enddo
         do j=ny-20,ny-10
           do i=10,nx-10
             npts=npts+1
             data(npts)=pix((j-1)*nx+i)
           enddo
         enddo
        if(npts.eq.0) then
          print*, 'sky_box npts error'
          goto 999
        endif
        its=-1
        call xits(data,npts,2.5,xmean1,sig1,xmean2,sig2,npts2,its)
        call xits(data,npts,3.,xmean1,sig1,xmean2,sig2,npts2,its)
        if(sig2 < 0.01 .or. xmean2 > 1.e3) then
          print '(4(1pe12.4),2i8)', xmean1,sig1,xmean2,sig2,npts2,its
        else
          print '(4f10.2,2i8)', xmean1,sig1,xmean2,sig2,npts2,its
        endif
        goto 999
      endif

      if(op.eq.'-x') then
        open(unit=1,file='sky.tmp')
        do while (.true.)
          read(1,*,end=150) ix,jx,ibox
          npts=0
          do j=jx-ibox/2,jx+ibox/2
            do i=ix-ibox/2,ix+ibox/2
              if( pix((j-1)*nx+i) == pix((j-1)*nx+i) ) then
                npts=npts+1
                array(npts)=pix((j-1)*nx+i)
              endif
            enddo
          enddo
          if(npts > ibox*ibox/2.) then
            call xits(array,npts,3.,xmean1,sig1,xmean2,sig2,npts2,its)
            if(npts2 > 5) then
              nsky=nsky+1
              sky(nsky)=xmean2
              skysig(nsky)=sig2
            endif
          endif
        enddo
150     close(unit=1)
      endif

      if(op.eq.'-r'.or.op.eq.'-t') then
        if(op.eq.'-r') then
          do while (.true.)
            read(1,*,end=100,err=100) prf
          enddo
100       close(unit=1)
        endif

        nctx=nx/ibox
        ncty=ny/ibox
        nstep=nx/nctx
        nsky=0
        do jbx=1,ncty-1
          jx=jbx*nstep
          do ibx=1,nctx-1
            ix=ibx*nstep
            npts=0
            if(op.eq.'-r') then
              call findr(prf(15),prf(16),prf(4),prf(13),prf(14),ix,jx,r)
              if(((prf(15)-ix)**2+(prf(16)-jx)**2)**0.5.le.r) goto 200
            endif
            do j=jx-ibox/2,jx+ibox/2
              do i=ix-ibox/2,ix+ibox/2
                if( pix((j-1)*nx+i) == pix((j-1)*nx+i) ) then
                  npts=npts+1
                  array(npts)=pix((j-1)*nx+i)
                endif
              enddo
            enddo
            if(npts < ibox*ibox/2.) goto 200
            call xits(array,npts,3.,xmean1,sig1,xmean2,sig2,npts2,its)
*            write(*,*) ix,jx,xmean2,sig2,npts2,its,
*     *                ((prf(15)-ix)**2+(prf(16)-jx)**2)**0.5,r
            if(npts2 > 5) then
              nsky=nsky+1
              sky(nsky)=xmean2
              skysig(nsky)=sig2
*              write(*,*) 'mark ',ix,jx,' dot blue 1'
            endif
200         continue
          enddo
        enddo
      endif

      if(nsky <= 1) then
        print*, 'error'
        goto 999
      endif
      call xits(sky,nsky,3.,xmean1,sig1,xmean2,sig2,npts2,its)
      call xits(skysig,nsky,3.,ymean1,sig1,ymean2,ysig2,npts2,its)
* write sky,skysig,sig on means,number of boxes used,iterations,number of boxes found
* nope, write sky,skysig, then box sky, skysig and num of boxes
      if(sig2 < 0.01 .or. xmean2 > 1.e3) then
        print '(4(1pe12.4),2i8)', xmean1,sig1,xmean2,sig2,npts2,its
      else
        print '(4f10.2,2i8)', xmean1,sig1,xmean2,sig2,npts2,its
      endif

* obsolete, use xml file
*        if(op.eq.'-s') then
*          call ftgiou(unit2,status)
*          call ftinit(unit2,'skybox.fits',1,status)
*          call ftphpr(unit2,simple,bitpix,naxis,naxes,0,1,extend,status)
*        call ftcopy(unit,unit2,0,status)
*        call ftcrhd(unit2,status)
*          call ftpkyf(unit2,'SKY1',xmean1,2,
*     *            'Sky value 1 (SKYBOX)',status)
*          call ftppre(unit2,1,1,nx*ny,pix,status)
*          call ftclos(unit2,status)
*          call ftfiou(unit2,status)
*        endif

999   call ftclos(unit,status)
      call ftfiou(unit,status)

      end

      subroutine findr(xc,yc,rad,e,pa,i,j,r)
      pi=3.1415926536
*      a=(area/(pi*e))**0.5
      a=rad
      rat=1.-e
      d=-pa*pi/180.
      x=i-xc
      y=j-yc
      b=(rat*a)**2
      a=a**2
      if(x.ne.0) then
        t=atan(y/x)
      else
        t=pi/2.
      endif
      c1=b*(cos(t))**2+a*(sin(t))**2
      c2=(a-b)*2*sin(t)*cos(t)
      c3=b*(sin(t))**2+a*(cos(t))**2
      c4=a*b
      r=(c4/(c1*(cos(d))**2+c2*sin(d)*cos(d)+c3*(sin(d))**2))**.5
      return
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
      npts2=0
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
      xold=xmean2+0.001*xmean2
      if(its.eq.-1) then
* its=-1, no abs check on difference
        its=0
        do while (xold.ne.xmean2)
          xold=xmean2
          its=its+1
          dum=0.
          npts2=0
          do j=1,npts
            if((data(j).eq.data(j)).and.
     *         (data(j).ge.xold-xsig*sig2)) then
              npts2=npts2+1
              dum=dum+data(j)
            endif
          enddo
          xmean2=dum/npts2
          dum=0.
          do j=1,npts
            if((data(j).eq.data(j)).and.
     *         (data(j).ge.xold-xsig*sig2)) then
              dum=dum+(data(j)-xmean2)**2
            endif
          enddo
          sig2=(dum/(npts2-1))**.5
          if(sig2.eq.0.) then
            print*, 'sky error in xits, sigma zero'
            stop
          endif
        enddo
      else
        its=0
        do while (xold.ne.xmean2)
          xold=xmean2
          its=its+1
          dum=0.
          npts2=0
          do j=1,npts
            if((data(j).eq.data(j)).and.
     *         (abs(data(j)-xold).le.xsig*sig2)) then
              npts2=npts2+1
              dum=dum+data(j)
            endif
          enddo
          xmean2=dum/npts2
          dum=0.
          do j=1,npts
            if((data(j).eq.data(j)).and.
     *         (abs(data(j)-xold).le.xsig*sig2)) then
              dum=dum+(data(j)-xmean2)**2
            endif
          enddo
          sig2=(dum/(npts2-1))**.5
        enddo
      endif
      return
      end
