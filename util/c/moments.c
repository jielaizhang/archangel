#include <time.h>
#include <iostream.h>
#include <fstream.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main(int argc, char **argv) {

  float flux[1000];
  float x[1000];
  float y[1000];
  int npts=1;

  ifstream data;
  data.open(argv[1]);
  while (data >> x[npts] >> y[npts] >> flux[npts]) {
    npts++;
  }
  npts--;

  int j;
  float xc=0;
  float yc=0;
  float totf=0.;

  for (j=1;j<=npts;j++) {
    xc=xc+x[j]*flux[j];
    yc=yc+y[j]*flux[j];
    totf=totf+flux[j];
  }
  xc=xc/totf;
  yc=yc/totf;

  for (j=1;j<=npts;j++) {
    x[j]=x[j]-xc;
    y[j]=y[j]-yc;
  }

  float mxx=0.;
  float myy=0.;
  float mxy=0.;
  float e,pa;
  totf=0;

  for (j=1;j<=npts;j++) {
    mxx=mxx+x[j]*x[j]*flux[j];
    myy=myy+y[j]*y[j]*flux[j];
    mxy=mxy+x[j]*y[j]*flux[j];
    totf=totf+flux[j];
  }

  mxx=mxx/totf;
  myy=myy/totf;
  mxy=mxy/totf;

  e=sqrt((pow((mxx-myy),2)+pow((2*mxy),2)))/(mxx+myy);
  pa=0.5*atan(2*mxy/(mxx-myy));
  e=1.-e;

  float a,b;
  float pi=3.1415926536;

  a=2.*sqrt(npts/(pi*e));
  b=a*e;
  pa=180.*pa/pi;
  cout << "mark " << xc << " " << yc << " " << " el blue ";
  cout << a << " " << b << " " << pa-90. << endl;

  return(0);
}

