      character name*20
      real*4 z,prob,x(1000000),y(1000000)

      n=iargc()
      call getarg(1,name)

      open(unit=1,file=name,status='old',err=999)
      do while (.true.)
        npts=npts+1
        read(1,*,end=200) x(npts),y(npts)
      enddo
200   npts=npts-1
      close(unit=1)
      call getarg(2,name)
      read(name,*) xmin
      call getarg(3,name)
      read(name,*) xmax
      call getarg(4,name)
      read(name,*) ymin
      call getarg(5,name)
      read(name,*) ymax
      call getarg(6,name)
      read(name,*) xbox 

      ibox=xbox
      dx=(xmax-xmin)/xbox
      dy=(ymax-ymin)/xbox
      yy=ymin+dy/2.
      do jj=1,ibox
        yy=ymin+(jj-1)*dy+dy/2.
        do ii=1,ibox
          xx=xmin+(ii-1)*dx+dx/2.
          xn=0.
          do i=1,npts
*            print*, x(i),y(i)
*            print*, -(x(i)-(xx-dx/2.))/dx,-(x(i)-(xx+dx/2.))/dx
            call slice(-(x(i)-(xx-dx/2.))/dx,-(x(i)-(xx+dx/2.))/dx,xn1)
*            print*, ii,jj,'xn1',xn1
            call slice(-(y(i)-(yy-dy/2.))/dy,-(y(i)-(yy+dy/2.))/dy,xn2)
*            print*, ii,jj,'xn2',xn2
            xn=xn+xn1*xn2
          enddo
          write(*,100,advance='no') xn
*100       format(1pe12.4)
100       format(f12.4)
        enddo
        write(*,*)
      enddo
999   end

      subroutine slice(x,y,rr)
      if (x.gt.y) then
        rr=0.
        return
      endif
      call lzprob(y,t1)
      call lzprob(abs(x),t2)
      call lzprob(abs(y),t3)
      if (x.lt.0.and.y.ge.0.) then
        rr=(t1-0.5)+(t2-0.5)
      else
        rr=abs((t3-0.5)-(t2-0.5))
      endif
      return
      end

      subroutine lzprob(z,prob)
      Z_MAX = 6.0
      if (z.eq.0.0) then
        x = 0.0
      else
        y = 0.5 * abs(z)
        if(y.ge.(Z_MAX*0.5)) then
          x = 1.0
        else if (y.lt.1.0) then
          w = y*y
          x = ((((((((0.000124818987 * w
     *                  -0.001075204047) * w +0.005198775019) * w
     *                -0.019198292004) * w +0.059054035642) * w
     *              -0.151968751364) * w +0.319152932694) * w
     *            -0.531923007300) * w +0.797884560593) * y * 2.0
        else
           y = y - 2.0
           x = (((((((((((((-0.000045255659 * y
     *                       +0.000152529290) * y -0.000019538132) * y
     *                     -0.000676904986) * y +0.001390604284) * y
     *                   -0.000794620820) * y -0.002034254874) * y
     *                 +0.006549791214) * y -0.010557625006) * y
     *               +0.011630447319) * y -0.009279453341) * y
     *             +0.005353579108) * y -0.002141268741) * y
     *           +0.000535310849) * y +0.999936657524
        endif
      endif
      if (z.gt.0.0) then
        prob = ((x+1.0)*0.5)
      else
        prob = ((1.0-x)*0.5)
      endif
      return
      end
