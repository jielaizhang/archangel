      real pix(1024,1024)
      real xdata(1024*1024)
      real tr(6),ims(6),c(10)
      character*30 file,ops

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
      call ftopen(unit,file,readwrite,blocksize,status)
      call ftghpr(unit,3,simple,bitpix,naxis,naxes,pc,gc,extend,status)
      nx=naxes(1)
      ny=naxes(2) ! data in xdata, nx & ny are array size
      nullval=sqrt(-1.)
      call ftgpve(unit,1,1,nx*ny,nullval,xdata,anynull,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)
      tr(2)=1.
      tr(6)=1.

      open(unit=1,file=file(1:iend)//'.sky',status='old',err=50)
      read(1,*,err=50) d1,d2,sky,skysig
50    close(unit=1)

      call getarg(2,ops)
      read(ops,*) xcon
      call getarg(3,ops)
      read(ops,*) izoom
      if(izoom .le. 1) then
        izoom=1
        xc=nx/2.
        yc=ny/2.
      else
        call getarg(4,ops)
        read(ops,*) xc
        call getarg(5,ops)
        read(ops,*) yc
      endif

      if(xcon > 0) then
        r1=sky+xcon*50.*skysig
      else
        r1=sky+50.*skysig/abs(xcon-2)
      endif
      r2=sky-0.05*(r1-sky)
      do i=1,10
        c(i)=0.1*i*(r1-r2)+r2
      enddo
      do j=1,ny
        do i=1,nx
          if(xdata(i+nx*(j-1)).ne.xdata(i+nx*(j-1))) then
            pix(i,j)=r2
          else
            pix(i,j)=xdata(i+nx*(j-1))
          endif
        enddo
      enddo

      call pgbegin(7,'images.gif/gif',1,1)
      call pgask(0)
      call pgscr(0,1.,1.,1.)
      call pgscr(1,0.,0.,0.)
      call pgscf(1)
      call pgsch(1.5)

      if(izoom == 1) then
        xaspect=float(ny)/float(nx)
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
      call pgsci(4)

      open(unit=1,file=file(1:iend)//'.ims',err=999)
      do while (.true.)
        read(1,*,end=999) ims
        call edraw(1.-ims(4),(ims(3)/((1.-ims(4))*pi))**0.5,
     *             -ims(5)*pi/180.,ims(1),ims(2))
      enddo
999   call pgend()
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
