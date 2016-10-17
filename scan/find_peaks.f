      real data(5000*5000)
      character file*100,strng*20
      integer status,unit,readwrite,blocksize,naxes(2),nfound,bitpix
      integer naxis,pc,gc
      logical simple,extend

      n=iargc()
      call getarg(1,file)
      if(file=='-h') then
        print*, ' '
        print*, 'Usage: find_peaks data_file'
        print*, ' '
        print*, 'find peaks from thres.tmp'
        goto 999
      endif

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

      open(unit=1,file='thres.tmp')
      do while (.true.)
        read(1,*,end=999) ixc,iyc
        isw=1
        do j=iyc-1,iyc+1
          do i=ixc-1,ixc+1
            if(data((j-1)*nx+i).gt.data((iyc-1)*nx+ixc)) then
              isw=0
            endif
*            print*, i,j,data((j-1)*nx+i),data((iyc-1)*nx+ixc),isw
          enddo
        enddo
        if(isw == 1) write(*,10) ixc,iyc,' 10 0. 0. 0.'
10      format(i5,i5,a)
      enddo
999	end
