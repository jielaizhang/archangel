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
        print*, 'if fit vars = 0, fit = xsfb'
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
      dumnull=-1.
      nullval=sqrt(dumnull)
      call ftgpve(unit,1,1,nx*ny,nullval,data,anynull,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)
      if(status.gt.0) call printerror(status)

      pi=3.1415926536
*      open(unit=1,file=file(1:ic)//'prf')
      open(unit=1,file='tmp.prf')
      npts=0
      read(1,'(1x)')
      do while (.true.)
        npts=npts+1
        read(1,*,end=10) (prf(npts,i),i=1,18)
      enddo
10    npts=npts-1
      close(unit=1)
      call getarg(2,file)
      read(file,*) alpha
      if(alpha.ne.0) then
        sstore=1.0857/alpha
      else
        sstore=0.
      endif
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
* assuming that elapert.py was run 1st for correct headers

*      if((cstore == 0.) .and. (re == 0.)) then
*        print*, ' radius         mag              area           xsfb'
*      else
*        print*, ' radius         mag              area           xsfb',
*     *        '            expm'
*      endif
      lct=0
      xint2=0.
* note the loop does not start unless radius is greater than 20 pixels

      do n=2,npts
        if(prf(n,4) < 20.) goto 100
        xc=prf(n,15)
        yc=prf(n,16)
        xint=0.
        nct=0
        nct_tot=0
*        i1=max(1,xc-prf(n,4)-5)
*        i2=min(nx,xc+prf(n,4)+5)
*        j1=max(1,yc-prf(n,4)-5)
*        j2=min(ny,yc+prf(n,4)+5)
        i1=xc-prf(n,4)-5
        i2=xc+prf(n,4)+5
        j1=yc-prf(n,4)-5
        j2=yc+prf(n,4)+5

        if(alpha.eq.0.and.cstore.eq.0.and.re.eq.0.and.se.eq.0) then
          do j=j1,j2
            do i=i1,i2
              x=i-xc
              y=j-yc
              call findr(xc,yc,prf(n,4),prf(n,13),prf(n,14),i,j,r)
              if((x**2+y**2)**.5.le.r) then
                nct_tot=nct_tot+1
                if((j.gt.1.and.j.lt.ny.and.i.gt.1.and.i.lt.nx).and.
     *          (data(i+nx*(j-1)).eq.data(i+nx*(j-1)))) then
                  nct=nct+1
                  xint=xint+data(i+nx*(j-1))-sky
                endif
              endif
            enddo
          enddo

        else 
          do j=j1,j2
            do i=i1,i2
              x=i-xc
              y=j-yc
              call findr(xc,yc,prf(n,4),prf(n,13),prf(n,14),i,j,r)
              if((x**2+y**2)**.5.le.r) then
                nct_tot=nct_tot+1
                nct=nct+1
*             if pixels outside frame, or NaN, use prf interpolation
                if((j.lt.1.or.j.gt.ny.or.i.lt.1.or.i.gt.nx).or.
     *          (data(i+nx*(j-1)).ne.data(i+nx*(j-1)))) then
                  do m=2,npts
                    if(prf(m,4).gt.r) then
                      zz=(r-prf(m,4))/(prf(m-1,4)-prf(m,4))
                      zz=prf(m,1)+(prf(m-1,1)-prf(m,1))*zz
                      goto 666
                    endif
                  enddo
666               if(zz.ge.sky) xint=xint+zz-sky
                else
                  xint=xint+data(i+nx*(j-1))-sky
                endif
              endif
            enddo
          enddo
        endif

* let prf intensities set aperture lum, use area of annulus
        t1=(1.-prf(n,13))*prf(n,4)**2
        t2=(1.-prf(n-1,13))*prf(n-1,4)**2
        area=pi*(t1-t2)
        if((prf(n,1)+prf(n-1,1))/2.-sky.le.0) then
          xsfb=xsfb_old
        else
          xsfb=((prf(n,1)+prf(n-1,1))/2.-sky)*area
          xsfb_old=xsfb
        endif

* let fit intensities set aperture lum, bulge+disk, deV or Sersic
        xnt1=0.
        if(alpha.ne.0.and.cstore.ne.0) then
          xnt=cstore+sstore*(scale*(prf(n,4)+prf(n-1,4))/2.)
          xnt=-0.4*xnt
          xnt1=10.**(xnt)
        endif

        xnt2=0.
        if(re.ne.0.) then
          rr=scale*(prf(n,4)+prf(n-1,4))/2.
          xnt=se+8.325*((rr/re)**0.25-1.)
          xnt=-0.4*xnt
          xnt2=10.**xnt
        endif

        if(alpha.eq.0.and.cstore.ne.0.) then
          rr=scale*(prf(n,4)+prf(n-1,4))/2.
          b=2.*cstore-(1./3.)
          xnt=exp(-b*((rr/re)**(1./cstore)-1.))
          xnt2=((10.**(se/(-2.5)))*xnt)
        endif

        if(xnt1.ne.0.or.xnt2.ne.0) then
          xnt=-2.5*alog10(xnt1+xnt2)
          z=scale*scale*(10.**((xnt-zpt)/(-2.5)))
          z=z*area
          if(z <= 0) z=1.
*          if(xsfb <= 0) xsfb=z
          write(*,'(5(1pe16.8)1x,a)') prf(n,4),-2.5*alog10(xint),
     *           float(nct),-2.5*alog10(xsfb),-2.5*alog10(z),'1'
        elseif(alpha.eq.0.and.cstore.eq.0.and.re.eq.0.and.se.eq.0) then
          write(*,'(5(1pe16.8),1x,a)') prf(n,4),-2.5*alog10(xint),
     *           float(nct),-2.5*alog10(xsfb),-2.5*alog10(xsfb),'1'
        else
          write(*,'(5(1pe16.8)1x,a)') prf(n,4),-2.5*alog10(xint),
     *           float(nct),-2.5*alog10(xsfb),-2.5*alog10(xsfb),'1'
        endif
*        print*, xint-xint2,z,-2.5*alog10(xint-xint2),-2.5*alog10(z)
        lct=nct_tot
        xint2=xint
100   enddo

* if only elliptical fit, abort

      if(alpha == 0.) goto 999
      delta=prf(npts,4)-prf(npts-1,4)
      xlast=prf(npts,4)
      zlast=z
      xc=prf(npts,15)
      yc=prf(npts,16)
      do n=1,100
        delta=delta+0.1*delta
        r=xlast+delta
        if(r.ge.(nx*ny)**0.5) goto 999
        t1=(1.-prf(npts,13))*r**2
        t2=(1.-prf(npts,13))*xlast**2
        area=pi*(t1-t2)

        if(cstore.ne.0.) then
          xnt=cstore+sstore*(scale*(r+xlast)/2.)
          xnt=-0.4*xnt
          xnt1=10.**(xnt)
        else
	    xnt1=0.
	  endif

        if(re.ne.0.) then
          rr=scale*(r+xlast)/2.
          xnt=se+8.325*((rr/re)**0.25-1.)
          xnt=-0.4*xnt
          xnt2=10.**xnt
        else
          xnt2=0.
        endif

        xnt=-2.5*alog10(xnt1+xnt2)
        z=scale*scale*(10.**((xnt-zpt)/(-2.5)))
        z=z*area
        if(z.eq.0) z=1.

        xint=0.
        nct=0
        nct_tot=0
        i1=xc-r-5
        i2=xc+r+5
        j1=yc-r-5
        j2=yc+r+5

        do j=j1,j2
          do i=i1,i2
            x=i-xc
            y=j-yc
        call findr(xc,yc,prf(npts,4),prf(npts,13),prf(npts,14),i,j,rr)
            if((x**2+y**2)**.5.le.rr) then
              nct_tot=nct_tot+1
              nct=nct+1
*             if pixels outside frame, or NaN, use prf interpolation
              if((j.lt.1.or.j.gt.ny.or.i.lt.1.or.i.gt.nx).or.
     *          (data(i+nx*(j-1)).ne.data(i+nx*(j-1)))) then
777             xint=xint+prf(npts,1)-sky
              else
                xint=xint+data(i+nx*(j-1))-sky
              endif
            endif
          enddo
        enddo

        if(-2.5*alog10(z).eq.0) then
           z=zlast
        else
           zlast=z
        endif
 
        write(*,'(5(1pe16.8),1x,a)') r,-2.5*alog10(xint),
     *           pi*t1,-2.5*alog10(z),-2.5*alog10(z),'1'
        test=-2.5*alog10(xint+z)+2.5*alog10(xint)
        if(abs(test) < 0.001) goto 999
        zlast=z
        xlast=r
      enddo

999   end

      subroutine findr(xc,yc,rad,e,pa,i,j,r)
      pi=3.1415926536
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
