      real data(4096*4096),prf(1000,18)
      character file*80,op*2

      integer status,unit,readwrite,blocksize,naxes(2),bitpix
      integer naxis,pc,gc
      logical simple,extend

      n=iargc()              ! command line read
      call getarg(1,op)
      if((op.eq.'-h ').or.(op(1:1).ne.'-')) then
        print*, ' '
        print*, 'Usage: elapert option file_name xc yc rstop'
        print*, ' '
        print*, 'Options: -h = this mesage'
        print*, '         -p = use .prf ellipses'
        print*, '         -c = use circlar apertures, needs'
        print*, '              xc, yc & rstop'
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
      open(unit=1,file=file(1:ic)//'sky')
      read(1,*) sky
      close(unit=1)

      status=0
      call ftgiou(unit,status)
      call ftopen(unit,file,readwrite,blocksize,status)
      call ftghpr(unit,3,simple,bitpix,naxis,naxes,pc,gc,extend,status)
      nx=naxes(1)
      ny=naxes(2)
      nullval=sqrt(-1.)
      call ftgpve(unit,1,1,nx*ny,nullval,data,anynull,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)
      if(status.gt.0) call printerror(status)

* output radius, integrated mag, area in pixels, sfb of annulus, exp fit luminosity
      write(*,*) 'radius mag area xsfb expm'
      pi=3.1415926536
      if(op == '-p') then
        open(unit=1,file=file(1:ic)//'prf')
        npts=0
        do while (.true.)
          npts=npts+1
          read(1,*,end=10) (prf(npts,i),i=1,18)
        enddo
10      npts=npts-1
        close(unit=1)
        open(unit=1,file=file(1:ic)//'sfb',err=11)
        read(1,*) cstore,alpha
        sstore=1.0857/alpha
        close(unit=1)
        open(unit=1,file=file(1:ic)//'cal',err=11)
        read(1,*) scale,zpt
        close(unit=1)
        goto 12
11      cstore=0.
        sstore=0.

12      lct=0.
        do n=2,npts
          xc=prf(n,15)
          yc=prf(n,16)
          xint=0.
          nct=0
          i1=max(1,xc-prf(n,4)-5)
          i2=min(nx,xc+prf(n,4)+5)
          j1=max(1,yc-prf(n,4)-5)
          j2=min(ny,yc+prf(n,4)+5)
          do j=j1,j2
            do i=i1,i2
              x=i-xc
              y=j-yc
              th=90.-180.*atan((j-xc)/(i-yc))/pi
              call findr(r,th*pi/180.,1.-prf(n,13),prf(n,4),
     *                   -prf(n,14)*pi/180.,prf(n,15),prf(n,16))
              if((x**2+y**2)**.5.le.r.and.
     *         data(i+nx*(j-1)).eq.data(i+nx*(j-1))) then
                xint=xint+data(i+nx*(j-1))-sky
                nct=nct+1
              endif
            enddo
          enddo

* let prf intensities set aperture lum
          xsfb=((prf(n,1)+prf(n-1,1))/2.-sky)*(nct-lct)
          if(xsfb <= 0) xsfb=1.
* let exp fit intensities set aperture lum
          if(sstore == 0.) then
            z=1.
          else
            r=prf(n,4)
            z=scale*scale*(10.**(((r*scale*sstore+cstore)-zpt)/-2.5))
            z=z*(nct-lct)
          endif
          if(z <= 0) z=1.

          if(nct > 0) then
          write(*,'(7(1pe16.8))') prf(n,4),-2.5*alog10(xint),
     *         float(nct),-2.5*alog10(xsfb),-2.5*alog10(z)
          endif
          lct=nct
        enddo

      else
        call getarg(3,file)
        read(file,*) xc
        call getarg(4,file)
        read(file,*) yc
        call getarg(5,file)
        read(file,*) rstop
        z=1.
        do while (z < rstop)
          z=z+z*0.1
          xint=0.
          nct=0
          i1=max(1,xc-z-5)
          i2=min(nx,xc+z+5)
          j1=max(1,yc-z-5)
          j2=min(ny,yc+z+5)
          do j=j1,j2
            do i=i1,i2
              x=i-xc
              y=j-yc
              th=90.-180.*atan((j-xc)/(i-yc))/pi
              call findr(r,th*pi/180.,1.,z,0.,xc,yc)
              if((x**2+y**2)**.5.le.r.and.
     *         data(i+nx*(j-1)).eq.data(i+nx*(j-1))) then
                xint=xint+data(i+nx*(j-1))-sky
                nct=nct+1
              endif
            enddo
          enddo
          if(nct > 0) then
          write(*,'(3(1pe16.8))') z,-2.5*alog10(xint),float(nct)
          endif
        enddo
      endif

999   end

      subroutine findr(r,t,eps,a,d,xc,yc)
      pi=3.1415926536
      bsq=(eps*a)**2
      asq=a**2
      c1=bsq*(cos(t))**2+asq*(sin(t))**2
      c2=(asq-bsq)*2*sin(t)*cos(t)
      c3=bsq*(sin(t))**2+asq*(cos(t))**2
      c4=asq*bsq
      r=(c4/(c1*(cos(d))**2+c2*sin(d)*cos(d)+c3*(sin(d))**2))**.5
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
