* takes a prf file and produces a model galaxy or subtracts directly from data file

	real pix(2048*2048),data(2048*2048)
      real images(1000,18),model(2048*2048)
      character file*100,op*2

      integer status,unit,rw,blocksize,naxes(2),nfound,bitpix
      integer naxis,pc,gc
      logical simple,extend

      n=iargc()
      call getarg(1,op)
      if((op == '-h') .or. (op(1:1) /= '-')) then
        print*, ' '
        print*, 'Usage: make_fake option file_name_prefix'
        print*, ' '
        print*, 'code looks for fake.in file output from XML file'
        print*, ' '
        print*, 'Options: -h = this mesage'
        print*, '         -m = produce model file'
        print*, '         -s = produce subtraction file'
        print*, '         -c = fill in a cleaned file'
        print*, ' '
        print*, 'note: output file = prefix.fake or model'
        goto 999
      endif

      call getarg(2,file)
      do idot=1,100
        if(file(idot:idot).eq.'.') exit
      enddo
      idot=idot-1
      if(idot == 100) then
        do idot=100,1,-1
          if(file(idot:idot).ne.' ') exit
        enddo
      endif
      status=0
      call ftgiou(unit,status)
*      call ftopen(unit,file(1:idot)//'.clean',rw,blocksize,status)
      call ftopen(unit,file,rw,blocksize,status)
      call ftghpr(unit,3,simple,bitpix,naxis,naxes,pc,gc,extend,status)
      nx=naxes(1)
      if(nx == 0) goto 999
      ny=naxes(2)
      dumnull=-1.
      nullval=sqrt(dumnull)
      call ftgpve(unit,1,1,nx*ny,nullval,pix,anynull,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)

*      open(unit=1,file=file(1:idot)//'.sky')
      open(unit=1,file='fake.in')
      read(1,*) sky
*      open(unit=1,file=file(1:idot)//'.prf')
      line=0
      do 
        line=line+1
        read(1,*,end=100,err=100) (images(line,i),i=1,18)
      enddo
100   line=line-1
      close(unit=1)
      x0=0.
      y0=0.
      do i=1,10
        x0=x0+images(i,15)/10.
        y0=y0+images(i,16)/10.
      enddo

      if(op == '-c') then
        do j=1,ny
          do i=1,nx
	      x=i-x0
	      y=j-y0
            if(pix((j-1)*nx+i) .eq. pix((j-1)*nx+i)) goto 401
        call findr(images,i,j,1,rmin,images(1,15),images(1,16))
            if((x**2+y**2)**.5 <= rmin) then
              l=1
              pix((j-1)*nx+i)=images(l,1)
              goto 401
            endif
        call findr(images,i,j,line,r,images(line,15),images(line,16))
	      x=i-images(line,15)
	      y=j-images(line,16)
            if((x**2+y**2)**.5 > r) goto 301
            do l=line-1,2,-1
              call findr(images,i,j,l,r,images(l,15),images(l,16))
	        x=i-images(l,15)
	        y=j-images(l,16)
              if((x**2+y**2)**.5 > r) goto 201
            enddo
201         call findr(images,i,j,l+1,r2,images(l+1,15),images(l+1,16))
            if(l.eq.1) call findr(images,i,j,1,r,x0,y0)
*            if(i.eq.327.and.j.eq.306) print*, l,r,r2
*            if(i.eq.327.and.j.eq.306) print*, (((x**2+y**2)**0.5)-r)
*      if(i.eq.327.and.j.eq.306) print*, images(l+1,1),images(l,1),(r2-r)
            xi=(((x**2+y**2)**0.5)-r)*(images(l+1,1)-images(l,1))/(r2-r)
            pix((j-1)*nx+i)=images(l,1)+xi
*            if(i.eq.327.and.j.eq.306) print*, images(l,1),xi
*            if(i.eq.327.and.j.eq.306) print*, pix((j-1)*nx+i)
            goto 401
301         pix((j-1)*nx+i)=sky
401	    enddo
	  enddo

      else

        do j=1,ny
          do i=1,nx
	      x=i-x0
	      y=j-y0
            if((x**2+y**2)**.5 <= 2) then
              l=1
              goto 300
            endif
        call findr(images,i,j,line,r,images(line,15),images(line,16))
	      x=i-images(line,15)
	      y=j-images(line,16)
            if((x**2+y**2)**0.5 > r) then
              l=line
              goto 300
            endif
            do l=line-1,2,-1
              call findr(images,i,j,l,r,images(l,15),images(l,16))
	        x=i-images(l,15)
	        y=j-images(l,16)
*              if(i.eq.533.and.j.eq.522) print*, l,i,images(l,15)
*              if(i.eq.533.and.j.eq.522) print*, l,j,images(l,16)
*              if(i.eq.533.and.j.eq.522) print*, l,x,y
*              if(i.eq.533.and.j.eq.522) print*, l,r,(x**2+y**2)**.5
*              if(i.eq.533.and.j.eq.522) print*, images(l,1)
              if((x**2+y**2)**.5 > r) goto 200
            enddo
300         data((j-1)*nx+i)=pix((j-1)*nx+i)-images(l,1)+sky
            model((j-1)*nx+i)=images(l,1)
            goto 400
200         call findr(images,i,j,l+1,r2,images(l+1,15),images(l+1,16))
	      x=i-images(l,15)
	      y=j-images(l,16)
            xi=(((x**2+y**2)**0.5)-r)*(images(l+1,1)-images(l,1))/(r2-r)
            xi=images(l,1)+xi
            data((j-1)*nx+i)=pix((j-1)*nx+i)-xi+sky
*            model((j-1)*nx+i)=images(l,1)+xi
            model((j-1)*nx+i)=xi
400	    enddo
	  enddo
      endif

      call ftgiou(unit,status)
      if(op == '-s') then
        call ftopen(unit,file(1:idot)//'.sub',1,blocksize,status)
      endif
      if(op == '-c') then
        call ftopen(unit,file(1:idot)//'.fake',1,blocksize,status)
      endif
      if(op == '-m') then
        call ftopen(unit,file(1:idot)//'.model',1,blocksize,status)
      endif
      if(status.eq.0) then
        call ftdelt(unit,status)
      elseif (status.eq.103) then
        status=0
        call ftcmsg
      else
        status=0
        call ftcmsg
        call ftdelt(unit,status)
      endif
      call ftfiou(unit,status)
      call ftgiou(unit,status)
      if(op == '-s') then
        call ftinit(unit,file(1:idot)//'.sub',1,status)
      endif
      if(op == '-c') then
        call ftinit(unit,file(1:idot)//'.fake',1,status)
      endif
      if(op == '-m') then
        call ftinit(unit,file(1:idot)//'.model',1,status)
      endif
      call ftphpr(unit,simple,bitpix,naxis,naxes,0,1,extend,status)
      if(op == '-s') then
        call ftppre(unit,1,1,nx*ny,data,status)
      elseif(op == '-c') then
        call ftppre(unit,1,1,nx*ny,pix,status)
      else
        call ftppre(unit,1,1,nx*ny,model,status)
      endif
      call ftclos(unit,status)
      call ftfiou(unit,status)
      if(status.gt.0) call printerror(status)

999	end

      subroutine findr(images,i,j,l,r,x0,y0)
      real images(1000,18)

      pi=3.1415926536
      a=images(l,4)
      rat=1.-images(l,13)
      d=-images(l,14)*pi/180.
      y=j-y0
      x=i-x0
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
      end do
      end
