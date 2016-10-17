#include <iostream.h>
#include <stdio.h>

main() {
  float data[5];
  FILE *infile, *outfile;
  char outstring[80];
  infile = fopen("read_format.input","r");
  if (infile == NULL) {
    printf("Can't open read_format.input\n");
    return(0);
  }
  int j=0;
  while(!feof(infile)) { 
    fscanf(infile,"%f",&data[j]);
    j++;
  }
  for(int i=0; i<5; ++i) cout << i << " " << data[i] << endl; 
  outfile = fopen("read_format.output","w");
  sprintf(outstring,"The input numbers are:"
  "%5.1f %5.1f %5.2f\n", data[0],data[1],data[3]);
  fputs(outstring,outfile);
  fclose(infile);
  fclose(outfile);
}
