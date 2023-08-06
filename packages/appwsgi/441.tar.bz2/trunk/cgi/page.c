// Copyright(c) gert.cuykens@gmail.com
#include <stdio.h>
#include <stdlib.h>

typedef struct SELF
{
 size_t lengthL;
 size_t lengthC;
 char   **line;
 int    **coor;
 void   (*add)(struct SELF*,char*);
 void   (*put)(struct SELF*,int*);
}PAGE;

static void 
add(PAGE *this, char *line)
{
 char **temp=this->line;
 if (temp = realloc(temp,(sizeof *temp) * (this->lengthL+2))) 
 {
  temp[this->lengthL] = line;
  temp[this->lengthL+1] = NULL;
  this->line = temp;
  this->lengthL += 1;
 }else printf(" <error>no memory</error>\n");
}

static void 
put(PAGE *this, int *coor)
{
 int **temp=this->coor;
 if (temp = realloc(temp,(sizeof *temp) * (this->lengthC+2))) 
 {
  temp[this->lengthC] = coor;
  temp[this->lengthC+1] = NULL;
  this->coor = temp;
  this->lengthC += 1;
 }else printf(" <error>no memory</error>\n");
}

PAGE
init(void)
{
 char **line;
 int  **coor;
 if((line=malloc(sizeof *line))&&(coor=malloc(sizeof *coor)))
 {
  line[0] = NULL;
  PAGE new = {0,0,line,coor,&add,&put};
  return new;
 }
 printf(" <error>no memory</error>\n");
 exit(EXIT_FAILURE);
}

/************************** test **********************************
int
main(void)
{
 int i;
 int *line;
 int c1[]={0,1};
 int c2[]={1,2};
 PAGE page = init();
 for(i=0;line=page.line[i];i++) printf("%i,%i\n",line[0],line[1]);
 page.put(&page,c1);
 page.put(&page,c2);
 for(i=0;line=page.line[i];i++) printf("%i,%i\n",line[0],line[1]);
 free(page.line);
}
************************** test **********************************/
