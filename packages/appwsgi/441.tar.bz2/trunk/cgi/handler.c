// Copyright(c) gert.cuykens@gmail.com
#include <stdio.h>
#include <stdlib.h>
#include "xml.c"

int 
main(void)
{
 printf("Content-Type: text/xml; charset=utf-8"
        "\r\n"
        "\r\n"
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<root>\n");

 char *x="";
 char *s=getenv("CONTENT_LENGTH");
 long l;
 if (s != NULL)
 {
  sscanf(s,"%ld",&l);
  if(x = malloc(l+1))
  {
   fgets(x, l+1, stdin);
   parse(x);
   free(x);
  }else printf(" <error>no memory</error>\n");
 }
 printf("</root>\n");
 return 0;
}
