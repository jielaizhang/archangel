	real radius(500),sr(500),rf(500),sf(500),prf(18)
	real a(10),lx(500),ly(500),yfit(500),re
	integer*2 kill(500)
	character name*20,char,rply,strng*20
      common xmin,xmax,ymin,ymax,nt

	n=iargc()
	call getarg(1,name)
      if(name == '-h') then
        print '(a)', 'Usage: bdd prf_file -sky sky -psf fwhm'
        print '(a)', ' '
        print '(a)', 'Options: -h = this message'
        print '(a)', '         -sky = override sky value'
        print '(a)', '         -psf = use fwhm for psf'
        goto 999
      endif

      do i=1,30
        if((name(i:i) == ' ').or.(name(i:i) == '.')) exit
      enddo
      iend=i-1

	call pgbegin(0,'/xs',1,1)
      call pgask(0)
      call pgscr(0,1.,1.,1.)
      call pgscr(1,0.,0.,0.)
	nt=3

      open(unit=1,file=name(1:iend)//'.sfb',status='old',err=5)
      read(1,*) cstore,alpha,se,re,sky
      ifit=3
      if(cstore == 0) ifit=2
      if(se == 0) ifit=1
      sstore=1.0857/alpha
	do while (.true.)
        npts=npts+1
	  read(1,*,end=200) radius(npts),sr(npts),kill(npts)
	enddo
      
5     open(unit=1,file=name(1:iend)//'.sky',status='old',err=10)
      read(1,*) sky,skysig
      goto 20
10    sky=0.
      fwhm=0.
20    close(unit=1)
      if(n > 2) then
        call getarg(2,strng)
        if(strng == '-sky') then
          call getarg(3,strng)
          read(strng,*) sky
        else
          call getarg(3,strng)
          read(strng,*) fwhm
        endif
      endif

      open(unit=1,file=name(1:iend)//'.cal',status='old',err=30)
      read(1,*) xscale,cons
      goto 40
30    print*, 'no cal file, assuming zero'
      xscale=1.
      cons=25.
40    close(unit=1)

	open(unit=1,file=name(1:iend)//'.prf',err=50)
	do while (.true.)
	  read(1,*,end=60) prf
	  npts=npts+1
        radius(npts)=prf(4)
        sr(npts)=prf(1)
	enddo
50    print*, 'no prf file, aborting'
      goto 999
60    close(unit=1)
	call linfit(radius,sr,5,a,chisqr)
      xcore=a(1)

      call pgadvance
      ymax=-1.e33
      ymin=1.e33
      do i=1,npts
        if(sr(i).gt.ymax) ymax=sr(i)
        if(sr(i).lt.ymin) ymin=sr(i)
      enddo
      ymax=ymax+0.2*(ymax-ymin)
      ymin=ymin-0.2*(ymax-ymin)
      xmin=radius(1)-0.1*(radius(npts)-radius(1))
      xmax=radius(npts)+0.1*(radius(npts)-radius(1))
	call pgwindow(xmin,xmax,ymin,ymax)
	call pgbox('BCNST',0.,0,'BCNST',0.,0)
	call pglabel('r (arcsec)','DN',name)
	do i=1,npts
	  call pgpoint(1,radius(i),sr(i),4)
	enddo
      call pgsci(4)
      call pgmove(xmin,sky)
      call pgdraw(xmax,sky)
      if(fwhm .ne. 0 .and. xmax < 20.*fwhm) then
        call gdraw(fwhm,xcore,0.,0.)
      endif
      call pgsci(1)

	do while (.true.)
	  call pgcurse(x,y,char)
	  if(char.eq.'/') then
          goto 100
	  else if(char.eq.'?') then
          print*, 'This section is for checking sky'
          print*, ' '
          print*, 'b = redo borders (select UR then LL)'
          print*, 'x = remove point'
          print*, 'l = kill all points lower'
          print*, 'u = kill all upper'
          print*, 's = calc sky (select low then upper)'
          print*, 'r = reset screen'
          print*, 'q = quit, move on to next secton'
          print*, '/ = abort program'
	  else if(char.eq.'q') then
          goto 999
	  else if(char.eq.'r') then
          ymax=-1.e33
          ymin=1.e33
          do i=1,npts
            if(sr(i).gt.ymax) ymax=sr(i)
            if(sr(i).lt.ymin) ymin=sr(i)
          enddo
          ymax=ymax+0.2*(ymax-ymin)
          ymin=ymin-0.2*(ymax-ymin)
          xmin=radius(1)-0.1*(radius(npts)-radius(1))
          xmax=radius(npts)+0.1*(radius(npts)-radius(1))
	    call pgadvance
	    call pgwindow(xmin,xmax,ymin,ymax)
	    call pgbox('BCNST',0.,0,'BCNST',0.,0)
	    call pglabel('r (pixel)','DN',name)
	    do i=1,npts
	      if(kill(i).ne.1) then
	        call pgpoint(1,radius(i),sr(i),4)
	      else
	        call pgpoint(1,radius(i),sr(i),5)
	      endif
	    enddo
          call pgsci(4)
          call pgmove(xmin,sky)
          call pgdraw(xmax,sky)
          if(fwhm .ne. 0 .and. xmax < 20.*fwhm) then
            call gdraw(fwhm,xcore,0.,0.)
          endif
          call pgsci(1)
	  else if(char.eq.'b') then
          xmin=x
          ymin=y
	    call pgcurse(x,y,char)
          xmax=x
          ymax=y
	    call pgadvance
	    call pgwindow(xmin,xmax,ymin,ymax)
	    call pgbox('BCNST',0.,0,'BCNST',0.,0)
	    call pglabel('r (pixel)','DN',name)
	    do i=1,npts
	      if(kill(i).ne.1) then
	        call pgpoint(1,radius(i),sr(i),4)
	      else
	        call pgpoint(1,radius(i),sr(i),5)
	      endif
	    enddo
          call pgsci(4)
          call pgmove(xmin,sky)
          call pgdraw(xmax,sky)
          if(fwhm .ne. 0 .and. xmax < 20.*fwhm) then
            call gdraw(fwhm,xcore,0.,0.)
          endif
          call pgsci(1)
	  else if(char.eq.'U'.or.char.eq.'u') then
	    rmin=1.e33
	    do i=npts,1,-1
	      if(radius(i).lt.x) exit
            kill(i)=1 
	    enddo
	    call pgadvance
	    call pgwindow(xmin,xmax,ymin,ymax)
	    call pgbox('BCNST',0.,0,'BCNST',0.,0)
	    call pglabel('r (pixel)','DN',name)
	    do i=1,npts
	      if(kill(i).ne.1) then
	        call pgpoint(1,radius(i),sr(i),4)
	      else
	        call pgpoint(1,radius(i),sr(i),5)
	      endif
	    enddo
          call pgsci(4)
          call pgmove(xmin,sky)
          call pgdraw(xmax,sky)
          if(fwhm .ne. 0 .and. xmax < 20.*fwhm) then
            call gdraw(fwhm,xcore,0.,0.)
          endif
          call pgsci(1)
	  else if(char.eq.'l') then
	    rmin=1.e33
	    do i=1,npts
	      if(radius(i).lt.x) kill(i)=1 
	    enddo
	    call pgadvance
	    call pgwindow(xmin,xmax,ymin,ymax)
	    call pgbox('BCNST',0.,0,'BCNST',0.,0)
	    call pglabel('r (pixel)','DN',name)
	    do i=1,npts
	      if(kill(i).ne.1) then
	        call pgpoint(1,radius(i),sr(i),4)
	      else
	        call pgpoint(1,radius(i),sr(i),5)
	      endif
	    enddo
          call pgsci(4)
          call pgmove(xmin,sky)
          call pgdraw(xmax,sky)
          if(fwhm .ne. 0 .and. xmax < 20.*fwhm) then
            call gdraw(fwhm,xcore,0.,0.)
          endif
          call pgsci(1)
	  else if(char.eq.'s') then
          x1=x
          call pgcurse(x,y,char)
          x2=x
          sky=0.
          nsky=0
	    do i=1,npts
            if(radius(i).ge.x1.and.radius(i).le.x2) then
              sky=sky+sr(i)
              nsky=nsky+1
            endif
	    enddo
          sky=sky/nsky
	    call pgadvance
	    call pgwindow(xmin,xmax,ymin,ymax)
	    call pgbox('BCNST',0.,0,'BCNST',0.,0)
	    call pglabel('r (pixel)','DN',name)
	    do i=1,npts
	      if(kill(i).ne.1) then
	        call pgpoint(1,radius(i),sr(i),4)
	      else
	        call pgpoint(1,radius(i),sr(i),5)
	      endif
	    enddo
          call pgsci(4)
          call pgmove(xmin,sky)
          call pgdraw(xmax,sky)
          if(fwhm .ne. 0 .and. xmax < 20.*fwhm) then
            call gdraw(fwhm,xcore,0.,0.)
          endif
          call pgsci(1)
	  else if(char.eq.'x') then
	    rmin=1.e33
	    do i=1,npts
	      r=abs(radius(i)-x)
	      if(r.lt.rmin.and.kill(i).eq.0) then
		imin=i
		rmin=r
	      endif
	    enddo
	    kill(imin)=abs(kill(imin)-1)
	    call pgadvance
	    call pgwindow(xmin,xmax,ymin,ymax)
	    call pgbox('BCNST',0.,0,'BCNST',0.,0)
	    call pglabel('r (pixel)','DN',name)
	    do i=1,npts
	      if(kill(i).ne.1) then
	        call pgpoint(1,radius(i),sr(i),4)
	      else
	        call pgpoint(1,radius(i),sr(i),5)
	      endif
	    enddo
          call pgsci(4)
          call pgmove(xmin,sky)
          call pgdraw(xmax,sky)
          if(fwhm .ne. 0 .and. xmax < 20.*fwhm) then
            call gdraw(fwhm,xcore,0.,0.)
          endif
          call pgsci(1)
        endif
      enddo

100   call pgadvance
      itmp=0
      do i=1,npts
        if((sr(i)-sky > 0) .and. (kill(i) == 0)) then
          itmp=itmp+1
          radius(itmp)=radius(i)*xscale
          sr(itmp)=-2.5*alog10((sr(i)-sky)/(xscale**2))+cons
        endif
      enddo
      npts=itmp

200   close(unit=1)
      if(radius(npts) == 0) npts=npts-1  ! kludge for do while read???
      ymax=-1.e33
      ymin=1.e33
      do i=1,npts
        if(sr(i).gt.ymax) ymax=sr(i)
        if(sr(i).lt.ymin) ymin=sr(i)
      enddo
      ymax=ymax+0.2*(ymax-ymin)
      ymin=ymin-0.2*(ymax-ymin)
      xmin=radius(1)-0.1*(radius(npts)-radius(1))
      xmax=radius(npts)+0.1*(radius(npts)-radius(1))
	call pgwindow(xmin,xmax,ymax,ymin)
	call pgbox('BCNST',0.,0,'BCNST',0.,0)
	call pglabel('r (arcsec)','\\gm',name)
	do i=1,npts
	  if(kill(i).ne.1) then
	    call pgpoint(1,radius(i),sr(i),4)
	  else
	    call pgpoint(1,radius(i),sr(i),5)
	  endif
	enddo
	if(ifit.ne.0) call fplot(se,re,sstore,cstore,radius(1),radius(npts),chisqr,ifit)
      if(fwhm .ne. 0 .and. xmax < 20.*fwhm) then
        call gdraw(fwhm,xcore,xscale,cons)
      endif

	do while (.true.)

	  call pgcurse(x,y,char)

	  if(char.eq.'q') then
          goto 999

	  else if(char.eq.'/') then
          open(unit=1,file=name(1:iend)//'.sfb')

* ifit = 1, disk only fit
*      = 2, r^1/4 only fit
*      = 3, B+D fit

          if(ifit == 1) then
            write(1,'(5(1pe12.4))') cstore,alpha,0.,0.,sky
          else if(ifit == 2) then
            write(1,'(5(1pe12.4))') 0.,0.,se,re,sky
          else
            write(1,'(5(1pe12.4))') cstore,1.0857/sstore,se,re,sky
          endif
          do i=1,npts
            if(ifit == 2) then
              write(1,'(2(1pe12.4),i3)') radius(i)**4.,sr(i),kill(i)
            else
              write(1,'(2(1pe12.4),i3)') radius(i),sr(i),kill(i)
            endif
          enddo
	    goto 999

	  else if(char.eq.'?') then
	    print*, ' ' 
	    print*, 'x = erase point        d = disk fit only'
	    print*, 'm = erase all min pts  f = do bulge+disk fit'
	    print*, 'u = erase all max pts  e = do r**1/4 fit only'
	    print*, 'b = redo boundaries    r = reset graphics'
	    print*, 'q = write .sfb file    / = abort'
	    print*, ' ' 

	  else if(char.eq.'u') then
	    rmin=1.e33
	    do i=npts,1,-1
	      if(radius(i).lt.x) exit
            kill(i)=1 
	    enddo
	    call pgadvance
	    call pgwindow(xmin,xmax,ymax,ymin)
	    call pgbox('BCNST',0.,0,'BCNST',0.,0)
	    if(ifit == 2) then
	      call pglabel('r\\u1/4','\\gm\\dR',name)
	    else
	      call pglabel('r (arcsec)','\\gm\\dR',name)
	    endif
	    do i=1,npts
	      if(kill(i).ne.1) then
	        call pgpoint(1,radius(i),sr(i),4)
	      else
	        call pgpoint(1,radius(i),sr(i),5)
	      endif
	    enddo
	    call fplot(se,re,sstore,cstore,radius(1),radius(npts),chisqr,ifit)
          if(fwhm .ne. 0 .and. xmax < 20.*fwhm) then
            call gdraw(fwhm,xcore,xscale,cons)
          endif

	  else if(char.eq.'l') then
	    rmin=1.e33
	    do i=1,npts
	      if(radius(i).lt.x) kill(i)=1 
	    enddo
	    call pgadvance
	    call pgwindow(xmin,xmax,ymax,ymin)
	    call pgbox('BCNST',0.,0,'BCNST',0.,0)
	    if(ifit == 2) then
	      call pglabel('r\\u1/4','\\gm\\dR',name)
	    else
	      call pglabel('r (arcsec)','\\gm\\dR',name)
	    endif
	    do i=1,npts
	      if(kill(i).ne.1) then
	        call pgpoint(1,radius(i),sr(i),4)
	      else
	        call pgpoint(1,radius(i),sr(i),5)
	      endif
	    enddo
	    call fplot(se,re,sstore,cstore,radius(1),radius(npts),chisqr,ifit)
          if(fwhm .ne. 0 .and. xmax < 20.*fwhm) then
            call gdraw(fwhm,xcore,xscale,cons)
          endif

	  else if(char.eq.'x') then
	    rmin=1.e33
	    do i=1,npts
	      r=abs(radius(i)-x)
	      if(r.lt.rmin.and.kill(i).eq.0) then
		imin=i
		rmin=r
	      endif
	    enddo
	    kill(imin)=abs(kill(imin)-1)
	    call pgadvance
	    call pgwindow(xmin,xmax,ymax,ymin)
	    call pgbox('BCNST',0.,0,'BCNST',0.,0)
	    if(ifit == 2) then
	      call pglabel('r\\u1/4','\\gm\\dR',name)
	    else
	      call pglabel('r (arcsec)','\\gm\\dR',name)
	    endif
	    do i=1,npts
	      if(kill(i).ne.1) then
	        call pgpoint(1,radius(i),sr(i),4)
	      else
	        call pgpoint(1,radius(i),sr(i),5)
	      endif
	    enddo
	    call fplot(se,re,sstore,cstore,radius(1),radius(npts),chisqr,ifit)
          if(fwhm .ne. 0 .and. xmax < 20.*fwhm) then
            call gdraw(fwhm,xcore,xscale,cons)
          endif

	  else if(char.eq.'e') then
	    if(ifit.ne.2) then
	      do j=1,npts
	        radius(j)=radius(j)**0.25
	      enddo
	      ifit=2
	      xmax=xmax**0.25
            xmin=radius(1)-0.1*(xmax-radius(1))
          endif
	    call pgadvance
	    call pgwindow(xmin,xmax,ymax,ymin)
	    call pgbox('BCNST',0.,0,'BCNST',0.,0)
	    call pglabel('r\\u1/4','\\gm\\dR',name)
	    do i=1,npts
	      if(kill(i).ne.1) then
	        call pgpoint(1,radius(i),sr(i),4)
	      else
	        call pgpoint(1,radius(i),sr(i),5)
	      endif
	    enddo
	    nf=0
	    do i=1,npts
	      if(kill(i).ne.1) then
		nf=nf+1
		rf(nf)=radius(i)
		sf(nf)=sr(i)
	      endif
	    enddo
	    a(1)=2
	    a(2)=.5
	    call linfit(rf,sf,nf,a,chisqr)
*	    print 333, re,se
*333	    format('Re =',f5.1,' Se =',f6.2)
	    se=a(1)+8.325
	    re=1./((a(2)/8.325)**4.)
	    call fplot(se,re,sstore,cstore,radius(1),radius(npts),chisqr,ifit)
          xscale=-abs(xscale)
          if(fwhm .ne. 0 .and. xmax < 20.*fwhm) then
            call gdraw(fwhm,xcore,xscale,cons)
          endif

	  else if(char.eq.'d') then
          xscale=abs(xscale)
          if(ifit == 2) then
            do i=1,npts
              radius(i)=radius(i)**4.
            enddo
	      xmax=xmax**4.
            xmin=radius(1)-0.1*(xmax-radius(1))
          endif
	    call pgadvance
	    call pgwindow(xmin,xmax,ymax,ymin)
	    call pgbox('BCNST',0.,0,'BCNST',0.,0)
	    call pglabel('r (arcsecs)','\\gm',name)
	    do i=1,npts
	      if(kill(i).ne.1) then
	        call pgpoint(1,radius(i),sr(i),4)
	      else
	        call pgpoint(1,radius(i),sr(i),5)
	      endif
	    enddo
          if(ifit == 2) call pgcurse(x,y,char)
          ifit=1
	    xdisk1=x
	    call pgcurse(x,y,char)
	    xdisk2=x
	    n=0
	    do i=1,npts
	      if(radius(i).ge.xdisk1.and.radius(i).le.xdisk2.and.kill(i).ne.1) then
		n=n+1
		lx(n)=radius(i)
		ly(n)=sr(i)
	      endif
	    enddo
	    call linfit(lx,ly,n,a,chisqr)
	    cstore=a(1)
	    sstore=a(2)
          alpha = 1.0857/a(2)
*	    print*, ' '
*	    print*, ' B(0)   Alpha     chisqr'
*	    print 111, cstore,alpha,chisqr
*	    print*, ' '
*111	    format(f5.1,1x,1pe9.3,1x,1pe9.3)
	    call fplot(se,re,sstore,cstore,radius(1),radius(npts),chisqr,ifit)
          if(fwhm .ne. 0 .and. xmax < 20.*fwhm) then
            call gdraw(fwhm,xcore,xscale,cons)
          endif

	  else if(char.eq.'p') then
	    if(nt <= 3) then
	      nt=4
	    else
	      nt=3
	    endif
	    call pgadvance
	    call pgwindow(xmin,xmax,ymax,ymin)
	    call pgbox('BCNST',0.,0,'BCNST',0.,0)
	    call pglabel('r (arcsec)','\\gm\\dR',name)
	    do i=1,npts
	      if(kill(i).ne.1) then
	        call pgpoint(1,radius(i),sr(i),4)
	      else
	        call pgpoint(1,radius(i),sr(i),5)
	      endif
	    enddo
	    call fplot(se,re,sstore,cstore,radius(1),radius(npts),chisqr,ifit)
          if(fwhm .ne. 0 .and. xmax < 20.*fwhm) then
            call gdraw(fwhm,xcore,xscale,cons)
          endif

	  else if(char.eq.'f') then
          xscale=abs(xscale)
          if(ifit == 2) then
            do i=1,npts
              radius(i)=radius(i)**4.
            enddo
	      xmax=xmax**4.
            xmin=radius(1)-0.1*(xmax-radius(1))
          endif
          ifit=3
	    nf=0
          se=0.
          re=0.
	    do i=1,npts
	      if(kill(i).ne.1) then
		  nf=nf+1
		  rf(nf)=radius(i)
		  sf(nf)=sr(i)
		endif
	    enddo
	    call fitx(nf,rf,sf,se,re,sstore,cstore,chisqr,2)
	    call fitx(nf,rf,sf,se,re,sstore,cstore,chisqr,nt)
	    call pgadvance
	    call pgwindow(xmin,xmax,ymax,ymin)
	    call pgbox('BCNST',0.,0,'BCNST',0.,0)
	    call pglabel('r (arcsec)','\\gm\\dR',name)
	    do i=1,npts
	      if(kill(i).ne.1) then
	        call pgpoint(1,radius(i),sr(i),4)
	      else
	        call pgpoint(1,radius(i),sr(i),5)
	      endif
	    enddo
	    call fplot(se,re,sstore,cstore,radius(1),radius(npts),chisqr,ifit)
          if(fwhm .ne. 0 .and. xmax < 20.*fwhm) then
            call gdraw(fwhm,xcore,xscale,cons)
          endif

	  else if(char.eq.'r') then
          ymax=-1.e33
          ymin=1.e33
          do i=1,npts
            if(sr(i).gt.ymax) ymax=sr(i)
            if(sr(i).lt.ymin) ymin=sr(i)
          enddo
          ymax=ymax+0.2*(ymax-ymin)
          ymin=ymin-0.2*(ymax-ymin)
          xmin=radius(1)-0.1*(radius(npts)-radius(1))
          xmax=radius(npts)+0.1*(radius(npts)-radius(1))
	    call pgadvance
	    call pgwindow(xmin,xmax,ymax,ymin)
	    call pgbox('BCNST',0.,0,'BCNST',0.,0)
	    if(ifit == 2) then
	      call pglabel('r\\u1/4','\\gm\\dR',name)
	    else
	      call pglabel('r (arcsec)','\\gm\\dR',name)
	    endif
	    do i=1,npts
	      if(kill(i).ne.1) then
	        call pgpoint(1,radius(i),sr(i),4)
	      else
	        call pgpoint(1,radius(i),sr(i),5)
	      endif
	    enddo
	    call fplot(se,re,sstore,cstore,radius(1),radius(npts),chisqr,ifit)
          if(fwhm .ne. 0 .and. xmax < 20.*fwhm) then
            call gdraw(fwhm,xcore,xscale,cons)
          endif

	  else if(char.eq.'b') then
          x1=x
          y1=y
	    call pgcurse(x,y,char)
          x2=x
          y2=y
          xmin=min(x1,x2)
          xmax=max(x1,x2)
          ymin=min(y1,y2)
          ymax=max(y1,y2)
	    call pgadvance
	    call pgwindow(xmin,xmax,ymax,ymin)
	    call pgbox('BCNST',0.,0,'BCNST',0.,0)
	    if(ifit == 2) then
	      call pglabel('r\\u1/4','\\gm\\dR',name)
	    else
	      call pglabel('r (arcsec)','\\gm\\dR',name)
	    endif
	    do i=1,npts
	      if(kill(i).ne.1) then
	        call pgpoint(1,radius(i),sr(i),4)
	      else
	        call pgpoint(1,radius(i),sr(i),5)
	      endif
	    enddo
	    call fplot(se,re,sstore,cstore,radius(1),radius(npts),chisqr,ifit)
          if(fwhm .ne. 0 .and. xmax < 20.*fwhm) then
            call gdraw(fwhm,xcore,xscale,cons)
          endif

	  endif
	enddo
999	end

	subroutine fplot(se,re,sstore,cstore,x1,x2,chisqr,ifit)
      character strng*50
      common xmin,xmax,ymin,ymax,nt

      alpha=1.0857/sstore
      write(strng,5) chisqr
5     format('\\gx\\u2\\d = ',1pe12.4)
      if(ifit == 1) then
	  xnt=cstore+sstore*x1
	  call pgmove(x1,xnt)
	  xnt=cstore+sstore*x2
	  call pgdraw(x2,xnt)
        ystep=(ymax-ymin)/20.
        xstep=(xmax-xmin)/20.
        call pgptxt(xmin+xstep,ymax-2.*ystep,0.,0.,strng)
        write(strng,10) cstore
10      format('\\gm\\do\\u = ',f5.2)
        call pgptxt(xmin+xstep,ymax-4.*ystep,0.,0.,strng)
        write(strng,20) alpha
20      format('\\ga = ',f7.2)
        call pgptxt(xmin+xstep,ymax-3.*ystep,0.,0.,strng)
        if(nt == 3) then
          call pgptxt(xmax-2.*xstep,ymin+ystep,0.,0.,'3P Fit')
        else
          call pgptxt(xmax-2.*xstep,ymin+ystep,0.,0.,'4P Fit')
        endif

      else if(ifit == 2) then
	  a1=se-8.325
        a2=8.325*(1./re)**.25
	  call pgsls(1)
	  call pgmove(x1,a2*x1+a1)
	  call pgdraw(x2,a2*x2+a1)
        ystep=(ymax-ymin)/20.
        xstep=(xmax-xmin)/20.
        call pgptxt(xmin+xstep,ymax-2.*ystep,0.,0.,strng)
        write(strng,30) se
30      format('\\gm\\de\\u = ',f5.2)
        call pgptxt(xmin+xstep,ymax-4.*ystep,0.,0.,strng)
        write(strng,40) re
40      format('r\\de\\u = ',f7.2)
        call pgptxt(xmin+xstep,ymax-3.*ystep,0.,0.,strng)
        if(nt == 3) then
          call pgptxt(xmax-2.*xstep,ymin+ystep,0.,0.,'3P Fit')
        else
          call pgptxt(xmax-2.*xstep,ymin+ystep,0.,0.,'4P Fit')
        endif

      else if(ifit == 3) then
        xbm = se - 5.*alog10(re) - 40.0
        xdm = cstore - 5.*alog10(alpha) - 38.6
        bdratio = 10.**(-0.4*(xbm - xdm))
        ystep=(ymax-ymin)/20.
        xstep=(xmax-xmin)/20.
        call pgptxt(xmin+xstep,ymax-2.*ystep,0.,0.,strng)
        write(strng,50) bdratio
50      format('B/D = ',f5.2)
        call pgptxt(xmin+xstep,ymax-7.*ystep,0.,0.,strng)
        write(strng,30) se
        call pgptxt(xmin+xstep,ymax-6.*ystep,0.,0.,strng)
        write(strng,40) re
        call pgptxt(xmin+xstep,ymax-5.*ystep,0.,0.,strng)
        if(nt == 3) then
          write(strng,10) cstore
        else
          write(strng,60) cstore
        endif
60      format('\\gm\\d*\\u = ',f5.2)
        call pgptxt(xmin+xstep,ymax-4.*ystep,0.,0.,strng)
        write(strng,20) alpha
        call pgptxt(xmin+xstep,ymax-3.*ystep,0.,0.,strng)
        if(nt == 3) then
          call pgptxt(xmax-2.*xstep,ymin+ystep,0.,0.,'3P Fit')
        else
          call pgptxt(xmax-2.*xstep,ymin+ystep,0.,0.,'4P Fit')
        endif

	  call pgsls(2)
	  xnt=cstore+sstore*x1
	  call pgmove(x1,xnt)
	  xnt=cstore+sstore*x2
	  call pgdraw(x2,xnt)

	  xstep=(x2-x1)/300.
	  do i=1,301
	    r=x1+(i-1)*xstep
	    xnt=se+8.325*((r/re)**0.25-1.)
	    xnt=-0.4*xnt
	    xnt1=10.**xnt
	    if(i.eq.1) then
	      call pgmove(r,-2.5*alog10(xnt1))
	    else
	      call pgdraw(r,-2.5*alog10(xnt1))
	    endif
	  enddo
	  call pgsls(1)
	  do i=1,301
	    r=x1+(i-1)*xstep
	    xnt=se+8.325*((r/re)**0.25-1.)
	    xnt=-0.4*xnt
	    xnt1=10**xnt
	    xnt=cstore+sstore*r
	    xnt=-0.4*xnt
	    xnt2=10**(xnt)
	    xnt3=xnt1+xnt2
	    if(i.eq.1) then
	      call pgmove(r,-2.5*alog10(xnt3))
	    else
	      call pgdraw(r,-2.5*alog10(xnt3))
	    endif
	  enddo
      endif
      return
      end

	subroutine fitx(npts,r,s,ie,re,sstore,cstore,chsqr,nt)

***	r,s = arrays of radius and surface brightness
***	npts = number of points
***	ie = eff. surface brightness
***	re = eff. radius
***	sstore = disk scale length
***	cstore = disk surface brightness (see format below for conversion 
***              to astrophysically meaningful values)
***   nt = number of parameters to fit (2 for r^1/4, 4 for B+D)
***	program would like some first guess to speed things up

	real ie
	real sigmay(1000),dela(10),sigma(10),yfit(1000),
     .	r(npts),s(npts),edge(10,2),a(10)

*	print '(a,$)', 'Do you wish all 4 parameters to be fit? y/(n) '
*	read(*,'(a)') rply

*** set sigmay
*	skyl=30.
*	do j=1,npts
*	  sigmay(j)=0.05+exp(-.922*(skyl-s(j)))
*	enddo
	do j=1,npts
	  sigmay(j)=1.
	enddo

*** intialize parameters
	nitlt=500
	if(nt.eq.3.and.sstore.eq.0) then
	  print*, 'Disk slope required for three parameter fits'
	  print*, ' '
	  return
	endif

*** computer guess if no input
	if(ie.eq.0) then
	  a(1)=22.
	  a(2)=10.
	  a(3)=22.
	  a(4)=3.e-2
	  if(nt.eq.2) then
          a(3)=cstore
	    a(4)=sstore
        endif
	else
	  a(1)=ie
	  a(2)=re
	  a(3)=cstore
	  a(4)=sstore
	endif

*** initialize step size
	dela(1)=0.1
	dela(2)=0.1
	dela(3)=0.1
	dela(4)=1.e-4

*** set edges of fit
	edge(1,1)=5.
	edge(1,2)=35.
	edge(2,1)=.5
	edge(2,2)=200.
	edge(3,1)=10.
	edge(3,2)=30.
	edge(4,1)=1.e-8
	edge(4,2)=.5

*** show fits to terminal
	nit=0
*	print*, ' '
*	print 90, npts,r(1),r(npts)
*90	format(' # of points = ',i3,' range = ',1pe8.2,' to ',1pe8.2)
*	print*, ' '
*	print*, '              -- Initial guess --'
*	print*, ' '
        alpha = 1.0857/a(4)
        xbm = a(1) - 5.*alog10(a(2)) - 40.0
        xdm = a(3) - 5.*alog10(alpha) - 38.6
        bdratio = 10.**(-0.4*(xbm - xdm))
*	print 100, nit,bdratio,(a(i),i=1,3),alpha,chsqr
*	print*, ' '
*	print*, ' '

*** call for grid search
300	call gridls(r,s,sigmay,npts,nt,1,a,dela,sigma,yfit,chsqr,edge)
	if(nt.eq.3) chsqr=chsqr*(npts-3)/(npts-4)
	nit=nit+1
      alpha = 1.0857/a(4)
      if(nit .gt. 5) Then
        xbm = a(1) - 5.*alog10(a(2)) - 40.0
        xdm = a(3) - 5.*alog10(alpha) - 38.6
        bdratio = 10.**(-0.4*(xbm - xdm))
      endif

*** compare to old fit for convergence test
	dif1=abs(a(1)-olda1)
	dif2=abs(a(2)-olda2)
	dif3=abs(a(3)-olda3)
	dif4=abs(a(4)-olda4)
	dif=dif1+dif2+dif3
	if(nt.eq.4) then
	  dif=(dif+10*olda4)/4
	else
	  dif=dif/3
	endif
	if((dif.lt.1e-7).and.(nit>50)) then
*	  print*, ' '
*	  print*, ' Parameters unchanged at the 0.1% level',nit,dif
	  goto 400
	endif
	olda1=a(1)
	olda2=a(2)
	olda3=a(3)
	olda4=a(4)

*** ever 20th step - reset step size
	if(mod(nit,20).eq.0) then
	   dela(1)=0.1
	   dela(2)=0.1
	   dela(3)=0.1
	   dela(4)=1.e-4
	endif
	if(nit.lt.nitlt) go to 300

*** query for more fits
400	xbm = a(1) - 5.*alog10(a(2)) - 40.0
      xdm = a(3) - 5.*alog10(alpha) - 38.6
      bdratio = 10.**(-0.4*(xbm - xdm))
*	print*, ' B/D   Ie   Re    B(0)    Alpha    chisqr'
*	print 100, bdratio,a(1),a(2),a(3),alpha,chsqr
100	format(f5.2,1x,f5.2,1x,f4.1,1x,f4.1,1x,1pe9.3,1x,1pe9.3)

*** set to meaningful values
	ie=a(1)
	re=a(2)
	cstore=a(3)
	sstore=a(4)
	return
	end

      subroutine gridls (x,y,sigmay, npts,nterms, mode, a, deltaa,
     1 sigmaa, yfit, chisqr,edge)
      dimension x(1),y(1),sigmay(1),a(1),deltaa(1),sigmaa(1),yfit(1)
     .,edge(10,2)
   11 nfree=npts - nterms
      free= nfree
      chisqr =0.
      if (nfree) 100,100,20
   20 do 90 j=1,nterms
***** evaluate chi square at first two seach points
   21 do 22 i=1,npts
   22 yfit(i)=airy(x,i,a,NTERMS)
   23 chisq1=fchisq(y,sigmay,npts,nfree,mode,yfit)
      fn=0.
      delta=deltaa(j)
   41 a(j)=a(j)+delta
      if(a(j) .lt. edge(j,1) .or. a(j) .gt. edge(j,2)) go to 82
      do 43 i=1,npts
   43 yfit(i)=airy(x,i,a,NTERMS)
   44 chisq2=fchisq(y,sigmay,npts,nfree,mode,yfit)
      if(chisq1-chisq2)51,61,61
***** reverse direction of search if chi square is increasing
   51 delta=-delta
      a(j)=a(j)+delta
      do 54 i=1,npts
   54 yfit(i)=airy(x,i,a,NTERMS)
      save=chisq1
      chisq1=chisq2
   57 chisq2=save
***** increnemt a(j) until chi square increases
   61 fn=fn+1.0
      a(j)=a(j)+delta
      if(a(j) .lt. edge(j,1) .or. a(j) .gt. edge(j,2)) go to 81
      do 64 i=1,npts
   64 yfit(i)=airy(x,i,a,NTERMS)
      chisq3=fchisq(y,sigmay,npts,nfree,mode,yfit)
   66 if(chisq3-chisq2) 71,81,81
   71 chisq1 = chisq2
      chisq2 = chisq3
      go to 61
***** find minimum of parpbola defined by last three points
   81 FIX=CHISQ3-CHISQ2
	IF(FIX.EQ.0) FIX=1.E-8
      delta=delta*(1./(1.+(chisq1-chisq2)/FIX)+0.5)
	FIX=FREE*(CHISQ3-2.*CHISQ2+CHISQ1)
	IF(FIX.EQ.0) FIX=1.E-8
   83 sigmaa(j)=deltaa(j)*sqrt(2./FIX)
   82 a(j)=a(j)-delta
   84 deltaa(j)=deltaa(j)*fn/3.
   90 continue
***** evaluate fit an chi square for final parameters
   91 do 92 i=1,npts
   92 yfit(i)=airy(x,i,a,NTERMS)
   93 chisqr=fchisq(y,sigmay,npts,nfree,mode,yfit)
  100 return
      end

***** chisqr subroutine *****
	function fchisq(s,sigmay,npts,nfree,mode,yfit)
	dimension s(1),sigmay(1),yfit(1)
	chisq=0.
	do 30 j=1,npts
30	chisq=chisq+((s(j)-yfit(j))**2)/sigmay(j)**2
	fchisq=chisq/nfree
	return
	end

***** fitting functions *****
	function airy(r,i,a,nterms)
	dimension r(1),a(4)
	common ie,re,sstore,cstore,chsqr
	xnt = a(1) + 8.325*((r(i)/a(2))**0.25 - 1.0)
	xnt = -0.4*xnt
	xnt1 = 10**xnt
	xnt =  a(3) + a(4)*r(i)
	if(nterms.eq.4) xnt = a(3) + a(4)*r(i)
	xnt = -0.4*xnt
	xnt2 = 10**(xnt) 
	xnt3 = xnt1 + xnt2
	airy = -2.5*(alog10(xnt3))
	return
	end

	subroutine linfit(x,y,npt,a,chisqr)
	real x(1),y(1),a(10),yfit(500),sigmay(500)
	sum=0.
	sumx=0.
	sumy=0.
	sumx2=0.
	sumy2=0.
	sumxy=0.
	do i=1,npt
	  x1=x(i)
	  y1=y(i)
*	  weight=1./sigmay(i)**2
	  weight=1.
	  sum=sum+weight
	  sumx=sumx+weight*x1
	  sumy=sumy+weight*y1
	  sumx2=sumx2+weight*x1*x1
	  sumy2=sumy2+weight*y1*y1
	  sumxy=sumxy+weight*x1*y1
	enddo
	delta=sum*sumx2-sumx*sumx
	a(1)=(sumx2*sumy-sumx*sumxy)/delta
	a(2)=(sumxy*sum-sumx*sumy)/delta
	nfree=npt-2
	do i=1,npt
	  yfit(i)=a(2)*x(i)+a(1)
        sigmay(i)=1.
	enddo
	chisqr=fchisq(y,sigmay,npt,nfree,mode,yfit)
	return
	end

	subroutine gdraw(b,a,xscale,cons)
      step=b*10./100.
      x=0.
      call pgsci(4)
      call pgsls(2)
      if(xscale.eq.0.) then
        call pgmove(x,a)
      else if(xscale < 0.) then
        call pgmove(x**0.25,-2.5*alog10(a/xscale**2)+cons)
      else
        call pgmove(x,-2.5*alog10(a/xscale**2)+cons)
      endif
      do i=1,100
        x=x+step
        y=a*exp(-0.5*x**2/b**2)
        if(xscale.eq.0.) then
          call pgdraw(x,y)
        else if(xscale < 0.) then
          call pgdraw(x**0.25,-2.5*alog10(y/xscale**2)+cons)
        else
          call pgdraw(x,-2.5*alog10(y/xscale**2)+cons)
        endif
      enddo
      call pgsci(1)
      call pgsls(1)
      return
      end
