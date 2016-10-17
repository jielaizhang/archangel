	real data(5000*5000)
      character file*100,strng1*20, strng2*20
      integer status,unit,readwrite,blocksize,naxes(2),nfound,bitpix
      integer naxis,pc,gc
      logical simple,extend

      n=iargc()
      call getarg(1,file)
      if(file=='-h') then
        print*, ' '
        print*, 'Usage: threshold data_file sky threshold'
        print*, ' '
        print*, 'write out pixels above sky+threshold'
        print*, ' '
        print*, 'Options: -h = this mesage'
        goto 999
      endif
      call getarg(2,strng1)
      call getarg(3,strng2)
      read(strng1,*) sky
      read(strng2,*) thres

      status=0
      call ftgiou(unit,status)
      call ftopen(unit,file,readwrite,blocksize,status)
      call ftghpr(unit,3,simple,bitpix,naxis,naxes,pc,gc,extend,status)
      nx=naxes(1)
      ny=naxes(2)
      xdum=-1.
      nullval=sqrt(xdum)
      call ftgpve(unit,1,1,nx*ny,nullval,data,anynull,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)

      do j=1,ny
        do i=1,nx
          if(data((j-1)*nx+i).ge.(sky+thres)) then
            print*, i,j,data((j-1)*nx+i)
10          format(i5,i5,f10.2)
          endif
        enddo
      enddo
999	end
