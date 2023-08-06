// Copyright(c) gert.cuykens@gmail.com
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mysql/mysql.h>

int 
db(char *user,char *password,char *database,char** query)
{
 unsigned int r,t,q;
 char *s;
 MYSQL mysql;
 MYSQL_RES *res;
 MYSQL_ROW row;
 MYSQL_FIELD *field;
 mysql_init(&mysql);
 if(!mysql_real_connect(&mysql,"localhost",user,password,database,0,NULL,0))
 {
  printf(" <error>%s</error>\n",mysql_error(&mysql));
  mysql_close(&mysql);
  return 0;
 }
 for(q=0;s=query[q];q++)
 {
  if(mysql_real_query(&mysql,s,(unsigned int)strlen(s)))
  {
   printf(" <error>%s</error>\n",mysql_error(&mysql));
   mysql_close(&mysql);
   return 0;
  }
  res=mysql_use_result(&mysql);
  for(r=0;row=mysql_fetch_row(res);r++)
  {
   printf(" <record index=\"%u\">\n",r);
   for (t=0;t<mysql_num_fields(res);t++) 
   {
    field = mysql_fetch_field_direct(res, t);
    printf("  <%s>%s</%s>\n",field->name,row[t],field->name);
   }
   printf(" </record>\n");
  }
  mysql_free_result(res);
 }
 mysql_close(&mysql);
 return 0;
}

/******** test ****************
int
main(void)
{
 char *query[2];
 query[0]="SHOW DATABASES;";
 query[1]="BAD SQL SYNTAX;";
 db("www","","www",query);
}
*******************************/
