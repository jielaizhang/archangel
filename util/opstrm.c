/********************************/
/*	opstrm	 valdes 8 31 82	*/
/*				*/
/*	Operate on an input	*/
/*	stream 			*/
/********************************/
#include	<stdio.h>
#include	<math.h>
#define		RMAX	100	/* maximum number of registers */
#define		CMDS	500	/* maximum number of commands */
#define		PI	3.141592654/* pi */

char   *help[] = {
    "Reverse Polish stream operator",
    "  usage:  opstrm operators constants",
    "",
    "  The argument list is repeated until the end of input and the stack",
    "  is cleared after each pass.  All output in each pass is put on one line.",
    "",
    "  operators: Pfile     The standard input is a program instead of data",
    "                       which is stored in file.opstrm .",
    "             Rfile     Substitute the commands in file.opstrm .  Programs",
    "                       can be nested though watch out for recursion.",
    "             r         Read value from standard input into x and push up",
    "                       stack (must be numerical of any format).",
    "             s         Skip next input value (may be alphabetic).",
    "             c         Copy input to output (may be alphabetic).",
    "             =         Write x to the standard output stream.",
    "             Sstring   Write string to standard output stream.",
    "             q         Quit (used to do calculation on argument list).",
    "             e         Enter (or copy) value.",
    "             pn        Put x value in storage location n (n = 0, 1, ..., 9).",
    "             gn        Get value from storage location n and put in x.",
    "             gc        Get value of line counter (starts with 1).",
    "             gl        Get log of line counter (gl = log(gc)).",
    "             d         Roll down stack (last x value is lost).",
    "             +         Add  x + y = x.",
    "             -         Subtract y - x = x.",
    "             x         Multiply  x * y = x.",
    "             /         Divide  y / x = x.",
    "             i         Invert x and y.",
    "             Fmax      Compare x and y and put the maximum in x and",
    "                       the minimum in y",
    "             Fabs      Absolute value of x.",
    "             Fmag      -2.5 * log(x) = x.",
    "             Flum      10**( -.4 * x) = x.",
    "             Fpow      y**x = x.",
    "             Fsq       x = Square x.",
    "             Fsqrt     x = Square root of x.",
    "             Flog      x = Base 10 logrithm of x.",
    "             Fdex      x = 10**x.",
    "             Fln       x = Natural logrithm of x.",
    "             Fexp      x = e**x.",
    "             Fcos      x = cosine of x (radians).",
    "             Fsin      x = sin of x (radians).",
    "             Fpolar    Take x and y and replace with radius and angle",
    "                       (radians) respectively.",
    "             Fpolar1   Take x and y and replace with radius and angle",
    "                       (radians between - pi / 2 and pi / 2) respectively.",
    "             Frec      Take x = radius and y = angle(radians) and replace",
    "                       with x and y, respectively.",
    "             Fpois     x = N y = lambda compute lambda**N exp( -lambda) / N!.",
    "             pi        3.141592654",
    "             fformat   Set output format (default g).",
    "             constant  If present constant will be used as operand.",
    0
};

char    cmds[CMDS][20], tmp[CMDS][20];
int     cflag = 0;

main (argc, argv)
int     argc;
char   *argv[];
{
    float   func3 (), func4 (), pois ();
    float   x[RMAX], z, store[10], value;
    int     i, j = -1, k, m, n, flag, steps;
    char    op[20], y[100], frmt[20], prgm[100];
    FILE * fin, *fout, *fopen ();

    if (argc > 1 && argv[1][0] == '^') {
	for (i = 0; help[i] != 0; i++)
	    printf ("%s\n", help[i]);
	exit (0);
    }

    flag = 0;
    steps = 0;
    if (argc == 1) {
	cflag = 1;
	steps = 2;
    }
    else
	for (i = 1; i < argc; i++, steps++)
	    switch (argv[i][0]) {
		case 'P': 
		    sprintf (prgm, "%s.opstrm", &argv[i][1]);
		    if ((fout = fopen (prgm, "w")) == NULL) {
			fprintf (stderr, "opstrm: Can't create %s\n", prgm);
			exit (0);
		    }
		    for (;;) {
			scanf ("%s", op);
			if (feof (stdin))
			    exit (0);
			strncpy (cmds[0], op, 20);
			fprintf (fout, "%s\n", op);
		    }
		case 'R': 
		    if (argv[i][0] == 'R')
			flag++;
		default: 
		    strncpy (cmds[steps], argv[i], 20);
	    }
    for (; (flag != 0) && (cflag == 0);) {
	for (i = 0; i < steps; i++)
	    strcpy (tmp[i], cmds[i]);
	for (i = 0, j = steps, steps = 0, flag = 0; i < j; i++, steps++) {
	    switch (tmp[i][0]) {
		case 'R': 
		    sprintf (prgm, "%s.opstrm", &tmp[i][1]);
		    if ((fin = fopen (prgm, "r")) == NULL) {
			fprintf (stderr, "opstrm: Can't find %s\n", prgm);
			exit (0);
		    }
		    for (;; steps++) {
			fscanf (fin, "%s", cmds[steps]);
			if (feof (fin))
			    break;
			if (cmds[steps][0] == 'R')
			    flag++;
		    }
		    fclose (fin);
		    steps--;
		    break;
		default: 
		    strcpy (cmds[steps], tmp[i]);
	    }
	}
    }

    srand (1);
    strcpy (frmt, "%g ");
    for (m = 1;; m++) {
	for (i = 0, j = -1; i < steps; i++) {
	    if (j > (RMAX - 1))
		goto reg;
	    if (cflag) {
		i = 0;
		scanf ("%s", cmds[i]);
		if (feof (stdin))
		    exit (0);
	    }
	    switch (cmds[i][0]) {
		case 'I': 
		    if (m != 1)
			++i;
		    break;
		case 'q': 
		    printf ("\n");
		    exit (0);
		case 'r': 
		    scanf ("%f", &x[++j]);
		    if (feof (stdin))
			exit (0);
		    break;
		case 'c': 
		    scanf ("%s", y);
		    if (feof (stdin))
			exit (0);
		    printf ("%s ", y);
		    break;
		case 'p': 
		    if (cmds[i][1] == 'i')
			x[++j] = PI;
		    else {
			sscanf (cmds[i], "p%d", &n);
			if ((n >= 0) && (n <= 9))
			    store[n] = x[j];
			else
			    goto stre;
		    }
		    break;
		case 'g': 
		    switch (cmds[i][1]) {
			case 'c': 
			    x[++j] = m;
			    break;
			case 'l': 
			    x[++j] = log10 ((double) m);
			    break;
			default: 
			    sscanf (cmds[i], "g%d", &n);
			    if ((n >= 0) && (n <= 9))
				x[++j] = store[n];
			    else
				goto stre;
		    }
		    break;
		case 'd': 
		    if (j > 0)
			j--;
		    else
			goto stack;
		    break;
		case '+': 
		    if (j >= 1) {
			x[j - 1] = x[j - 1] + x[j];
			j--;
		    }
		    else
			goto stack;
		    break;
		case '-': 
		    if (cmds[i][1] == 0) {
			if (j >= 1) {
			    x[j - 1] = x[j - 1] - x[j];
			    j--;
			}
			else
			    goto stack;
		    }
		    else
			sscanf (cmds[i], "%f", &x[++j]);
		    break;
            case '*':
		case 'x': 
		    if (j >= 1) {
			x[j - 1] = x[j - 1] * x[j];
			j--;
		    }
		    else
			goto stack;
		    break;
		case '/': 
		    if (x[j] == 0.)
			goto divide;
		    if (j >= 1) {
			x[j - 1] = x[j - 1] / x[j];
			j--;
		    }
		    else
			goto stack;
		    break;
		case 'i': 
		    if (j >= 1) {
			value = x[j - 1];
			x[j - 1] = x[j];
			x[j] = value;
		    }
		    else
			goto stack;
		    break;
		case 's': 
		    scanf ("%*s");
		    break;
		case 'e': 
		    x[j+1] = x[j];
		    j++;
		    break;
		case '=': 
		    if (j >= 0)
			printf (frmt, x[j]);
		    else
			goto stack;
		    break;
		case 'S': 
		    printf ("%s ", cmds[i] + 1);
		    break;
		case 'f': 
		    sprintf (frmt, "%%%s ", cmds[i] + 1);
		    break;
		case 'F': 
		    if (!strcmp (cmds[i], "Fmax")) {
			if (j >= 1) {
			    if (x[j] < x[j - 1]) {
				value = x[j];
				x[j] = x[j - 1];
				x[j - 1] = value;
			    }
			}
			else
			    goto stack;
		    }
		    if (!strcmp (cmds[i], "Fabs"))
			x[j] = fabs (x[j]);
		    if (!strcmp (cmds[i], "Fsq"))
			x[j] = x[j] * x[j];
		    if (!strcmp (cmds[i], "Fpow"))
			x[j] = pow (x[j - 1], x[j]);
		    if (!strcmp (cmds[i], "Fsqrt"))
			x[j] = sqrt (x[j]);
		    if (!strcmp (cmds[i], "Fln"))
			x[j] = log (x[j]);
		    if (!strcmp (cmds[i], "Fexp"))
			x[j] = exp (x[j]);
		    if (!strcmp (cmds[i], "Flog"))
			x[j] = log10 (x[j]);
		    if (!strcmp (cmds[i], "Fdex"))
			x[j] = pow (10., x[j]);
		    if (!strcmp (cmds[i], "Fmag"))
			x[j] = -2.5 * log10 (x[j]);
		    if (!strcmp (cmds[i], "Flum"))
			x[j] = pow (10., -.4 * x[j]);
		    if (!strcmp (cmds[i], "Fcos"))
			x[j] = cos (x[j]);
		    if (!strcmp (cmds[i], "Fsin"))
			x[j] = sin (x[j]);
		    if (!strcmp (cmds[i], "Frec")) {
			if (j >= 1) {
			    z = x[j] * sin (x[j - 1]);
			    x[j] = x[j] * cos (x[j - 1]);
			    x[j - 1] = z;
			}
			else
			    goto stack;
		    }
		    if (!strcmp (cmds[i], "Fpolar")) {
			if (j >= 1) {
			    z = sqrt (x[j] * x[j] + x[j - 1] * x[j - 1]);
			    x[j - 1] = atan2 (x[j - 1], x[j]);
			    x[j] = z;
			}
			else
			    goto stack;
		    }
		    if (!strcmp (cmds[i], "Fpolar1")) {
			if (j >= 1) {
			    z = sqrt (x[j] * x[j] + x[j - 1] * x[j - 1]);
			    x[j - 1] = atan2 (x[j - 1], x[j]);
			    if (x[j - 1] < -PI / 2.)
				x[j - 1] += PI;
			    if (x[j - 1] > PI / 2.)
				x[j - 1] -= PI;
			    x[j] = z;
			}
			else
			    goto stack;
		    }
		    if (!strcmp (cmds[i], "Fpois"))
			x[j] = pois (x + j - 1);
		    break;
		default: 
		    sscanf (cmds[i], "%f", &x[++j]);
	    }
	}
	printf ("\n");
    }
reg: 
    fprintf (stderr, "opstrm: register overflow\n");
    exit (0);
stack: 
    fprintf (stderr, "opstrm: stack empty\n");
    exit (0);
divide: 
    fprintf (stderr, "opstrm: divide by zero\n");
    exit (0);
stre: 
    fprintf (stderr, "opstrm: invalid store - %s\n", cmds[i]);
    exit (0);
}

float   pois (x)
float  *x;
{
    int     i, N;
    double  y, lambda;

    N = x[1];
    lambda = x[0];
    for (y = 1, i = 2; i <= N; i++)
	y *= i;
    return (pow (lambda, x[1]) * exp (-lambda) / y);
}
