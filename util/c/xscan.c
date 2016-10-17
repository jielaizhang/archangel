/* this is c++ version of gasp_images */

#include <time.h>
#include <iostream.h>
#include <iomanip.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "/usr/local/cfitsio/fitsio.h"

void read_data(char filename[], long naxes[], float data[1024][1024]);
void printerror(int status);

int main(int argc, char **argv) {

  time_t sec1;
  sec1=time(NULL);

  long naxes[2];
  float data[1024][1024];

  if (argc < 2) {
    cout << "Usage: -f/-m file sky threshold minpix" << endl;
    exit(0);
  }

  read_data(argv[2], naxes, data);

  float flux[20000][4];
  int nx=naxes[0];
  int ny=naxes[1];
  int i,j,l;
  int next=1;
  int ntot=0;
  float sky=atof(argv[3]);
  float thres=atof(argv[4]);
  int minpix=atoi(argv[5]);

  time_t sec2;
  sec2=time(NULL);
  // cout << "start " << sec2-sec1 << endl;

  // flux[][0]=intensity
  // flux[][1]/[2] = x and y
  // flux[][3] = object number

  for (j=1;j<=ny;j++) {
    for (i=1;i<=nx;i++) {

      if((data[i][j]-sky)>=thres) {
        ntot++;
        int id=0;
        float r;
        flux[ntot][0]=data[i][j]-sky;
        flux[ntot][1]=i;
        flux[ntot][2]=j;
        for (l=1;l<ntot;l++) {
          r=sqrt(pow((flux[l][1]-flux[ntot][1]),2)+pow((flux[l][2]-flux[ntot][2]),2));
          if(r<1.1) {
            flux[ntot][3]=flux[l][3];
            id=1;
          }
        }
        if(id==0) {
          flux[ntot][3]=next;
          next++;
        }
      }
    }
  }

  time_t sec3;
  sec3=time(NULL);
  // cout << "join " << sec3-sec1 << endl;
  // join

  for (l=1;l<=ntot;l++) {
    for (i=1;i<=l;i++) {
      float r;
      int id;
      r=sqrt(pow((flux[l][1]-flux[i][1]),2)+pow((flux[l][2]-flux[i][2]),2));
      // cout << flux[l][3] << " " << flux[i][3] << endl;
      if((r<1.1)&&(flux[l][3]!=flux[i][3])) {
        id=flux[i][3];
        for (j=1;j<=ntot;j++) {
          if(flux[j][3]==id) 
            flux[j][3]=flux[l][3];
        }
      }
    }
  }

  time_t sec4;
  sec4=time(NULL);
  // cout << "calculate " << sec4-sec1 << endl;
 
  for (l=1;l<=next;l++) {

    int n=0;
    float xc=0;
    float yc=0;
    float totf=0.;

    for (j=1;j<=ntot;j++) {
      if(flux[j][3]==l) {
        if(argv[1][1] == 'p') {
          cout << "mark " << flux[j][1] << " ";
          cout << flux[j][2] << " dot #" << l << endl;
        }
        xc=xc+flux[j][1]*flux[j][0];
        yc=yc+flux[j][2]*flux[j][0];
        totf=totf+flux[j][0];
        n++;
      }
    }
    if(n>=minpix) {
      xc=xc/totf;
      yc=yc/totf;

      for (j=1;j<=ntot;j++) {
        if(flux[j][3]==l) {
          flux[j][1]=flux[j][1]-xc;
          flux[j][2]=flux[j][2]-yc;
        }
      }

      float s1=0.;
      float s2=0.;
      float s3=0.;
      float s4=0.;
      float s5=0.;
      float s6=0.;

      for (j=1;j<=ntot;j++) {
        if(flux[j][3]==l) {
          s1=s1+flux[j][0]*flux[j][1];
          s2=s2+flux[j][0]*flux[j][2];
          s3=s3+flux[j][0]*flux[j][1]*flux[j][1];
          s4=s4+flux[j][0]*flux[j][2]*flux[j][2];
          s5=s5+flux[j][0]*flux[j][1]*flux[j][2];
          s6=s6+flux[j][0];
        }
      }

      float xx,yy,xy,rr,e,pa;

      xx=(s3-(s1*s1)/s6)/s6;
      yy=(s4-(s2*s2)/s6)/s6;
      xy=(s5-(s1*s2)/s6)/s6;
      rr=xx+yy;
      e=xx-yy;
      e=sqrt(e*e+4.*xy*xy)/rr;
      pa=atan(xy/(0.5*rr*(1.+e)-yy));

      float a,b;
      float pi=3.1415926536;

      e=1.-e;
      a=2.*sqrt(n/(pi*e));
      b=a*e;
      pa=180.*pa/pi;

      switch (argv[1][1]) {
        case 'm':
          cout << "mark " << xc << " " << yc << " " << " el blue ";
          cout << a << " " << b << " " << pa << endl;
          break;
        case 'f':
          cout.setf(ios::fixed, ios::floatfield);
          cout.width(10);
          cout.precision(2);
          cout << xc;
          cout.width(10);
          cout.precision(2);
          cout << yc;
          cout.width(10);
          cout.precision(0);
          // cout << pi*a*b/4.;
          cout << n;
          cout.width(10);
          cout.precision(3);
          cout << 1.-b/a;
          cout.width(10);
          cout.precision(1);
          cout << pa << endl;
          break;
      }

    }
  }
  time_t sec5;
  sec5=time(NULL);
  // cout << "end " << sec5-sec1 << endl;
  return(0);
}

void read_data(char filename[], long naxes[], float data[1024][1024]) {

    fitsfile *fptr;       /* pointer to the FITS file, defined in fitsio.h */
    int status,  nfound, anynull;
    long fpixel, nbuffer, npixels;
    long i=0;
    long j=0;

#define buffsize 1024
    float datamin, datamax, nullval, buffer[buffsize];

    status = 0;

    if ( fits_open_file(&fptr, filename, READONLY, &status) )
         printerror( status );

    /* read the NAXIS1 and NAXIS2 keyword to get image size */
    /* naxes[0] will be nx, and naxes[1] will be ny */

    if ( fits_read_keys_lng(fptr, "NAXIS", 1, 2, naxes, &nfound, &status) )
         printerror( status );

    npixels  = naxes[0] * naxes[1];         /* number of pixels in the image */

    fpixel   = 1;
    nullval  = 0;                /* don't check for null values in the image */
    datamin  = 1.0E30;
    datamax  = -1.0E30;

    nbuffer = naxes[0];
    while (npixels > 0)
    {
      j++;
      if ( fits_read_img(fptr, TFLOAT, fpixel, nbuffer, &nullval,
                  buffer, &anynull, &status) )
           printerror( status );

      for (i = 0; i < nbuffer; i++) {
        data[i+1][j]=buffer[i];

      }
      npixels -= nbuffer;    /* increment remaining number of pixels */
      fpixel  += nbuffer;    /* next pixel to be read in image */
    }

    if ( fits_close_file(fptr, &status) )
         printerror( status );

}

void printerror(int status) {

    /*****************************************************/
    /* Print out cfitsio error messages and exit program */
    /*****************************************************/


    if (status)
    {
       fits_report_error(stderr, status); /* print error report */

       exit( status );    /* terminate the program, returning error status */
    }
    return;
}

