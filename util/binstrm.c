/****************************************/
/*	binstrm		valdes 8 31 82	*/
/*					*/
/*	statistics of input stream	*/
/****************************************/
#include	<stdio.h>
#include	<math.h>
#define		BINS	101

char   *help[] = {
    "Statistics of input stream of x, (x, y), or (x, y, z)",
    "  usage: binstrm [h] [t] [c] [a] [s] [r] [xmin xmax #xbins [ymin ymax #ybins] ]",
    "  Options:         h   Print header",
    "                   t   Print total",
    "                   a   Print average",
    "                   c   Print count",
    "                   s   Print standard deviation",
    "                   r   Print range",
    "                       With no arguments an input stream of x values",
    "                       is analyzed.",
    "    xmin xmax #xbins   Analyze y in a stream of x, y values in #xbins",
    "                       between xmin and xmax.",
    "    ymin ymax #ybins   Analyze z in a stream of x, y, z values in #xbins",
    "                       between xmin and xmax and in #ybins between ymin",
    "                       and ymax.",
    0
};

main (argc, argv)
short   argc;
char   *argv[];
{
    static float   xbin[BINS], ybin[BINS], count[BINS][BINS], sum[BINS][BINS], sum2[BINS][BINS];
    int     i, j, k, l, m, xbins, ybins;
    float   x, xmin, xmax, dx, y, ymin, ymax, dy, z;
    static float   zmin[BINS][BINS], zmax[BINS][BINS];
    char    hflag, tflag, aflag, sflag, cflag, rflag;

    if (argc > 1 && argv[1][0] == '^') {
	for (i = 0; help[i] != 0; i++)
	    fprintf (stderr, "%s\n", help[i]);
	exit (0);
    }

    hflag = aflag = cflag = rflag = sflag = 0;
    xbins = ybins = 1;
    for (i = 1, m = 0; i < argc; i++)
	switch (argv[i][0]) {
	    case 'h': 
		hflag = 1;
		break;
	    case 't': 
		tflag = 1;
		break;
	    case 'a': 
		aflag = 1;
		break;
	    case 'c': 
		cflag = 1;
		break;
	    case 's': 
		sflag = 1;
		break;
	    case 'r': 
		rflag = 1;
		break;
	    default: 
		if (m == 0) {
		    sscanf (argv[i], "%f", &xmin);
		    sscanf (argv[++i], "%f", &xmax);
		    sscanf (argv[++i], "%d", &xbins);
		    if (xbins >= BINS)
			xbins = BINS - 1;
		    dx = (xmax - xmin) / xbins;
		    for (j = 0; j <= xbins; j++)
			xbin[j] = (j - 1) * dx + xmin;
		}
		if (m == 1) {
		    sscanf (argv[i], "%f", &ymin);
		    sscanf (argv[++i], "%f", &ymax);
		    sscanf (argv[++i], "%d", &ybins);
		    if (ybins >= BINS)
			ybins = BINS - 1;
		    dy = (ymax - ymin) / ybins;
		    for (j = 0; j <= ybins; j++)
			ybin[j] = (j - 1) * dy + ymin;
		}
		m++;
	}

    for (i = 0; i <= xbins; i++)
	for (j = 0; j <= ybins; j++) {
	    count[i][j] = 0.;
	    sum[i][j] = 0.;
	    sum2[i][j] = 0.;
	    zmin[i][j] = 1e30;
	    zmax[i][j] = -1e30;
	}

    for (i = 1, j = 1;;) {
	switch (m) {
	    case 1: 
		scanf ("%f", &x);
		if (feof (stdin))
		    break;
		if ((x < xbin[0]) || (x >= (xbin[xbins] + dx)))
		    x = xbin[0];
		for (i = 0; (x >= xbin[i + 1]) && (i < xbins); i++);
		break;
	    case 2: 
		scanf ("%f", &x);
		if (feof (stdin))
		    break;
		if ((x < xbin[0]) || (x >= (xbin[xbins] + dx)))
		    x = xbin[0];
		for (i = 0; (x >= xbin[i + 1]) && (i < xbins); i++);
		scanf ("%f", &y);
		if (feof (stdin))
		    break;
		if ((y < ybin[0]) || (y >= (ybin[ybins] + dy)))
		    y = ybin[0];
		for (j = 0; (y >= ybin[j + 1]) && (j < ybins); j++);
		break;
	}
	scanf ("%f", &z);
	if (feof (stdin))
	    break;
	count[i][j] += 1;
	sum[i][j] += z;
	sum2[i][j] += z * z;
	if (z < zmin[i][j])
	    zmin[i][j] = z;
	if (z > zmax[i][j])
	    zmax[i][j] = z;
    }

    if (hflag) {
	if (m > 0)
	    printf ("           X          ");
	if (m > 1)
	    printf ("           Y          ");
	if (cflag)
	    printf ("      Count");
	if (tflag)
	    printf ("        Sum");
	if (aflag)
	    printf ("    Average");
	if (sflag)
	    printf ("    Std Dev");
	if (rflag)
	    printf ("    Minimum");
	if (rflag)
	    printf ("    Maximum");
	printf ("\n");
    }
 /* print statistics */
    for (i = 1; i <= xbins; i++)
	for (j = 1; j <= ybins; j++) {
	    if ((count[i][j] == 0) && (cflag == 0))
		continue;
	    if (m > 0)
		printf (" %10g %10g", xbin[i], xbin[i] + dx);
	    if (m > 1)
		printf (" %10g %10g", ybin[j], ybin[j] + dy);
	    if (cflag)
		printf (" %10.0f", count[i][j]);
	    if (tflag)
		printf (" %10g", sum[i][j]);
	    if (aflag)
		if (count[i][j] > 0)
		    printf (" %10g", sum[i][j] / count[i][j]);
		else
		    printf (" %10g", 0.);
	    if (sflag)
		if (count[i][j] > 1)
		    printf (" %10g", sqrt ((count[i][j] * sum2[i][j] -
				    sum[i][j] * sum[i][j]) / (count[i][j] * (count[i][j] - 1))));
		else
		    printf ("          0");
	    if (rflag)
		printf (" %10g %10g", zmin[i][j], zmax[i][j]);
	    printf ("\n");
	}
}
