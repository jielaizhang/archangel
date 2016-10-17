	real data(4096*4096)
      character file*100,strng*10

      integer status,unit,readwrite,blocksize,naxes(2),nfound,bitpix
      integer naxis,pc,gc
      logical simple,extend

      n=iargc()
      call getarg(1,file)

      if(file=='-h'.or.file=='') then
        print*, ' '
        print*, 'Usage: min_max data_file x y r'
        print*, ' '
        print*, 'find the location of the min and max pixels'
        print*, 'if specified, from x and y for radius r'
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

      if(n > 1) then
        call getarg(2,strng)
        read(strng,*) x
        call getarg(3,strng)
        read(strng,*) y
        call getarg(4,strng)
        read(strng,*) r
      else
        x=nx/2
        y=ny/2
        r=nx*ny
      endif

      xmin=+1.e33
      xmax=-1.e33
      nan=0
      do j=1,ny
        do i=1,nx
          if(((i-x)**2+(j-y)**2)**0.5 < r) then
            if(data((j-1)*nx+i).eq.data((j-1)*nx+i)) then
              if(data((j-1)*nx+i).ge.xmax) then
                xmax=data((j-1)*nx+i)
                imax=i
                jmax=j
              endif
              if(data((j-1)*nx+i).le.xmin) then
                xmin=data((j-1)*nx+i)
                imin=i
                jmin=j
              endif
            else
              nan=nan+1
            endif
          endif
        enddo
      enddo
      print*, 'Minimum of ',xmin,' at x = ',imin,' and y = ',jmin
      print*, 'Maximum of ',xmax,' at x = ',imax,' and y = ',jmax
      print*, 'Number of NaN pixels ',nan

999   end
