C***********************************************************************
      SUBROUTINE TB04A (N,X,F,D,A)
C
C     FIT A CUBIC SPLINE  -  SAVE THE FIRST DERIVATIVES
C
C     FROM HARWELL LIBRARY
C
C###### 19/05/70 LAST LIBRARY UPDATE
C     DATA NP/6/
      DIMENSION X(N),F(N),D(N),A(1)
C F(I) ARE THE FUNCTION VALUES AT THE POINTS X(I) FOR I=1,N AND
C THE SPLINE DERIVATIVES D(I) ARE FOUND.  THE DIMENSION OF A MUST
C NOT BE LESS THAN 3*N. PERIPHERAL NP MUST BE AN OUTPUT MEDIUM.
      DO 5 I=2,N
      IF(X(I)-X(I-1))1,1,5
C1    WRITE(NP,3)I
C3     FORMAT(' RETURN FROM TB04A BECAUSE X('I3,') OUT OF ORDER')
    1 A(1)=1.
      RETURN
5     CONTINUE
      DO 30 I=1,N
      J=2
      IF(I-1)6,10,6
6     J=N-1
      IF(I.EQ.N)GO TO 10
      H1=1./(X(I)-X(I-1))
      H2=1./(X(I+1)-X(I))
      A(3*I-2)=H1
      A(3*I-1)=2.*(H1+H2)
      A(3*I)=H2
      D(I)=3*(F(I+1)*H2*H2+F(I)*(H1*H1-H2*H2)-F(I-1)*H1*H1)
      GO TO 30
10    H1=1./(X(J)-X(J-1))
      H2=1./(X(J+1)-X(J))
      A(3*I-2)=H1*H1
      A(3*I-1)=H1*H1-H2*H2
      A(3*I)=-H2*H2
      D(I)=2.*(F(J)*(H2*H2*H2+H1*H1*H1)-F(J+1)*H2*H2*H2-F(J-1)*H1*H1*H1)
30    CONTINUE
      P=A(4)/A(1)
      A(5)=A(5)-P*A(2)
      A(6)=A(6)-P*A(3)
      D(2)=D(2)-P*D(1)
      DO 50 I=3,N
      K=3*I-4
      P=A(K+2)/A(K)
      A(K+3)=A(K+3)-P*A(K+1)
      D(I)=D(I)-P*D(I-1)
      IF(I.NE.N-1)GO TO 50
      P=A(K+5)/A(K)
      A(K+5)=A(K+6)-P*A(K+1)
      A(K+6)=A(K+7)
      D(N)=D(N)-P*D(N-2)
50    CONTINUE
      D(N)=D(N)/A(3*N-1)
      DO 60 I=3,N
      J=N+2-I
60    D(J)=(D(J)-A(3*J)*D(J+1))/A(3*J-1)
      D(1)=(D(1)-D(2)*A(2)-D(3)*A(3))/A(1)
      A(1)=0.
      RETURN
      END
C***********************************************************************
      REAL FUNCTION TG01B*4(IX,N,U,S,D,X)
C
C     EVAULAUTE CUBIC SPLINE
C
C     FROM HARWELL LIBRARY
C
C###### 04/08/70LAST LIBRARY UPDATE
C
C**********************************************************************
C
C      TG01B -  FUNCTION ROUTINE TO EVALUATE A CUBIC SPLINE GIVEN SPLINE
C     VALUES AND FIRST DERIVATIVE VALUES AT THE GIVEN KNOTS.
C
C     THE SPLINE VALUE IS DEFINED AS ZERO OUTSIDE THE KNOT RANGE,WHICH
C     IS EXTENDED BY A ROUNDING ERROR FOR THE PURPOSE.
C
C                  F = TG01B(IX,N,U,S,D,X)
C
C       IX    ALLOWS CALLER TO TAKE ADVANTAGE OF SPLINE PARAMETERS SET
C             ON A PREVIOUS CALL IN CASES WHEN X POINT FOLLOWS PREVIOUS
C             X POINT. IF IX < 0 THE WHOLE RANGE IS SEARCHED FOR KNOT
C             INTERVAL; IF IX > 0 IT IS ASSUMED THAT X IS GREATER THAN
C             THE X OF THE PREVIOUS CALL AND SEARCH STARTED FROM THERE.
C       N     THE NUMBER OF KNOTS.
C       U     THE KNOTS.
C       S     THE SPLINE VALUES.
C       D     THE FIRST DERIVATIVE VALUES OF THE SPLINE AT THE KNOTS.
C       X     THE POINT AT WHICH THE SPLINE VALUE IS REQUIRED.
C       F     THE VALUE OF THE SPLINE AT THE POINT X.
C
C                                      MODIFIED JULY 1970
C
C**********************************************************************
C
C     ALLOWABLE ROUNDING ERROR ON POINTS AT EXTREAMS OF KNOT RANGE
C     IS 2**IEPS*MAX(!U(1)!,!U(N)!).
C     INTEGER*4 IFLG/0/,IEPS/-19/
      DATA IFLG,IEPS/0,-19/
      DIMENSION U(1),S(1),D(1)
C
C
      IF(X.LT.U(1)) GO TO 990
      IF(X.GT.U(N)) GO TO 991
C
C
      IF(IX.LT.0.OR.IFLG.EQ.0) GO TO 12
C
      IF(X.LE.U(J+1)) GO TO 8
C
    1 J=J+1
   11 IF(X.GT.U(J+1)) GO TO 1
      GO TO 7
C
C
   12 J=ABS(X-U(1))/(U(N)-U(1))*(N-1)+1
C
      J=MIN0(J,N-1)
C
      IFLG=1
C
      IF(X.GE.U(J)) GO TO 11
    2 J=J-1
      IF(X.LT.U(J)) GO TO 2
C
C
    7 H=U(J+1)-U(J)
      Q1=H*D(J)
      Q2=H*D(J+1)
      SS=S(J+1)-S(J)
      B=3.0*SS-2.0*Q1-Q2
      A=Q1+Q2-2.0*SS
C
C
    8 Z=(X-U(J))/H
      TG01B=((A*Z+B)*Z+Q1)*Z+S(J)
      RETURN
C
C     MODIFIED TO EXTRAPOLATE OUTSIDE KNOT RANGE
C 990 IF(X.LE.U(1)-2.0**IEPS*AMAX1(ABS(U(1)),ABS(U(N)))) GO TO 99
  990 J=1
      GO TO 7
C
C 991 IF(X.GE.U(N)+2.0**IEPS*AMAX1(ABS(U(1)),ABS(U(N)))) GO TO 99
  991 J=N-1
      GO TO 7
C  99 IFLG=0
C
C     TG01B=0.0
C     RETURN
      END
