// Copyright(c) gert.cuykens@gmail.com
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct SELF
{
 size_t length;
 char **line;
 void (*add)(struct SELF*,char*);
 char *location;
 char *user;
 char *password;
 char *database;
 char *name;
 char *data;
 int dataSize;
}PAGE;

static void 
add(PAGE *this, char *line)
{
 char **temp=this->line;
 if (temp = realloc(temp,(sizeof *temp) * (this->length + 2))) 
 {
  temp[this->length] = line;
  temp[this->length+1] = NULL;
  this->line = temp;
  this->length += 1;
 }else printf(" <error>no memory</error>\n");
}

PAGE
init(void)
{
 char **line;
 if(line = malloc(sizeof *line))
 {
  line[0] = NULL;
  PAGE new = {0,line,&add,NULL,NULL,NULL,NULL,NULL,NULL,0};
  return new;
 }
 printf(" <error>no memory</error>\n");
 exit(EXIT_FAILURE);
}

/********************* test ******************************
int
main(void)
{
 size_t i;
 char *line;
 PAGE page = init();
 for(i=0;line=page.line[i];i++) printf("%s\n",line);
 page.add(&page,"hello");
 page.add(&page,"world");
 page.location="test";
 for(i=0;line=page.line[i];i++) printf("%s\n",line);
 free(page.line);
 printf("%s\n",page.location);
}
**********************************************************/
