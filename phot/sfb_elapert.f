      real data(4096*4096),prf(1000,18)
      character file*80

      integer status,unit,readwrite,blocksize,naxes(2),bitpix
      integer naxis,pc,gc
      logical simple,extend

      n=iargc()              ! command line read
      call getarg(1,file)
      if(file.eq.'-h ') then
        print*, ' '
        print*, 'Usage: quick_elapert file_name alpha mu_o',
     *          ' re se sky scale zpt'
        print*, ' '
        goto 999
      endif

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
      nullval=sqrt(-1.)
      call ftgpve(unit,1,1,nx*ny,nullval,data,anynull,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)
      if(status.gt.0) call printerror(status)

      pi=3.1415926536
      open(unit=1,file=file(1:ic)//'prf')
      npts=0
      do while (.true.)
        npts=npts+1
        read(1,*,end=10) (prf(npts,i),i=1,18)
      enddo
10    npts=npts-1
      close(unit=1)
      call getarg(2,file)
      read(file,*) alpha
      sstore=1.0857/alpha
      call getarg(3,file)
      read(file,*) cstore
      call getarg(4,file)
      read(file,*) re
      call getarg(5,file)
      read(file,*) se
      call getarg(6,file)
      read(file,*) sky
      call getarg(7,file)
      read(file,*) scale
      call getarg(8,file)
      read(file,*) zpt

* output radius, integrated mag, area in pixels, sfb of annulus, exp fit luminosity
      print*, ' radius         mag              area           xsfb',
     *        '            expm'
      lct=0
      do n=2,npts
        if(prf(n,4) < 3) goto 100
        xc=prf(n,15)
        yc=prf(n,16)
        xint=0.
        nct=0
        nct_tot=0
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
            if((x**2+y**2)**.5.le.r) then
              nct_tot=nct_tot+1
              if(data(i+nx*(j-1)).eq.data(i+nx*(j-1))) then
                xint=xint+data(i+nx*(j-1))-sky
                nct=nct+1
* key point here, if pixel masked sub in the prf value
              else
                xint=xint+prf(n,1)-sky
                nct=nct+1
              endif
            endif
          enddo
        enddo

* let prf intensities set aperture lum, use area of annulus
        t1=(1.-prf(n,13))*prf(n,4)**2
        t2=(1.-prf(n-1,13))*prf(n-1,4)**2
        area=pi*(t1-t2)
        xsfb=((prf(n,1)+prf(n-1,1))/2.-sky)*area
        if(xsfb <= 0) xsfb=1.

* let exp fit intensities set aperture lum
        if(cstore.ne.0.) then
          xnt=cstore+sstore*(scale*(prf(n,4)+prf(n-1,4))/2.)
          xnt=-0.4*xnt
          xnt1=10.**(xnt)
        else
          xnt1=0.
        endif

        if(re.ne.0.) then
          rr=scale*(prf(n,4)+prf(n-1,4))/2.
          xnt=se+8.325*((rr/re)**0.25-1.)
          xnt=-0.4*xnt
          xnt2=10.**xnt
        else
          xnt2=0.
        endif

        if(xnt1.ne.0.or.xnt2.ne.0) then
          xnt=-2.5*alog10(xnt1+xnt2)
          z=scale*scale*(10.**((xnt-zpt)/-2.5))
          z=z*area
          if(z.eq.0) z=1.
          write(*,'(7(1pe16.8))') prf(n,4),-2.5*alog10(xint),
     *           float(nct),-2.5*alog10(xsfb),-2.5*alog10(z)
        else
          write(*,'(7(1pe16.8))') prf(n,4),-2.5*alog10(xint),
     *           float(nct),-2.5*alog10(xsfb)
        endif
        lct=nct_tot
100   enddo

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
