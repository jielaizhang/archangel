* this is a quick code to test various FORTRAN90 options

      character*20 suffix
      real vertices(3)
      integer day, x(4)
      real*8 pi

      x=(/ 1,2,3,4 /)

*      print '(e12.3,es12.3,en12.3)', x,x,x
      print '(2pe12.3)', x

      y=1; z=2; pi=2.*asin(1.) ! multiple assigns per line

      print*, 'initialization test',iflag  ! iflag will only be zero if -finit-local-zero option used

      do day=1,32
        select case (day)
          case(1, 21, 31)
            suffix='st'
          case(2, 22)
            suffix='nd'
          case(3, 23)
            suffix='rd'
          case(4:20, 24:30)
            suffix='th'
          case default
            suffix='XX'    ! bizarre bug means that last case must be only 1 line
        end select
        write(*,'(i4,a2)') day,suffix
      enddo

      do                      ! open end do loop
        n=n+1
        print*, n
        if(n > 10) exit       ! exit to break loop
        if(n > 5) cycle       ! cycle loop after 5
        print*, 'no cycle'
      enddo

      end
