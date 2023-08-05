// Copyright(c) gert.cuykens@gmail.com
#include <stdio.h>
#include <string.h>
#include <expat.h>
#include "db.c"
#include "page_db.c"

static void
startElement(void *userData, const XML_Char *name, const XML_Char **atts)
{
 PAGE *page = (PAGE*)userData;
 free(page->data);
 page->data = NULL;
}

static void
characterData(void *userData, const XML_Char *s, int l)
{
 char *data;
 PAGE *page = (PAGE *)userData;
 if (page->data==NULL)
 {
  if(data=malloc(l))
  {
   memcpy(data,s,l);
   page->data=data;
   page->dataSize=l;
  }else{printf(" <error>no memory</error>\n");}
 }
 else
 {
  if(data=realloc(data, l+page->dataSize))
  {
   memcpy(data+page->dataSize,s,l);
   page->data=data;
   page->dataSize+=l;
  }else{printf(" <error>no memory</error>\n");}
 }
}

static void
endElement(void *userData, const XML_Char *name)
{
 PAGE *page = (PAGE*)userData;
 if (strcmp("user",name)==0) page->user=page->data;
 else if (strcmp("password",name)==0) page->password=page->data;
 else if (strcmp("database",name)==0) page->database=page->data;
 else if (strcmp("sql",name)==0 && page->data!=NULL) page->add(page,page->data);
 else free(page->data);
 page->data = NULL;
}

static int
parse(char *buf)
{
 size_t i;
 char *line;
 PAGE page=init();
 XML_Parser parser = XML_ParserCreate(NULL);
 XML_SetUserData(parser, &page);
 XML_SetStartElementHandler(parser, startElement);
 XML_SetCharacterDataHandler(parser, characterData);
 XML_SetEndElementHandler(parser, endElement);
 if (XML_Parse(parser, buf, strlen(buf), 1) == XML_STATUS_ERROR) 
 {
  printf(" <error>%s at line %u</error>\n"
         " <input>%s</input>\n",
         XML_ErrorString(XML_GetErrorCode(parser)),
         XML_GetCurrentLineNumber(parser),buf);
  XML_ParserFree(parser);
  for(i=0;line=page.line[i];i++)free(page.line[i]);
  free(page.line);
  free(page.user);
  free(page.password);
  free(page.database);
  return 0;
 }
 XML_ParserFree(parser);
 db(page.user,page.password,page.database,page.line);
 for(i=0;line=page.line[i];i++)free(page.line[i]);
 free(page.line);
 free(page.user);
 free(page.password);
 free(page.database);
 return 1;
}

/************** test *****************
int
main(void)
{
 parse("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
       "<root>\n"
       " <user>www</user>\n"
       " <password></password>\n"
       " <database>www</database>\n"
       " <sql>SHOW DATABASES;</sql>\n"
       "</root>");
} 
*************************************/
