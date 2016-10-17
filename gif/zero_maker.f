      real pix(1024,1024)
      real xdata(1024*1024)
      real tr(6),prf(1000,18),c(10)
      character*2 op
      character*30 file,outfile

      integer status,unit,readwrite,blocksize,naxes(2),bitpix
      integer naxis,pc,gc
      logical simple,extend   ! block of cfitsio variables

      call getarg(1,file)
      do i=1,30
        if(file(i:i) == '.') exit
      enddo
      iend=i-1

      pi=3.1415926536
      status=0
      call ftgiou(unit,status)
      if(ilong == 0) then
      call ftopen(unit,file,readwrite,blocksize,status)
      else
      call ftopen(unit,file,readwrite,blocksize,status)
      endif
      call ftghpr(unit,3,simple,bitpix,naxis,naxes,pc,gc,extend,status)
      nx=naxes(1)
      ny=naxes(2) ! data in xdata, nx & ny are array size
      nullval=sqrt(-1.)
      call ftgpve(unit,1,1,nx*ny,nullval,xdata,anynull,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)
      do j=1,ny
        do i=1,nx
          if(xdata(i+nx*(j-1)).ne.xdata(i+nx*(j-1))) then
            pix(i,j)=1.
          else
            pix(i,j)=0.
          endif
        enddo
      enddo
      tr(2)=1.
      tr(6)=1.

      call getarg(2,file)
      read(file,*) izoom
      r1=1.
      r2=0.
      do i=1,10
        c(i)=0.1*i*(r1-r2)+r2
      enddo
      if(izoom .le. 1) then
        izoom=1
        xc=nx/2.
        yc=ny/2.
      else
        call getarg(3,file)
        read(file,*) xc
        call getarg(4,file)
        read(file,*) yc
      endif

      call pgbegin(7,'zero.gif/gif',1,1)
      call pgask(0)
      call pgscr(0,1.,1.,1.)
      call pgscr(1,0.,0.,0.)
      call pgscf(1)
      call pgsch(1.5)

      if(izoom == 1) then
        xaspect=ny/nx
        i1=1
        i2=nx
        j1=1
        j2=ny
      else
        xaspect=1.
        xstep=(nx/2.)/izoom
        i1=xc-xstep
        if(i1 < 1) then
          i1=1
          i2=2.*xstep
        endif
        i2=xc+xstep
        if(i2 > nx) then
          i2=nx
          i1=nx-2.*xstep
        endif
        j1=yc-xstep
        if(j1 < 1) then
          j1=1
          j2=2.*xstep
        endif
        j2=yc+xstep
        if(j2 > ny) then
          j2=ny
          j1=ny-2.*xstep
        endif
      endif
      call pgadvance
      call pgpap(7.,xaspect)
      call gray(pix,i1,i2,j1,j2,r1,r2)

999   call pgend()
      end

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

      subroutine edraw(eps,a,d,xc,yc)
      pi=3.1415926536
      bsq=(eps*a)**2
      asq=a**2
      th=0.
      step=2.
      do i=1,365/step+step
        th=th+step
        t=th*pi/180.
        c1=bsq*(cos(t))**2+asq*(sin(t))**2
        c2=(asq-bsq)*2*sin(t)*cos(t)
        c3=bsq*(sin(t))**2+asq*(cos(t))**2
        c4=asq*bsq
        r=(c4/(c1*(cos(d))**2+c2*sin(d)*cos(d)+c3*(sin(d))**2))**.5
        if(th == step) then
          call pgmove(r*cos(t)+xc,r*sin(t)+yc)
        else
          call pgdraw(r*cos(t)+xc,r*sin(t)+yc)
        endif
      enddo  
      return
      end   

      subroutine gray(pix,i1,i2,j1,j2,r1,r2)
      real pix(1024,1024),tr(6)

      tr(2)=1.
      tr(6)=1.
*      call pgsvp(0.0,1.0,0.0,1.0)
*      call pgqvsz(1,w1,w2,w3,w4)
      call pgwindow(float(i1),float(i2),float(j1),float(j2))
      call pggray(pix,1024,1024,i1,i2,j1,j2,r1,r2,tr)
      call pgbox('bcnst',0.,0,'bcnst',0.,0)
      return
      end

      subroutine eplot(prf,npts,i1,i2,j1,j2)
      real prf(1000,18)
      character*80 strng

      pi=3.1415926536
      call pgwindow(float(i1),float(i2),float(j1),float(j2))
      call pgbox('bcnst',0.,0,'bcnst',0.,0)
      n=0
      do i=1,npts
        if(prf(i,4) > (i2-i1)*0.05) then
          if(prf(i,7) > 0) then
            call pgsci(4)
          else
            call pgsci(2)
          endif
          call edraw(1.-prf(i,13),prf(i,4),-prf(i,14)*pi/180.,
     *               prf(i,15),prf(i,16))
        endif
      enddo
      call pgsci(1)
      return
      end
