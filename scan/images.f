* this is a brute force version of gasp_images, threshold image finder
* much slower than gasp_images

      real data(4096*4096),flux(1024*1024,4),nullval
      integer*2 object(32768,2)
      integer status,unit,readwrite,blocksize,naxes(2),nfound,bitpix
      integer naxis,pcount,gcount
      logical simple,extend
      character fname*100,op*2

      n=iargc()
      call getarg(1,op)
      if((op.eq.'-h').or.(op(1:1).ne.'-')) then
        print*, ' '
        print '(a)', 'Usage: option file_name sky threshold minpix'
        print*, ' '
        print '(a)', 'Options: -h = this mesage'
        print '(a)', '         -f = dump data'
        print '(a)', '         -m = dump mark file'
        print '(a)', '         -n = dump nexus file'
        goto 999
      endif

      status=0
      call ftgiou(unit,status)
      call getarg(2,fname)
      call ftopen(unit,fname,readwrite,blocksize,status)
      call ftghpr(unit,3,simple,bitpix,naxis,naxes,pcount,
     &       gcount, extend, status)
*     call ftgknj(unit,'NAXIS',1,2,naxes,nfound,status)
      nx=naxes(1)
      ny=naxes(2)
      nullval=sqrt(-1.)
      call ftgpve(unit,1,1,nx*ny,nullval,data,anynull,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)

      call getarg(3,fname)
      read(fname,*) sky
      call getarg(4,fname)
      read(fname,*) thres
      call getarg(5,fname)
      read(fname,*) minpix

      ntot=0
      next=0
      do j=1,ny
        do i=1,nx
          if((data((j-1)*nx+i)-sky).ge.thres) then
            ntot=ntot+1
            if(ntot.ge.1024*1024) then
              print*, 'too many pixels over threshold'
              goto 999
            endif
            flux(ntot,1)=data((j-1)*nx+i)-sky
            flux(ntot,2)=i
            flux(ntot,3)=j
            do l=1,ntot-1
              r=((flux(l,2)-i)**2+(flux(l,3)-j)**2)**0.5
              if(r.le.1.1) then
                flux(ntot,4)=flux(l,4)
                goto 100
              endif
            enddo
            next=next+1
            flux(ntot,4)=next
          endif
100     enddo
      enddo

      do l=1,ntot-1
        do i=l+1,ntot
          if(flux(l,4).ne.flux(i,4)) then
            r=((flux(l,2)-flux(i,2))**2+(flux(l,3)-flux(i,3))**2)**0.5
            id=flux(i,4)
            if(r.le.1.1) then
              do j=1,ntot
                if(flux(j,4).eq.id) flux(j,4)=flux(l,4)
              enddo
            endif
          endif
        enddo
      enddo

      nobj=0
      do i=1,ntot
        do j=1,nobj
          if(flux(i,4).eq.object(j,1)) goto 200
        enddo
        nobj=nobj+1
        if(nobj.ge.32768) then
          print*, 'too many objects'
          goto 999
        endif
        object(nobj,1)=flux(i,4)
        j=nobj
200     object(j,2)=object(j,2)+1
      enddo

      do l=1,nobj
        if(object(l,2).ge.minpix) then
          n=0
          totf=0.
          xc=0.
          yc=0.
          do j=1,ntot
            if(flux(j,4).eq.object(l,1)) then
              xc=xc+flux(j,2)*flux(j,1)
              yc=yc+flux(j,3)*flux(j,1)
              totf=totf+flux(j,1)
              n=n+1
            endif
          enddo

          xc=xc/totf
          yc=yc/totf

          do j=1,ntot
            if(flux(j,4).eq.object(l,1)) then
              flux(j,2)=flux(j,2)-xc
              flux(j,3)=flux(j,3)-yc
            endif
          enddo

          s1=0.
          s2=0.
          s3=0.
          s4=0.
          s5=0.
          s6=0.

          do j=1,ntot
            if(flux(j,4).eq.object(l,1)) then
              s1=s1+flux(j,1)*flux(j,2)
              s2=s2+flux(j,1)*flux(j,3)
              s3=s3+flux(j,1)*flux(j,2)*flux(j,2)
              s4=s4+flux(j,1)*flux(j,3)*flux(j,3)
              s5=s5+flux(j,1)*flux(j,2)*flux(j,3)
              s6=s6+flux(j,1)
            endif
          enddo

          xx=(s3-(s1*s1)/s6)/s6
          yy=(s4-(s2*s2)/s6)/s6
          xy=(s5-(s1*s2)/s6)/s6
          rr=xx+yy
          e=xx-yy
          e=sqrt(e*e+4.*xy*xy)/rr
          pa=atan(xy/(0.5*rr*(1.+e)-yy))

          pi=3.1415926536

          e=1.-e
          a=2.*sqrt(n/(pi*e))
          b=a*e
          pa=180.*pa/pi
          if(op.eq.'-f') then
            write(*,666) xc,yc,n,(1.-b/a),pa,totf
666         format(2f6.1,i8,f7.3,f6.1,f11.1)
          endif
          if(op.eq.'-n') then
            write(*,*) totf,a,(1.-b/a),pa,xc,yc
          endif
          if(op.eq.'-m') then
            write(*,667) xc,yc,a,b,pa
667         format('mark ',2f6.1,' el red ',3f8.1)
          endif
        endif

      enddo
999   end
