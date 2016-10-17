	real data(4096*4096)
      character file1*100,file2*100,strng*10

      integer stat,inunit,readwrite,blocksize,naxes(2),nfound,bitpix
      integer naxis,pc,gc,outunit
      logical simple,extend
      character record*80

      n=iargc()
      call getarg(1,file1)
      if(file1=='-h'.or.file1==''.or.file2=='') then
        print*, ' '
        print*, 'Usage: zero data_file output_file value'
        print*, ' '
        print*, 'Options: -h = this mesage'
        print*, ' '
        print*, 'set all pixels below value to NaN'
        goto 999
      endif
      call getarg(2,file2)
      call getarg(3,strng)
      read(strng,*) x

      stat=0
      call ftgiou(inunit,stat)
      call ftopen(inunit,file1,readwrite,blocksize,stat)
      call ftghpr(inunit,3,simple,bitpix,naxis,naxes,pc,gc,extend,stat)
      nx=naxes(1)
      ny=naxes(2)
      nullval=sqrt(-1.)
      call ftgpve(inunit,1,1,nx*ny,nullval,data,anynull,stat)

      do i=1,nx*ny
        if(data(i).le.x) data(i)=sqrt(-1.)
      enddo

      call ftgiou(outunit,stat)
      call ftopen(outunit,file2,1,blocksize,stat)
      if(stat.eq.0) then
        call ftdelt(outunit,stat)
      elseif (stat.eq.103) then
        stat=0
        call ftcmsg
      else
        stat=0
        call ftcmsg
        call ftdelt(outunit,stat)
      endif
      call ftfiou(outunit,stat)
      call ftgiou(outunit,stat)
      call ftinit(outunit,file2,1,stat)

      call ftghsp(inunit,nkeys,nspace,stat)
      do i=1,nkeys
          call ftgrec(inunit,i,record,stat)
          call ftprec(outunit,record,stat)
      end do

      call ftppre(outunit,1,1,nx*ny,data,stat)

      call ftclos(outunit,stat)
      call ftfiou(outunit,stat)

      call ftclos(inunit,stat)
      call ftfiou(inunit,stat)

999	end
