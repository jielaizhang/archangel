*
*  Polynomial fitting/anaylsis program
*
*  J. Schombert - October 1984
*
*  reads and stores data for polynominal fitting
*
*
	real x(100000),y(100000),x2(100000),y2(100000)
	real a(10),b(10),sigmay(100000),sig2(100000)
	integer iflag(100000)
	character file*30,oldfile*30,rply,char,type*5,title*30
	character pstrng*50,strng1*15,strng2*15,xlabel*30,ylabel*30

	open(unit=9,file='tmp.oberon')
      call pgbegin(7,'/xwin',1,1)
      call pgask(0)
	call pgupdt(1)
      call pgscr(0,1.,1.,1.)
      call pgscr(1,0.,0.,0.)
	call pgscf(2)
*	write(*,*) ' '
*	write(*,*) ' f  = calculate fit        b = redfine borders'
*	write(*,*) ' /  = exit                 c = change fit parameters'
*	write(*,*) ' 1  = cancel first quad    2 = cancel second quad'
*	write(*,*) ' 3  = cancel third quad    4 = cancel fourth quad'
*	write(*,*) ' h  = increase weight(2x)  l = decrease weight(2x)'
*	write(*,*) ' x  = erase 1 point        s = erase n sigmas'
*	write(*,*) ' d  = new data set         p = hardcopy into oberon.ps'
*	write(*,*) ' '

      n=iargc()
      call getarg(1,file)
      if(file.eq.' ') then
        write(*,'(a,$)') 'Enter file name: '
        read(*,'(a)',end=999) file
      endif
	oldfile=file
	write(*,'(a,$)') 'Enter column numbers: '
	read(*,*) jack,jill
	if(jack.lt.0) then
	 ijack=1
	 jack=abs(jack)
	endif
	write(*,'(a,$)') 'Error column? y/(n): '
	read(*,'(a)') rply
	if(rply.eq.'y') then
	  write(*,'(a,$)') 'Enter error column: '
	  read(*,*) ierr
	endif
	iflipx=1
	iflipy=1
	write(*,'(a,$)') 'Flip x axis y/(n): '
	read(*,'(a)') rply
	if(rply.eq.'y') iflipx=-1
	write(*,'(a,$)') 'Flip y axis y/(n): '
	read(*,'(a)') rply
	if(rply.eq.'y') iflipy=-1
	iquad=2
	write(*,'(a,$)') 'Enter xlabel: '
	read(*,'(a)') xlabel
	write(*,'(a,$)') 'Enter ylabel: '
	read(*,'(a)') ylabel
	write(*,'(a,$)') 'Enter title: '
	read(*,'(a)') title
	do i=1,100000
	  sigmay(i)=1.
	enddo
	open(unit=1,file=file)
	do while (.true.)
	  read(1,*,end=20) (a(i),i=1,max(ierr,jill,jack))
	  npts=npts+1
	  y(npts)=iflipy*a(jill)
          if(ijack.eq.0) then
	    x(npts)=iflipx*a(jack)
	  else
	    x(npts)=iflipx*alog10(a(jack))
	  endif
	  if(ierr.ne.0) sigmay(npts)=a(ierr)
	enddo
20	xlow=1.e10
	xhi=-1.e10
	ylow=1.e10
	yhi=-1.e10
        do i=1,npts
	  if(x(i).lt.xlow) xlow=x(i)
	  if(x(i).gt.xhi) xhi=x(i)
	  if(y(i).lt.ylow) ylow=y(i)
	  if(y(i).gt.yhi) yhi=y(i)
	enddo
	xlow=xlow-0.1*(xhi-xlow)
	xhi=xhi+0.1*(xhi-xlow)
	ylow=ylow-0.1*(yhi-ylow)
	yhi=yhi+0.1*(yhi-ylow)
	xlow2=xlow
	xhi2=xhi
	ylow2=ylow
	yhi2=yhi
30	inv=1
	write(*,'(a,$)') 'Inverse fit? y/(n): '
	read(*,'(a)') rply
	if(rply.eq.'y') inv=-1
	write(*,'(a,$)') 'Enter order of fit: '
	read(*,*) norder
40	num=0
	do i=1,npts
	  if(iflag(i).ne.1) then
	    num=num+1
	    sig2(num)=sigmay(i)
	    if(inv.eq.-1) then
              x2(num)=y(i)
              y2(num)=x(i)
	    else
	      x2(num)=x(i)
              y2(num)=y(i)
	    endif
	  endif
	enddo
	if(norder.eq.1) then
	  call linfit(x2,y2,sig2,num,a,sig)
	  print*, a(1),a(2),a(4),a(5)
	else
	  call polfit(x2,y2,num,(norder+1),a,chi,sig2,sig)
	endif
5000	vx=1./2500.
	vy=1./2000.
	if(char.eq.'p'.or.char.eq.'P') then
	  if(ifirst.eq.0) then
	    write(*,*) 'plotting - output to oberon.ps'
	    call pgend
	    call pgbegin(7,'oberon.ps/ps',1,1)
	    call pgscf(2)
	    call pgadvance
	    call pgvport(.1,.9,.1,.9)
	    call pgwindow(iflipx*xlow,iflipx*xhi,iflipy*ylow,iflipy*yhi)
	    call pgbox('bcnst',0.,0, 'bcnst',0.,0)
	    call pgwindow(xlow,xhi,ylow,yhi)
	    call pglabel(xlabel,ylabel,title)
	    ifirst=1
          else
	    call pgend
            call pgbegin(7,'?',1,1)
            call pgask(0)
            call pgscr(0,1.,1.,1.)
            call pgscr(1,0.,0.,0.)
	    call pgscf(2)
	    call pgupdt(1)
	    call pgadvance
	    call pgvport(.1,.9,.1,.9)
	    call pgwindow(iflipx*xlow,iflipx*xhi,iflipy*ylow,iflipy*yhi)
	    call pgbox('bcnst',0.,0, 'bcnst',0.,0)
	    call pgwindow(xlow,xhi,ylow,yhi)
	    call pglabel(xlabel,ylabel,title)
	    char=' '
	    ifirst=0
	  endif
	else
	  call pgadvance
	  call pgvport(.1,.9,.1,.9)
	  call pgwindow(iflipx*xlow,iflipx*xhi,iflipy*ylow,iflipy*yhi)
	  call pgbox('bcnst',0.,0, 'bcnst',0.,0)
	  call pgwindow(xlow,xhi,ylow,yhi)
	  call pglabel(xlabel,ylabel,title)
	endif
        do i=1,npts
          if(iflag(i).eq.0) then
	    call pgpoint(1,x(i),y(i),17)
	  else
	    call pgpoint(1,x(i),y(i),5)
	  endif
	enddo
        if(inv.eq.1) then
          step=(xhi-xlow)/100.
          xstep=xlow
        else
          step=(yhi-ylow)/100.
          xstep=ylow
        endif
        do i=1,101
          sum=0.
          do j=1,norder+1
	    if(xstep.ne.0.) then
	      sum=sum+a(j)*xstep**(j-1)
	    else
	      sum=a(1)
	    endif
	  enddo
          if(i.eq.1.and.inv.eq.1) call pgmove(xlow,sum)
          if(i.eq.1.and.inv.eq.-1) call pgmove(sum,ylow)
          if(inv.eq.1) then
	    call pgdraw(xstep,sum)
	  else
            call pgdraw(sum,xstep)
	  endif
	  xstep=xstep+step
	enddo
	if(inv.eq.1) then
	  type='X->Y '
	else
	  type='Y->X '
	endif
	ty=.93*(yhi-ylow)+ylow
	if(iquad.eq.2) tx=.04*(xhi-xlow)+xlow
	if(iquad.eq.1.and.norder.eq.1) tx=.40*(xhi-xlow)+xlow
	if(iquad.eq.1.and.norder.gt.1) tx=.65*(xhi-xlow)+xlow
	dy=.04*(yhi-ylow)
	r=a(3)
	sb=a(4)
	sm=a(5)
	do j=1,10
	  b(j)=a(j)
	enddo
	if(iflipx.eq.-1.and.iflipy.eq.-1) then
	  do j=1,norder+1
	    b(j)=a(j)*iflipx**j
	  enddo
	endif
	if((iflipx.eq.-1.and.inv.eq.1).or.(iflipy.eq.-1.and.inv.eq.-1)) then
 	  do j=1,norder+1
	    b(j)=a(j)*(iflipx**(j-1))*(iflipy**(j-1))
	  enddo
	endif 
	if((iflipy.eq.-1.and.inv.eq.1).or.(iflipx.eq.-1.and.inv.eq.-1)) then 
	  do j=1,norder+1
	    b(j)=a(j)*iflipx*iflipy
	  enddo
	endif
	if(norder.eq.1) then
	  write(pstrng,1000) type
1000	  format(a5,'1\\ust\\d order fit')
          call pgptext(tx,ty,0.,0.,pstrng)
          call number(strng1,b(2),0,0)
          call number(strng2,b(1),0,0)
          call pgptext(tx,ty-dy,0.,0.,'m  = '//strng1//'b  = '//strng2)
          call number(strng1,sm,0,0)
          call number(strng2,sb,0,0)
          call pgptext(tx,ty-1.9*dy,0.,0.,
     *           '\\gs\\dm\\u = '//strng1//'\\gs\\db\\u = '//strng2)
          call number(strng1,r,0,0)
          call number(strng2,sig,0,0)
          call pgptext(tx,ty-3*dy,0.,0.,
     *		       'R  = '//strng1//'\\gs  = '//strng2)
	  write(9,*) b(2),b(1),sm,sb,r,sig
	else
	  if(norder.eq.2) write(pstrng,1010) type,norder
1010      format(a5,i1,'\\und\\d order fit')
          if(norder.eq.3) write(pstrng,1020) type,norder
1020      format(a5,i1,'\\urd\\d order fit')
          if(norder.ge.4) write(pstrng,1030) type,norder
1030      format(a5,i1,'\\uth\\d order fit')
          call pgptext(tx,ty,0.,0.,pstrng)
          do j=1,norder+1
            call number(strng1,b(j),0,0)
            write(pstrng,1040) j,strng1
1040        format('A(',i1,') = ',a15)
            write(*,*) b(j)
	      call pgptext(tx,ty-j*dy,0.,0.,pstrng)
	    enddo
	  call number(strng1,sig,0,0)
	  call pgptext(tx,ty-j*dy,0.,0.,'\\gs = '//strng1)
	  write(9,*) (b(j),j=1,norder+1),sig
	endif
500	if(char.eq.'p'.or.char.eq.'P') goto 5000
        call pgcurse(w,z,char)
	if(char.eq.'f'.or.char.eq.'F') goto 40
	if(char.eq.'b'.or.char.eq.'B') goto 200
	if(char.eq.'/') goto 999
	if(char.eq.'1') goto 510
	if(char.eq.'2') goto 520
	if(char.eq.'3') goto 530
	if(char.eq.'4') goto 540
	if(char.eq.'c'.or.char.eq.'C') goto 30
	if(char.eq.'h'.or.char.eq.'H') goto 3000
	if(char.eq.'l'.or.char.eq.'L') goto 3000
	if(char.eq.'s'.or.char.eq.'S') goto 4000
	if(char.eq.'p'.or.char.eq.'P') goto 5000
	if(char.eq.'x'.or.char.eq.'X') goto 505
	if(char.eq.'?') then
 	  write(*,*) ' '
 	  write(*,*) ' f  = calculate fit        b = redfine borders'
 	  write(*,*) ' n  = new colums           c = change fit parameters'
 	  write(*,*) ' 1  = cancel first quad    2 = cancel second quad'
 	  write(*,*) ' 3  = cancel third quad    4 = cancel fourth quad'
 	  write(*,*) ' h  = increase weight(2x)  l = decrease weight(2x)'
 	  write(*,*) ' x  = erase 1 point        s = erase n sigmas'
 	  write(*,*) ' d  = new data set         p = hardcopy into oberon.ps'
 	  write(*,*) ' '
	  goto 500
	endif
	if(char.eq.'d'.or.char.eq.'n') then
	  if(char.eq.'d') then
	    write(*,'(a,$)') 'Enter data file name: '
	    read(*,'(a)') file
	    if(file.eq.' ') file=oldfile
	  endif
	  write(*,'(a,$)') 'Enter column numbers: '
	  read(*,*) jack,jill
	  write(*,'(a,$)') 'Error column? y/(n): '
	  read(*,'(a)') rply
	  if(rply.eq.'y') then
	    write(*,'(a,$)') 'Enter error column: '
	    read(*,*) ierr
	  endif
	  iflipx=1
	  iflipy=1
	  write(*,'(a,$)') 'Flip x axis y/(n): '
	  read(*,'(a)') rply
	  if(rply.eq.'y') iflipx=-1
	  write(*,'(a,$)') 'Flip y axis y/(n): '
	  read(*,'(a)') rply
	  if(rply.eq.'y') iflipy=-1
	  iquad=2
	  write(*,'(a,$)') 'Enter xlabel: '
	  read(*,'(a)') title
	  if(title.ne.' ') xlabel=title
	  write(*,'(a,$)') 'Enter ylabel: '
	  read(*,'(a)') title
	  if(title.ne.' ') ylabel=title
	  write(*,'(a,$)') 'Enter title: '
	  read(*,'(a)') title
	  do i=1,5000
	    sigmay(i)=1.
	  enddo
	  if(char.eq.'d') then
	    close(unit=1)
	    open(unit=1,file=file)
	  else
	    rewind(1)
	  endif
	  npts=0
	  do while (.true.)
	    read(1,*,end=1111) (a(i),i=1,max(ierr,jill,jack))
	    npts=npts+1
	    y(npts)=iflipy*a(jill)
            if(ijack.eq.0) then
	      x(npts)=iflipx*a(jack)
	    else
	      x(npts)=iflipx*alog10(a(jack))
	    endif
	    iflag(npts)=0
	    if(ierr.ne.0) sigmay(npts)=a(ierr)
	  enddo
1111	  xlow=1.e10
	  xhi=-1.e10
	  ylow=1.e10
	  yhi=-1.e10
          do i=1,npts
	    if(x(i).lt.xlow) xlow=x(i)
	    if(x(i).gt.xhi) xhi=x(i)
	    if(y(i).lt.ylow) ylow=y(i)
	    if(y(i).gt.yhi) yhi=y(i)
	  enddo
	  xlow=xlow-0.1*(xhi-xlow)
	  xhi=xhi+0.1*(xhi-xlow)
	  ylow=ylow-0.1*(yhi-ylow)
	  yhi=yhi+0.1*(yhi-ylow)
	  xlow2=xlow
	  xhi2=xhi
	  ylow2=ylow
	  yhi2=yhi
	  inv=1
	  write(*,'(a,$)') 'Inverse fit? y/(n): '
	  read(*,'(a)') rply
	  if(rply.eq.'y') inv=-1
	  write(*,'(a,$)') 'Enter order of fit: '
	  read(*,*) norder
	  goto 40
	endif
	goto 500
505     rmin=1.e33
	do i=1,npts
	  r=((x(i)-w)**2+(y(i)-z)**2)**.5
	  if(r.lt.rmin) then
	    imin=i
	    rmin=r
	  endif
	enddo
	if(iflag(imin).eq.0) then
	  call pgpoint(1,x(imin),y(imin),5)
	  iflag(imin)=1
	else
	  iflag(imin)=0
	  call pgpoint(1,x(imin),y(imin),17)
	endif
	goto 500
510	r1=w
	r2=xhi2
	s1=z
	s2=yhi2
	goto 560
520	r1=xlow2
	r2=w
	s1=z
	s2=yhi2
	goto 560
530	r1=xlow2
	r2=w
	s1=ylow2
	s2=z
	goto 560
540	r1=w
	r2=xhi2
	s1=ylow2
	s2=z
	goto 560
550	r1=w-(xhi-xlow)/200.
	r2=w+(xhi-xlow)/200.
	s1=z-(yhi-ylow)/200.
	s2=z+(yhi-ylow)/200.
560	do 400 i=1,npts
	  if(iflag(i).eq.1) goto 400
	  if(x(i).ge.r1.and.x(i).le.r2) goto 410
	  goto 400
410	  if(y(i).ge.s1.and.y(i).le.s2) goto 420
	  goto 400
420	  iflag(i)=1
	  call pgpoint(1,x(i),y(i),5)
400	continue
	goto 500
200	write(*,'(a,$)') 'Enter xlow,xhi,ylow,yhi..... '
	read(*,*) xlow,xhi,ylow,yhi
	xlow=xlow*iflipx
	ylow=ylow*iflipy
	xhi=xhi*iflipx
	yhi=yhi*iflipy
	write(*,'(a,$)') 'Enter print quadrant (1 or 2).. '
	read(*,*) iquad
	goto 5000
3000	ihi=ihi+1
	if(ihi.eq.2) goto 3100
	p1=w
	q1=z
	call pgpoint(1,w,z,2)
	goto 500
3100	ihi=0
	dq=2.
	if(char.eq.'h'.or.char.eq.'H') dq=.5
	p2=w
	q2=z
	call pgpoint(1,w,z,2)
	do 3200 i=1,npts
	  if(x(i).gt.p2.or.x(i).lt.p1) goto 3200
	  if(y(i).gt.q2.or.y(i).lt.q1) goto 3200
	  sigmay(i)=sigmay(i)*dq
3200	continue
	goto 500
4000	write(*,'(a,$)') 'Enter number of sigmas to delete... '
	read(*,*) xsig
	do i=1,npts
	  if(iflag(i).ne.1) then
	    if(inv.eq.1) then
	      w=x(i)
	      v=y(i)
	    else
	      w=y(i)
	      v=x(i)
	    endif
	    z=0.
	    do j=1,norder+1
	      z=z+a(j)*w**(j-1)
	    enddo
	    d=abs(v-z)
	    if(d.gt.(xsig*sig)) iflag(i)=1
	  endif
	enddo
      goto 40
999   call pgend
      end 

      subroutine linfit(x,y,s,n,coeff,sig)
*	from bevington chapter 6
      dimension x(100000),y(100000),coeff(10),s(100000)
      real*8 sum,sumx,sumy,sumx2,sumy2,sumxy,del,var
      sum=0.0
      sumx=0.0
      sumy=0.0
      sumxy=0.0
      sumx2=0.0
      sumy2=0.0
      do 250 k=1,n
      sum=sum+(1./s(k)**2)
      sumx=sumx+(1./s(k)**2)*x(k)
      sumy=sumy+(1./s(k)**2)*y(k)
      sumxy=sumxy+(1./s(k)**2)*x(k)*y(k)
      sumx2=sumx2+(1./s(k)**2)*x(k)*x(k)
      sumy2=sumy2+(1./s(k)**2)*y(k)*y(k)
 250  continue
      del=sum*sumx2-sumx*sumx
c     y intersect -- a
      coeff(1)=(sumx2*sumy-sumx*sumxy)/del
      a=coeff(1)
c     slope -- b
      coeff(2)=(sum*sumxy-sumx*sumy)/del
      b=coeff(2)
c     varience
      var=(sumy2+a*a*sum+b*b*sumx2-2.*(a*sumy+b*sumxy-a*b*sumx))/(n-2)
c     correlation coefficient -- r
      coeff(3)=(sum*sumxy-sumx*sumy)/(dsqrt(del*(sum*sumy2-sumy*sumy)))
c     sigma b
      coeff(4)=dsqrt(var*sumx2/del)
c     sigma m
      coeff(5)=dsqrt(var*sum/del)
      sig=0.
      do 100 k=1,n
      z=a+b*x(k)
 100  sig=sig+(z-y(k))**2
      sig=(sig/(n-1))**.5
 999  return
      end
      subroutine polfit(x,y,npts,nterms,a,chisqr,sigmay,sig)
      real*8 sumx(10),sumy(10),xterm,yterm,array(10,10),chisq
      real x(1),y(1),a(1),sigmay(1)
 11   nmax=2*nterms-1
      do 13 n=1,nmax
 13   sumx(n)=0.
      do 15 j=1,nterms
 15   sumy(j)=0.
      chisq=0.
 21   do 50 i=1,npts
      xi=x(i)
      yi=y(i)
      weight=1./sigmay(i)**2
 41   xterm=weight
      do 44 n=1,nmax
      sumx(n)=sumx(n)+xterm
 44   xterm=xterm*xi
 45   yterm=yi*weight
      do 48 n=1,nterms
      sumy(n)=sumy(n)+yterm
 48   yterm=yterm*xi
 49   chisq=chisq+weight*yi**2
 50   continue
 51   do 54 j=1,nterms
      do 54 k=1,nterms
      n=j+k-1
 54   array(j,k)=sumx(n)
      delta=determ(array,nterms)
      if(delta) 61,57,61
 57   chisqr=0.
      do 59 j=1,nterms
 59   a(j)=0.
      goto 80
 61   do 70 l=1,nterms
 62   do 66 j=1,nterms
      do 65 k=1,nterms
      n=j+k-1
 65   array(j,k)=sumx(n)
 66   array(j,l)=sumy(j)
 70   a(l)=determ(array,nterms)/delta
 71   do 75 j=1,nterms
      chisq=chisq-2*a(j)*sumy(j)
      do 75 k=1,nterms
      n=j+k-1
 75   chisq=chisq+a(j)*a(k)*sumx(n)
 76   free=npts-nterms
 77   chisqr=chisq/free
 80   sig=0.
      do 100 i=1,npts
      dum=0.
      do 110 j=1,nterms
	if(j.eq.1) then
	  dum=dum+a(j)
	else
	  dum=dum+a(j)*(x(i)**(j-1))
	endif
110   continue
 100  sig=sig+(y(i)-dum)**2
      sig=(sig/(npts-2))**.5
      return
      end
      function determ(array,norder)
      real*8 array(10,10),save
 10   determ=1.
 11   do 50 k=1,norder
      if(array(k,k)) 41,21,41
 21   do 23 j=k,norder
      if(array(k,j)) 31,23,31
 23   continue
      determ=0.
      goto 60
 31   do 34 i=k,norder
      save=array(i,j)
      array(i,j)=array(i,k)
 34   array(i,k)=save
      determ=-determ
 41   determ=determ*array(k,k)
      if(k-norder) 43,50,50
 43   k1=k+1
      do 46 i=k1,norder
      do 46 j=k1,norder
 46   array(i,j)=array(i,j)-array(i,k)*array(k,j)/array(k,k)
 50   continue
 60   return
      end
	subroutine number(strng,x,j,isw)
C  if isw = 0 -> do real x, if isw = 1 -> do integer j
	character strng*15
	if(isw.eq.1) goto 200
	if(x.eq.0.) then
	  write(strng,10) x
10	  format(f4.2)
	  goto 999
	endif
	i=1
	if(x.lt.0.) i=-1
	log=alog10(i*x)
	rem=x/10.**log
	do while (rem.gt.9.99.or.rem.lt.-9.99)
	  rem=rem/10.
	  log=log+1
	enddo
	if(log.le.-2) then
	  log=log-1
	  rem=rem*10.
	endif
	if(abs(rem).gt.+.1.and.log.eq.-1) then
	  log=log-1
	  rem=rem*10.
	endif
	if(x.lt.0) then
	  if(x.gt.-.1) then
	    if(log.ge.-9) write(strng,20) rem,log
20	    format(f5.2,'x10\\u',i2,'\\d')
	    if(log.lt.-9) write(strng,30) rem,log
30	    format(f5.2,'x10\\u',i3,'\\d')
	    goto 999
	  endif
	  if(x.ge.-9.99) then
	    write(strng,40) x
40	    format(f5.2)
	    goto 999
	  endif
	  if(x.ge.-99.99) then
	    write(strng,50) x
50	    format(f6.2)
	    goto 999
	  endif
	  if(x.lt.-99.99) then
	    if(log.le.9) write(strng,60) rem,log
60	    format(f5.2,'x10\\u',i1,'\\d')
	    if(log.gt.9) write(strng,70) rem,log
70	    format(f5.2,'x10\\u',i2,'\\d')
	  endif
	else
	  if(x.lt..1) then
	    if(log.ge.-9) write(strng,80) rem,log
80	    format(f4.2,'x10\\u',i2,'\\d')
	    if(log.lt.-9) write(strng,90) rem,log
90	    format(f4.2,'x10\\u',i3,'\\d')
	    goto 999
	  endif
	  if(x.le.9.99) then
	    write(strng,100) x
100	    format(f4.2)
	    goto 999
	  endif
	  if(x.le.99.99) then
	    write(strng,110) x
110	    format(f5.2)
	    goto 999
	  endif
	  if(x.gt.99.99) then
	    if(log.le.9) write(strng,120) rem,log
120	    format(f4.2,'x10\\u',i1,'\\d')
	    if(log.gt.9) write(strng,130) rem,log
130	    format(f4.2,'x10\\u',i2,'\\d')
	  endif
	endif
	goto 999
200	if(j.le.-10000) write(strng,210) j
	if(j.gt.-10000.and.j.le.-1000) write(strng,220) j
	if(j.gt.-1000.and.j.le.-100) write(strng,230) j
	if(j.gt.-100.and.j.le.-10) write(strng,240) j
	if(j.gt.-10.and.j.le.-1) write(strng,250) j
	if(j.ge.0.and.j.lt.10) write(strng,260) j
	if(j.ge.10.and.j.lt.100) write(strng,250) j
	if(j.ge.100.and.j.lt.1000) write(strng,240) j
	if(j.ge.1000.and.j.lt.10000) write(strng,230) j
	if(j.ge.10000) write(strng,220) j
210	format(i6)
220	format(i5)
230	format(i4)
240	format(i3)
250	format(i2)
260	format(i1)
999	return
	end
