* turns IRAF mask file into a NaN mask file

      real data(4096*4096)
      character file1*100,file2*100

      integer status,unit,readwrite,blocksize,naxes(2),nfound,bitpix
      integer naxis,pc,gc
      logical simple,extend

      n=iargc()
      call getarg(1,file1)
      call getarg(2,file2)

      if(file1=='-h'.or.file1==''.or.file2=='') then
        print*, ' '
        print '(a)', 'Usage: mask iraf_mask_file out_file'
        print*, ' '
        print '(a)', 'Options: -h = this mesage'
        goto 999
      endif

      status=0
      call ftgiou(unit,status)
      call ftopen(unit,file1,readwrite,blocksize,status)
      call ftghpr(unit,3,simple,bitpix,naxis,naxes,pc,gc,extend,status)
      nx=naxes(1)
      ny=naxes(2)
      nullval=sqrt(-1.)
      call ftgpve(unit,1,1,nx*ny,nullval,data,anynull,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)

      do j=1,ny
        do i=1,nx
          if(data((j-1)*nx+i).eq.0.) data((j-1)*nx+i)=sqrt(-1.)
        enddo
      enddo

      call ftgiou(unit,status)
      call ftopen(unit,file2,1,blocksize,status)
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
      call ftinit(unit,file2,1,status)
      call ftphpr(unit,simple,bitpix,naxis,naxes,0,1,extend,status)
      call ftppre(unit,1,1,nx*ny,data,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)
999   end
