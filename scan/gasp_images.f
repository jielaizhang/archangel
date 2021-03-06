C  Program  IMAGES
C
C    Reads in pixel-data and finds images above a threshold above
C    sky. Uses standard ipac im tools.
C
* WARNING - this program has a flaw for threshold < 1, integer problem
* this is somewhat fixed by letting Iint = 1 for Rint between 0 and 1

* this is a kluged up version of old GASP IMAGES, runs fast but coding is awful

      Integer*4 Np,Fcol,Lcol,Minpix,Line,Nlines,Ncols,imag
      integer*4 Maxcols/2048/,Nmax/4194304/
      Real*4 Trsh,Back,Pix(8192*8192),tmp(8192)
      Character Filnam*100,rply,op*2
      Logical Weight
      real nullval
      integer status,unit,readwrite,blocksize,naxes(2),nfound,bitpix
      integer naxis,pcount,gcount
      logical simple,extend

      imag=iargc()
      call getarg(1,op)
      if((op.eq.'-h').or.(op(1:1).ne.'-')) then
        print*, ' '
        print*, 'Usage: option file_name sky threshold minpix weight'
        print*, ' '
        print*, 'Options: -h = this mesage' 
        print*, '         -f = dump data'
        print*, '         -m = dump mark file'
        print*, '         -n = dump nexus file'
        print*, ' '
        print*, 'note: option required (fortran)'
        print*, ' '
        print*, 'note: that any char for weight will cancel'
        print*, 'lum weighting (output lum becomes area)'
        print*, ' '
        print*, 'note: this is OSX 10.8 version'
        goto 999
      endif    

*      open(unit=4,file='gasp_images.par')
*      read(4,'(a)') filnam
*      read(4,*) trsh
*      read(4,*) minpix
*      read(4,*) back
*      read(4,'(a)') rply
*      close(unit=4)
*      if(rply.eq.'y') then
*        weight=.true.
*      else
*        weight=.false.
*      endif

      status=0
      call getarg(2,filnam)
      call ftgiou(unit,status)
      call ftopen(unit,filnam,readwrite,blocksize,status)
      call ftghpr(unit,3,simple,bitpix,naxis,naxes,pcount,
     &       gcount, extend, status)
      ncols=naxes(1)
      nlines=naxes(2)
      dumnull=-1.
      nullval=sqrt(dumnull)
      call ftgpve(unit,1,1,ncols*nlines,nullval,pix,anynull,status)
      call ftclos(unit,status)
      call ftfiou(unit,status)

*      do i=1,ncols*nlines
*        print*, pix(i)
*      enddo

      call getarg(3,filnam)
      read(filnam,*) back
      call getarg(4,filnam)
      read(filnam,*) trsh
      call getarg(5,filnam)
      read(filnam,*) minpix
      weight=.true.
      call getarg(6,filnam)
      if(filnam == 'false') then
        weight=.false.
      else
        weight=.true.
      endif

      Fcol = 1
      Lcol = Ncols
* never called
*      If(.not.mindef) Fcol = 1
*      If(.not.maxdef) Lcol = Ncols
      Unit=0
      imag=0
      Call IMINIT(Nmax,Pix,Ncols,Fcol,Lcol,Back,Trsh,Minpix,Unit,
     *            Weight,op,tmp,Nmax,Line,Np,imag)
      imag=1
      Do Line=1,Nlines
        do j=1,Ncols
          tmp(j)=pix((line-1)*Ncols+j)
        enddo
* used to do ENTRY for IMAG and IMEND, now call IMINIT again with added terms
        Call IMINIT(Nmax,Pix,Ncols,Fcol,Lcol,Back,Trsh,Minpix,Unit,
     *              Weight,op,tmp,Nmax,Line,Np,imag)
      END DO
*1010 Call IMEND(Pix,Nmax,Line,Np)
 1010 imag=2
      Call IMINIT(Nmax,Pix,Ncols,Fcol,Lcol,Back,Trsh,Minpix,Unit,
     *            Weight,op,Pix,Nmax,Line,Np,imag)
999   stop
      End

      Subroutine IMINIT(Nmax,Rast,Ncols,Fcol,Lcol,Back,Trsh,Minpix,
     $         Unit,Weight,op,tmp,Mcols,Line,Np,imag)
      Implicit none      
C
C Calculates moments of connected images.
C    Output goes to unit UNIT.
C
* alot of added variables to get it to do the right thing

      Integer*4 Ncols,Ix,Line,Fcol,Lcol,imag,Mcols
      real*4 X0(8192),Y0(8192),Back,Back2
      Integer*4 Np,M,Lut(8192),Unit,Minpix,Imnum,Nmax,Nim/8192/
      Integer*4 Impix(8192),Nxtpix(8192),Im(8192)
      Integer*4 Fcol2,Lcol2,Minpix2,Unit2,Isa,Bin2
      Integer*4 Npix(8,8192),IInt,i,j,k,nxtim,l,ima,itot,isp,imp,ii
      Real*4 Trsh3,Trsh2,Trsh,Rint,Sum(6,8192),dx,dy
*      Real*4 Rast(Ncols),tmp(Ncols)  <- not clear this works with different entrance not ENTRY
      Real*4 Rast(8192*8192),tmp(8192)
      Logical Weight2,Data,Weight
      character op*2

* kludge fix for no ENTRY in g77
      if(imag.eq.1) goto 20
      if(imag.eq.2) goto 25

      Fcol2=Fcol
      Lcol2=Lcol
      Back2=Back
      Minpix2=Minpix
      Bin2 = 1
      Unit2=Unit
      Trsh2=Trsh
      Trsh3=Trsh
      If(.NOT.Weight) Trsh3=0.0
      Weight2=Weight
      Do I=1,7
        K=2**I
        Do J=K/2,K-1
          Lut(J)=I
        END DO
      END DO
      Nxtim=1
      Do I=1,Nim
        Im(I)=I+1
      END DO
      Return

* kludge fix for entry which is not allowed in g77
* new entrances and reset Rast from tmp variable
*     Entry IMAG(Rast,Ncols,Line,Np)
20    Data=.TRUE.
      Go to 30
*     Entry IMEND(Rast,Ncols,Line,Np)
25    Data=.FALSE.
30    Np=0
*      Ncols=Mcols
      rast(1)=tmp(1)
      do ii=1,ncols
        rast(ii)=tmp(ii)
      enddo

      Do Ix=Fcol2,Lcol2
*        if(Rast(Ix)-Back2-Trsh2.gt.0.) print*, Ix,Rast(Ix),Back2,Trsh2
        If(.NOT.Data) THEN
          L=0
          Go to 50
        END IF
*   40   If( Rast(Ix).LT.-1000 ) THEN
   40   If( Rast(Ix).ne.Rast(Ix) ) THEN
*          print*, 'not ok',Rast(Ix)
          Rint=0
        ELSE
*          if(Rast(Ix)-Back2-Trsh2.gt.0.) print*, 'ok',Ix,Rast(Ix)
*          print*, 'ok',Ix,Rast(Ix)
          Rint=Rast(Ix)-Back2-Trsh2
        END IF
*        If(Rint.LT.1.0) THEN  <- old if for integers
        If(Rint.LE.0.0) THEN
          M=0
        ELSE
          If(Rint.GE.128.0) THEN
            M=8
          ELSE
            IInt = Rint
* kludge to get real number rint between 0 and 1 to work
            if(iint.eq.0) iint=1
            M=Lut(IInt)
          END IF
        END IF
        L=0
        If(M.GT.0) L=1
*        if(rint.gt.0) then
*          l=1
*          m=1
*        endif
*        if(rint.gt.0) type*, line,ix,rint,m,l,iint
        If(.NOT.Weight2) Rint=1.0
   50   Isa=Isign(1,Impix(Ix))
        If(Impix(Ix).EQ.0) Isa=0
        Ima=Iabs(Impix(Ix))
        If(Isa.EQ.L) Go to 499
        If(Isa.EQ.0) Go to 299
        If(Nxtpix(Ix).EQ.0.AND.Im(Ima).EQ.Ix) Go to 200
C                                                          Remove
        K=Im(Ima)
        If(K.EQ.Ix) Go to 120
  110   If(Nxtpix(K).EQ.Ix) Go to 130
        K=Nxtpix(K)
        Go to 110
  120   Im(Ima)=Nxtpix(Ix)
        Go to 140
  130   Nxtpix(K)=Nxtpix(Ix)
  140   Nxtpix(Ix)=0
        Go to 298
C                                                            Delete
  200   Itot=Npix(1,Ima)
        Do I=2,8
          Itot=Itot+Npix(I,Ima)
        END DO
        If(Itot.LT.Minpix2) Go to 260
        Np=Np+1
        Imnum=Imnum+1
        If(Bin2.NE.0) Imnum=Bin2
        Call MOMENTS(X0(Ima),Y0(Ima),Sum(1,Ima),Npix(1,Ima),Trsh3,Imnum,
     $    Unit2,op)
  260   Do J=1,6
          Sum(J,Ima)=0.0
        END DO
        Do J=1,8
          Npix(J,Ima)=0
        END DO
        Im(Ima)=Nxtim
        Nxtim=Ima
  298   Impix(Ix)=0
        If(L.EQ.0) Go to 700
  299   If(Ix.EQ.1) Go to 300
        Isp=Isign(1,Impix(Ix-1))
        If(Impix(Ix-1).EQ.0) Isp=0
        If(Isp.EQ.L) Go to 400
C                                                              Start
  300   If(Nxtim.GT.Nim) Stop 'Too many images on one line'
*        print*, 'starting'
        Impix(Ix)=Nxtim
        X0(Impix(Ix))=Float(Ix)
        Y0(Impix(Ix))=Float(Line)
        Nxtim=Im(Nxtim)
        Im(Impix(Ix))=Ix
        Impix(Ix)=Impix(Ix)*L
        Go to 600
C                                                               Build
  400   Impix(Ix)=Impix(Ix-1)
        K=Ix-1
  410   If(Nxtpix(K).EQ.0) Go to 420
        K=Nxtpix(K)
        Go to 410
  420   Nxtpix(K)=Ix
        Go to 600
  499   If(L.EQ.0) Go to 700
        If(Ix.EQ.1) Go to 600
        Isp=Isign(1,Impix(Ix-1))
        If(Impix(Ix-1).EQ.0) Isp=0
        If(Impix(Ix-1).EQ.Impix(Ix)) Go to 600
        If(Isp.NE.Isa) Go to 600
C                                                                Join
  500   Imp=Iabs(Impix(Ix-1))
        Dx=X0(Imp)-X0(Ima)
        Dy=Y0(Imp)-Y0(Ima)
        Sum(1,Ima)=Sum(1,Ima)+Sum(1,Imp)+Sum(6,Imp)*Dx
        Sum(2,Ima)=Sum(2,Ima)+Sum(2,Imp)+Sum(6,Imp)*Dy
        Sum(3,Ima)=Sum(3,Ima)+Sum(3,Imp)+2*Sum(1,Imp)*Dx
     $    +Sum(6,Imp)*Dx*Dx
        Sum(4,Ima)=Sum(4,Ima)+Sum(4,Imp)+2*Sum(2,Imp)*Dy
     $    +Sum(6,Imp)*Dy*Dy
        Sum(5,Ima)=Sum(5,Ima)+Sum(5,Imp)+Sum(2,Imp)*Dx
     $    +Sum(1,Imp)*Dy+Sum(6,Imp)*Dx*Dy
        Sum(6,Ima)=Sum(6,Ima)+Sum(6,Imp)
        Do J=1,6
          Sum(J,Imp)=0.0
        END DO
        Do J=1,8
          Npix(J,Ima)=Npix(J,Ima)+Npix(J,Imp)
          Npix(J,Imp)=0
        END DO
        K=Ix
  520   If(Nxtpix(K).EQ.0) Go to 530
        K=Nxtpix(K)
        Go to 520
  530   Nxtpix(K)=Im(Imp)
        K=Im(Imp)
        Im(Imp)=Nxtim
        Nxtim=Imp
  540   Impix(K)=Impix(Ix)
        K=Nxtpix(K)
        If(K.GT.0) Go to 540
C                                                               Add
  600   Ima=Iabs(Impix(Ix))
*        print*, 'adding',Ima
        Dx=Ix-X0(Ima)
        Dy=Line-Y0(Ima)
        Sum(1,Ima)=Sum(1,Ima)+Rint*Dx
        Sum(2,Ima)=Sum(2,Ima)+Rint*Dy
        Sum(3,Ima)=Sum(3,Ima)+Rint*Dx*Dx
        Sum(4,Ima)=Sum(4,Ima)+Rint*Dy*Dy
        Sum(5,Ima)=Sum(5,Ima)+Rint*Dx*Dy
        Sum(6,Ima)=Sum(6,Ima)+Rint
*        print*, (sum(i,Ima),i=1,6)
        Npix(M,Ima)=Npix(M,Ima)+1
*        print*, 'npix',npix(m,ima),m,ima
  700 continue
      END DO
      Return
      End

      Subroutine MOMENTS(X0,Y0,Sum,Npix,Trsh,Ngal,Unit,op)
      Implicit none      
C
C  Receives raw image data and calculates image-parameters.
C  Output is sent to unit UNIT and to the terminal.
C
      Integer*4 Unit,Ngal
      real*4 X0,Y0
      Integer*4 Linout/0/,Npix(8),J
      Real*4 Theta,Galno,Zero,Sum(6),E,YY,XX,XY,Xpos,Ypos,No(8),rr,t2
      Real*4 Trsh
      character op*2
c
      Galno=Ngal
      Xpos=Sum(1)/Sum(6)+X0
      Ypos=Sum(2)/Sum(6)+Y0
      XX=(Sum(3)-Sum(1)*Sum(1)/Sum(6))/Sum(6)
      YY=(Sum(4)-Sum(2)*Sum(2)/Sum(6))/Sum(6)
      XY=(Sum(5)-Sum(1)*Sum(2)/Sum(6))/Sum(6)
      E=0.0
      Theta=0.0
      RR=XX+YY
      If(RR.EQ.0.0) Go to 20
      E=XX-YY
      E=Sqrt(E*E+4.0*XY*XY)/RR
      T2=0.5*RR*(1.0+E)-YY
      If(T2.EQ.0.0) Go to 20
      Theta=Atan(XY/T2)*57.29578
   20 No(8)=Npix(8)
      Do J=7,1,-1
        No(J)=No(J+1)+Npix(J)
      END DO
      Sum(6)=Sum(6)+No(1)*Sign(Trsh,Sum(6))

      j=no(1)
      if(e.lt.1.) then
        write(*,666) xpos,ypos,j,e,theta,-2.5*alog10(sum(6))
      endif
666   format(2f7.1,i8,f7.3,f7.1,f11.4)
      if(op.eq.'-n') then 
        write(*,*) sum(6),2.*sqrt(no(1)/(3.14159*(1.-e))),e,
     *             theta,xpos,ypos
      endif
      if(op.eq.'-m') then       
        write(*,667) xpos,ypos,2.*sqrt(no(1)/(3.14159*(1.-e))),
     *               (1.-e)*2.*(sqrt(no(1)/(3.14159*(1.-e)))),theta
667     format('mark ',2f7.1,' el red ',3f8.1)
      endif  

*      If(Term) Write(*,99998) Xpos,Ypos,No(1),E,Theta,sum(6)
* old GASP write to indirect format file
*      If(Unit.GT.0) THEN
*        Linout=Linout+1
*        Write(Unit,Rec=Linout) Sum(6),Zero,Zero,No,RR,E,Theta,Xpos,Ypos,
*     $    Trsh,Galno
*      END IF
      Return
      End
