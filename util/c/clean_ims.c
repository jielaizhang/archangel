#include <time.h>
#include <iostream.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "/usr/local/cfitsio/fitsio.h"

void read_data(char filename[], long naxes[], float data[1024][1024]);
void write_data(char filename[], long naxes[], float data[1024][1024]);
void printerror(int status);

main(int argc, char **argv) {

  time_t sec1;
  sec1=time(NULL);

  long naxes[2];
  float data[1024][1024];

  cout << "read " << endl;
  if (argc > 1) {
    read_data(argv[1], naxes, data);
  }
  cout << "done" << endl;

  int nx=naxes[0];
  int ny=naxes[1];

  float images[100][5];
  FILE *infile;
  infile = fopen("ims_clean.dat","r");
  if (infile == NULL) {
    printf("Can't open ims_clean file\n");
    return(0);
  }
  int nct=-1;
  while(!feof(infile)) { 
    nct++;
    for(int n=0; n<5; ++n) fscanf(infile,"%f",&images[nct][n]);
  }
  fclose(infile);

  float xmin=1.e10;
  int nmax=0;

  for(int n=0; n<=nct; ++n) {
    float x=nx/2.-images[n][0];
    float y=ny/2.-images[n][1];
    float r=sqrt(x*x+y*y);
    if(r <= xmin) {
      xmin=r;
      nmax=n;
    }
  }

  float pi=3.1415926536;

  for(int j=0; j<=ny; ++j) {
    for (int i=0; i<=nx; ++i) {
      for(int n=0; n<=nct; ++n) {
        if(n != nmax) {
          float x=i-images[n][0];
          float y=j-images[n][1];
          float fct=(1.-images[n][3])+1.;
          float a=fct*(sqrt(images[n][2]/(pi*(1.-images[n][3]))));
          float b=(a*(1.-images[n][3]));
          a=a*a;
          b=b*b;
          float d=-images[n][4]*pi/180.;
          float t;
          if(x != 0) {
            t=atan(y/x);
          } else {
            t=pi/2.;
          }
          float c1=b*cos(t)*cos(t)+a*sin(t)*sin(t);
          float c2=(a-b)*2.*sin(t)*cos(t);
          float c3=b*sin(t)*sin(t)+a*cos(t)*cos(t);
          float c4=a*b;
          float rr=sqrt(c4/(c1*cos(d)*cos(d)+c2*sin(d)*cos(d)+c3*sin(d)*sin(d)));
          if(sqrt(x*x+y*y) <= rr) data[i][j]=0.;
        }
      }
    }
  }

  cout << "write" << endl;
  write_data("clean.fits", naxes, data);
  cout << "done" << endl;

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

    float datamin, datamax, nullval, buffer[1024];

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
      if ( fits_read_img(fptr, TFLOAT, fpixel, nbuffer, &nullval,
                  buffer, &anynull, &status) )
           printerror( status );

      for (i = 0; i < nbuffer; i++) {
        data[i][j]=buffer[i];

      }
      j++;
      npixels -= nbuffer;    /* increment remaining number of pixels */
      fpixel  += nbuffer;    /* next pixel to be read in image */
    }

    if ( fits_close_file(fptr, &status) )
         printerror( status );

}

void write_data( char filename[], long naxes[], float data[1024][1024])

    /******************************************************/
    /* Create a FITS primary array containing a 2-D image */
    /******************************************************/
{
    fitsfile *fptr;       /* pointer to the FITS file, defined in fitsio.h */
    int status, ii, jj;
    long  fpixel, nelements, exposure, nbuffer;
    long  i=0;
    long  j=0;
    float *array[1024];

    /* initialize FITS image parameters */
    int bitpix   =  -32; 
    long naxis    =   2;  /* 2-dimensional image                            */

    /* allocate memory for the whole image */
    array[0] = (float *)malloc( naxes[0] * naxes[1]
                                        * sizeof( float ) );

    /* initialize pointers to the start of each row of the image */
    for( ii=1; ii<naxes[1]; ii++ )
      array[ii] = array[ii-1] + naxes[0];

    remove(filename);               /* Delete old file if it already exists */

    status = 0;         /* initialize status before calling fitsio routines */

    if (fits_create_file(&fptr, filename, &status)) /* create new FITS file */
        printerror( status );           /* call printerror if error occurs */

    if ( fits_create_img(fptr,  bitpix, naxis, naxes, &status) )
         printerror( status );

    for (jj = 0; jj < naxes[1]; jj++)
    {   for (ii = 0; ii < naxes[0]; ii++)
        {
            array[jj][ii] = data[ii][jj];
        }
    }


    fpixel = 1;                               /* first pixel to write      */
    nelements = naxes[0] * naxes[1];          /* number of pixels to write */

    /* write the array of unsigned integers to the FITS file */
    if ( fits_write_img(fptr, TFLOAT, fpixel, nelements, array[0], &status) )
       printerror( status );

    free( array[0] );  /* free previously allocated memory */

    /* write another optional keyword to the header */
    /* Note that the ADDRESS of the value is passed in the routine */
    /* exposure = 1500.; */
    /* if ( fits_update_key(fptr, TLONG, "EXPOSURE", &exposure, */
    /*      "Total Exposure Time", &status) ) */
    /*      printerror( status ); */

    if ( fits_close_file(fptr, &status) )                /* close the file */
         printerror( status );

    return;
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

