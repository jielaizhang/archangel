#include <time.h>
#include <iostream.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "/usr/local/cfitsio/fitsio.h"

void read_data(char filename[], long naxes[], float data[4096][4096]);
void write_data(char filename[], long naxes[], float data[4096][4096]);
void printerror(int status);

main(int argc, char **argv) {

  time_t sec1;
  sec1=time(NULL);

  long naxes[2];
  float data[4096][4096];

  cout << "read " << endl;
  if (argc > 1) {
    read_data(argv[1], naxes, data);
  }
  cout << "done" << endl;

  int nx=naxes[0];
  int ny=naxes[1];

  cout << "write" << endl;
  write_data("junk1.fits", naxes, data);
  cout << "done" << endl;

  time_t sec5;
  sec5=time(NULL);
  // cout << "end " << sec5-sec1 << endl;
  return(0);
}

void read_data(char filename[], long naxes[], float data[4096][4096]) {

    fitsfile *fptr;       /* pointer to the FITS file, defined in fitsio.h */
    int status,  nfound, anynull;
    long fpixel, nbuffer, npixels;
    long i=0;
    long j=0;

    float datamin, datamax, nullval, buffer[4096];

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

void write_data( char filename[], long naxes[], float data[4096][4096])

    /******************************************************/
    /* Create a FITS primary array containing a 2-D image */
    /******************************************************/
{
    fitsfile *fptr;       /* pointer to the FITS file, defined in fitsio.h */
    int status, ii, jj;
    long  fpixel, nelements, exposure, nbuffer;
    long  i=0;
    long  j=0;
    float *array[4096];

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

