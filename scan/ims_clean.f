      real pix(4096*4096),images(10000,6),tmp(6)
      character file1*100,file2*100,op*2

      integer status,unit,readwrite,blocksize,naxes(2),nfound,bitpix
      integer naxis,pc,gc
      logical simple,extend

      n=iargc()
      call getarg(1,op)
      if((op == '-h') .or. (op(1:1) /= '-')) then
        print*, ' '
        print*, 'Usage: ims_clean op data_file ims_file scale x y r e t'
        print*, ' '
        print*, 'Options: -h = this mesage'
        print*, '         -v = output each iteration'
        print*, '         -q = quiet'
        print*, ' '
        print*, 'note: ims_file is -f output from gasp_images'
        print*, '      scale is scale factor for images'
        print*, '      x and y are coords for object not to delete'
        print*, '      r is outer radius to ignore'
        print*, '      e and t are ellipse ecc and pos angle'
        print*, '      output file = file_name.clean'
        goto 999
      endif

      call getarg(2,file1)
      status=0
      call ftgiou(unit,status)
      call ftopen(unit,file1,readwrite,blocksize,status)
      call ftghpr(unit,3,simple,bitpix,naxis,naxes,pc,gc,extend,status)
      nx=naxes(1)
      ny=naxes(2)
      dumnull=-1.
      nullval=sqrt(dumnull)
      call ftgpve(unit,1,1,nx*ny,nullval,pix,anynull,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)
      if(status.gt.0) call printerror(status)

      call getarg(3,file2)
      open(unit=1,file=file2)
      pi=3.1415926536

* load in parameters from command line, scale factor, x/y center and ellipse parameters

      xfact=1.
      if(n > 3) then
        call getarg(4,file2)
        read(file2,*) xfact
        call getarg(5,file2)
        read(file2,*) xc
        call getarg(6,file2)
        read(file2,*) yc
        call getarg(7,file2)
        read(file2,*) rout
      endif

* read in .ims file, ignore things too flat or with 2 pixels of target

      num=0
      do while (.true.)
        num=num+1
        read(1,*,end=100,err=100) (images(num,i),i=1,6)
        r=((images(num,1)-xc)**2+(images(num,2)-yc)**2)**0.5
        if((images(num,4) > 0.99) .or. 
     *     (r < 10.0)) num=num-1
      enddo
100   num=num-1
      close(unit=1)

* if outer limit radius is zero, clean whole frame, otherwise find gal in .ims file and plan
* to ignore its area during cleaning

      if(rout.ne.0) then
        call getarg(8,file2)
        read(file2,*) xeps
        call getarg(9,file2)
        read(file2,*) e
        do i=1,num
          x=xc-images(i,1)
          y=yc-images(i,2)
          if((x**2+y**2)**0.5.le.10.) then
            nope=i
            goto 150
          endif
        enddo
*150     xa=2.*sqrt(rout/(pi*(1.-xeps)))
150     xa=rout
        e=-e*pi/180.  ! pos angle to radians
      endif

* clean all objects in .ims outside gal ellipse

200   do n=1,num

* determine is center of .ims object is inside gal ellipse

        if(rout == 0) then
          rr=0.
        else
          x=images(n,1)-xc
          y=images(n,2)-yc
          if(x /= 0) then
            t=atan(y/x)
          else 
            t=pi/2.
          endif
          call findr(rr,t,xeps,xa,e,xc,yc)
        endif

        if(((sqrt(x*x+y*y) > 2.*rr) .or. (images(n,4) < 0.05))
     *    .and. (n.ne.nope)) then
          if(op == '-v') print 10, n,num
10        format('cleaning ',i4,' of ',i4)
          eps=images(n,4)-0.20*images(n,4) ! fatten by 20%
          a=xfact*(sqrt(images(n,3)/(pi*(1.-eps))))
          b=(a*(1.-eps))
          i1=images(n,1)-a-1
          i2=images(n,1)+a+1
          if(i1 < 1) i1=1
          if(i2 > nx) i2=nx
          j1=images(n,2)-a-1
          j2=images(n,2)+a+1
          if(j1 < 1) j1=1
          if(j2 > ny) j2=ny
          a=a*a
          b=b*b
          d=-images(n,5)*pi/180.
          do j=j1,j2
            do i=i1,i2
              x=i-images(n,1)
              y=j-images(n,2)
              x2=i-xc
              y2=j-yc
              if(x /= 0) then
                t=atan(y/x)
              else 
                t=pi/2.
              endif
              c1=b*cos(t)*cos(t)+a*sin(t)*sin(t)
              c2=(a-b)*2.*sin(t)*cos(t)
              c3=b*sin(t)*sin(t)+a*cos(t)*cos(t)
              c4=a*b
        rr=sqrt(c4/(c1*cos(d)*cos(d)+c2*sin(d)*cos(d)+c3*sin(d)*sin(d)))
        if(sqrt(x*x+y*y) <= rr) then
          pix((j-1)*nx+i)=sqrt(dumnull)
        endif
            enddo
          enddo
        endif
      enddo

      call ftgiou(unit,status)
      do idot=1,80
        if(file1(idot:idot).eq.'.') exit
      enddo
      call ftopen(unit,file1(1:idot)//'clean',1,blocksize,status)
      if(status == 0) then
        call ftdelt(unit,status)
      elseif (status == 103) then
        status=0
        call ftcmsg
      else
        status=0
        call ftcmsg
        call ftdelt(unit,status)
      endif
      call ftfiou(unit, status)

      call ftgiou(unit,status)
      call ftinit(unit,file1(1:idot)//'clean',1,status)
      call ftphpr(unit,simple,bitpix,naxis,naxes,0,1,extend,status)
      call ftppre(unit,1,1,nx*ny,pix,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)
      if(status.gt.0) call printerror(status)

999   end

      subroutine printerror(status)  
      integer status
      character errtext*30,errmessage*80     

      call ftgerr(status,errtext)
      print *,'FITSIO Error Status =',status,': ',errtext
      call ftgmsg(errmessage) 
      do while (errmessage .ne. ' ')
          print *,errmessage
          call ftgmsg(errmessage)
      end do
      end

      subroutine findr(r,t,eps,a,d,xc,yc)

* subroutine to find the distance r from ellipse center xc,yc at angle t (in radians)
* for ellipse of semi-major axis (a) eccentricity (eps) and pos angle (d)

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
