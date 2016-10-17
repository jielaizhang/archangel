* make a masked data file from a NaN mask

      real data1(4096*4096),data2(4096*4096)
      character file1*100,file2*100,file3*100,strng*20

      integer status,unit,readwrite,blocksize,naxes(2),nfound,bitpix
      integer naxis,pc,gc
      logical simple,extend

      n=iargc()
      call getarg(1,file1)
      call getarg(2,file2)
      call getarg(3,file3)
      if(n.ge.4) then
        call getarg(4,strng)
        read(strng,'(i8)') ix
        call getarg(5,strng)
        read(strng,'(i8)') iy
      else
        ix=0
        iy=0
      endif
      if(n.ge.6) then
        call getarg(6,strng)
        read(strng,'(i8)') ixc
        call getarg(7,strng)
        read(strng,'(i8)') iyc
        call getarg(8,strng)
        read(strng,'(i8)') irr
      else
        ixc=0
        iyc=0
        irr=0
      endif

      if(file1=='-h'.or.file1==''.or.file2==''.or.file3 =='') then
        print*, ' '
        print '(a)', 'Usage: mask data mask outfile x y xc yc rr'
        print*, ' '
        print '(a)', 'Options: -h = this mesage'
        print '(a)', '          x = x shift in pixels'
        print '(a)', '          y = y shift in pixels'
        print '(a)', '         xc = ignore x center'
        print '(a)', '         yc = ignore y center'
        print '(a)', '         rr = ignore center radius'
        goto 999
      endif

      status=0
      call ftgiou(unit,status)
      call ftopen(unit,file1,readwrite,blocksize,status)
      if(status.gt.0) then
        print*, 'clean file error'
        goto 999
      endif
      call ftghpr(unit,3,simple,bitpix,naxis,naxes,pc,gc,extend,status)
      nx=naxes(1)
      ny=naxes(2)
      dumnull=-1.
      nullval=sqrt(dumnull)
      call ftgpve(unit,1,1,nx*ny,nullval,data1,anynull,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)

      status=0
      call ftgiou(unit,status)
      call ftopen(unit,file2,readwrite,blocksize,status)
      if(status.gt.0) then
        print*, 'clean file error'
        goto 999
      endif
      call ftghpr(unit,3,simple,bitpix,naxis,naxes,pc,gc,extend,status)
      call ftgpve(unit,1,1,nx*ny,nullval,data2,anynull,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)

      do j=1,ny
        jj=j-iy-1
        if(jj.lt.1) jj=1
        if(jj.gt.ny) jj=ny
        do i=1,nx
          ii=i-ix
          if(ii.lt.1) ii=1
          if(ii.gt.nx) ii=nx
          if(data2(jj*nx+ii).ne.data2(jj*nx+ii).and.
     *      (((j-iyc)**2+(i-ixc)**2)**0.5.ge.irr)) then
            data1((j-1)*nx+i)=sqrt(dumnull)
          endif
        enddo
      enddo

      call ftgiou(unit,status)
      call ftopen(unit,file3,1,blocksize,status)
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
      call ftinit(unit,file3,1,status)
      call ftphpr(unit,simple,bitpix,naxis,naxes,0,1,extend,status)
      call ftppre(unit,1,1,nx*ny,data1,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)

999   end
