      real data(4096*4096)
      character file*100,strng*10

      integer status,unit,readwrite,blocksize,naxes(2),nfound,bitpix
      integer naxis,pc,gc
      logical simple,extend

      n=iargc()
      call getarg(1,file)

      if(file=='-h'.or.file=='') then
        print*, ' '
        print*, 'Usage: nan data_file'
        print*, ' '
        print*, 'print mark x y dot red 1 for all NaN pixels'
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

      do j=1,ny
        do i=1,nx
          if(data((j-1)*nx+i).ne.data((j-1)*nx+i)) then
            print*, 'mark',i,j,' dot red 1'
          endif
        enddo
      enddo

999   end
