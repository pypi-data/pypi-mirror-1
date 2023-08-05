// Copyright (c) gert.cuykens@gmail.com
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <regex.h>
#include "page.c"

void 
regex(char *buffer,char *pattern,PAGE *page)
{
 size_t l,so;
 int errcode;
 char *errbuf,*line;
 int *coor;
 regex_t re;
 regmatch_t rm;
 errcode=regcomp(&re, pattern, REG_EXTENDED);
 so=0;
 if(errcode==0)errcode=regexec(&re, &buffer[0], 1, &rm, 0);
 while(errcode==0)
 {
  if(coor=malloc(2*sizeof coor))
  {
   coor[0]=so+rm.rm_so;
   coor[1]=so+rm.rm_eo;
   page->put(page,coor);
  }else{printf("no memory\n");break;}
  if(line=malloc(rm.rm_eo-rm.rm_so))
  {
   memcpy(line, buffer+so+rm.rm_so, rm.rm_eo-rm.rm_so);
   line[rm.rm_so, rm.rm_eo-rm.rm_so]=(int)NULL;
   page->add(page,line);
  }else{printf("no memory\n");break;}
  so=so+rm.rm_eo+1;
  errcode=regexec(&re, buffer+so, 1, &rm, REG_NOTBOL);
 }
 l=regerror(errcode,&re,errbuf,0);
 if(errbuf=malloc(l))
 {
  regerror(errcode,&re,errbuf,l);
  printf("%s\n",errbuf,l);
  free(errbuf);
 }else printf("no memory");
 regfree(&re); 
}

int
main(void)
{
 //find csv delimiter ,(?=(?:[^"]*"[^"]*")*(?![^"]*")) does not work with posix regex
 size_t i;
 char *line;
 PAGE page=init();

 regex("222test222,222test222,222test222,222test222,222test222,222test222"
      ,"test"
      ,&page);

 for(i=0;line=page.line[i];i++)
 {
  printf("%s\n",page.line[i]);
  printf("%i\n",page.coor[i][0]);
  printf("%i\n",page.coor[i][1]);
  free(page.line[i]);
  free(page.coor[i]);
 }
 free(page.line);
 free(page.coor);
}
