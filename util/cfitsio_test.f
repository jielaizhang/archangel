* cfitsio test

      real data1(4096*4096)
      character file1*100

      integer status,unit,readwrite,blocksize,naxes(2),nfound,bitpix
      integer naxis,pc,gc
      logical simple,extend

      n=iargc()
      call getarg(1,file1)

      if(file1=='-h'.or.file1=='') then
        print*, ' '
        print '(a)', 'Usage: cfitsio_test filename'
        goto 999
      endif

      status=0
      call ftgiou(unit,status)
      call ftopen(unit,file1,readwrite,blocksize,status)
      print*, status
      call ftghpr(unit,3,simple,bitpix,naxis,naxes,pc,gc,extend,status)
      print*, naxes
      nx=naxes(1)
      ny=naxes(2)
      dumnull=-1.
      nullval=sqrt(dumnull)
      call ftgpve(unit,1,1,nx*ny,nullval,data1,anynull,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)
999	end
