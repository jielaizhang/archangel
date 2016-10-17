/********************************/
/*	fltstrm	 valdes 8 31 82	*/
/*				*/
/*	Filter and input stream	*/
/********************************/
#include	<stdio.h>

char   *help[] = {
    "Filter a periodic input stream.",
    "  usage: fltstrm options",
    "  Options:  r min max - range of values passed.  Input must be numeric.",
    "            c - copy input to output unchanged if all test are passed.",
    "                May be string.",
    "            s - skip input no output.  May be string.",
    "  Input: a stream .",
    "  Output: filtered stream",
    "  The argument list is repeatedly cycled and any sequence of values",
    "  which does not pass the filter criterion are not output.",
    0
};

main (argc, argv)
int     argc;
char   *argv[];
{
    int     i, flag;
    char    in[132];
    char    out[1000];
    float   min, max, value;

    if ((argc < 2) || (argv[1][0] == '^')) {
	for (i = 0; help[i] != 0; i++)
	    fprintf (stderr, "%s\n", help[i]);
	exit (0);
    }

    for (;;) {
	out[0] = '\0';
	flag = 1;
	for (i = 1; i < argc; ++i) {
	    switch (argv[i][0]) {
		case 'r': 
		    sscanf (argv[++i], "%f", &min);
		    sscanf (argv[++i], "%f", &max);
		    scanf ("%s", in);
		    if (feof (stdin))
			break;
		    sscanf (in, "%f", &value);
		    if ((value >= min) && (value <= max)) {
			strcat (out, in);
			strcat (out, " ");
		    }
		    else
			flag = 0;
		    break;
		case 'c': 
		    scanf ("%s", in);
		    if (feof (stdin))
			break;
		    strcat (out, in);
		    strcat (out, " ");
		    break;
		case 's': 
		    scanf ("%*s");
		    break;
		default: 
		    fprintf (stderr, "fltstrm: error in argument list\n");
		    exit (0);
	    }
	    if (feof (stdin))
		break;
	}
	if (flag)
	    printf ("%s\n", out);
	if (feof (stdin))
	    break;
    }
}
