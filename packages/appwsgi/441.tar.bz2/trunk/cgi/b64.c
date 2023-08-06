/*  
**  Modified for Gcc
**  http://www.sendmail.org/~ca/email/prgs/ed64.c
**  Simple base64 encoder/decoder
**  $Id: ed64.c,v 1.2 2000/06/11 17:22:23 ca Exp $
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define OK	(0)
#define FAIL	(-1)
#define BUFOVER	(-2)

static int verbose = 0;

char *encode_table;
char *decode_table;

#define CHAR64(c)  (((c) < 0 || (c) > 127) ? -1 : index_64[(c)])

static char basis_64[] =
   "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/???????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????";

static char index_64[128] = {
    -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1,
    -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1,
    -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,62, -1,-1,-1,63,
    52,53,54,55, 56,57,58,59, 60,61,-1,-1, -1,-1,-1,-1,
    -1, 0, 1, 2,  3, 4, 5, 6,  7, 8, 9,10, 11,12,13,14,
    15,16,17,18, 19,20,21,22, 23,24,25,-1, -1,-1,-1,-1,
    -1,26,27,28, 29,30,31,32, 33,34,35,36, 37,38,39,40,
    41,42,43,44, 45,46,47,48, 49,50,51,-1, -1,-1,-1,-1
};


int encode64(const char *_in, unsigned inlen,
		  char *_out, unsigned outmax, unsigned *outlen)
{
    const unsigned char *in = (const unsigned char *)_in;
    unsigned char *out = (unsigned char *)_out;
    unsigned char oval;
    char *blah;
    unsigned olen;

    /* Will it fit? */
    olen = (inlen + 2) / 3 * 4;
    if (outlen)
      *outlen = olen;
    if (outmax < olen)
      return BUFOVER;

    /* Do the work... */
    blah=(char *) out;
    while (inlen >= 3) {
      /* user provided max buffer size; make sure we don't go over it */
        *out++ = basis_64[in[0] >> 2];
        *out++ = basis_64[((in[0] << 4) & 0x30) | (in[1] >> 4)];
        *out++ = basis_64[((in[1] << 2) & 0x3c) | (in[2] >> 6)];
        *out++ = basis_64[in[2] & 0x3f];
        in += 3;
        inlen -= 3;
    }
    if (inlen > 0) {
      /* user provided max buffer size; make sure we don't go over it */
        *out++ = basis_64[in[0] >> 2];
        oval = (in[0] << 4) & 0x30;
        if (inlen > 1) oval |= in[1] >> 4;
        *out++ = basis_64[oval];
        *out++ = (inlen < 2) ? '=' : basis_64[(in[1] << 2) & 0x3c];
        *out++ = '=';
    }

    if (olen < outmax)
      *out = '\0';
    
    return OK;
}


int decode64(const char *in, unsigned inlen,
		  char *out, unsigned *outlen)
{
    unsigned len = 0,lup;
    int c1, c2, c3, c4;

    /* check parameters */
    if (out==NULL) return FAIL;

    /* xxx these necessary? */
    if (in[0] == '+' && in[1] == ' ') in += 2;
    if (*in == '\r') return FAIL;

    for (lup=0;lup<inlen/4;lup++)
    {
        c1 = in[0];
        if (CHAR64(c1) == -1) return FAIL;
        c2 = in[1];
        if (CHAR64(c2) == -1) return FAIL;
        c3 = in[2];
        if (c3 != '=' && CHAR64(c3) == -1) return FAIL; 
        c4 = in[3];
        if (c4 != '=' && CHAR64(c4) == -1) return FAIL;
        in += 4;
        *out++ = (CHAR64(c1) << 2) | (CHAR64(c2) >> 4);
        ++len;
        if (c3 != '=') {
            *out++ = ((CHAR64(c2) << 4) & 0xf0) | (CHAR64(c3) >> 2);
            ++len;
            if (c4 != '=') {
                *out++ = ((CHAR64(c3) << 6) & 0xc0) | CHAR64(c4);
                ++len;
            }
        }
    }

    *out=0; /* terminate string */
    *outlen=len;
    return OK;
}

void
printstr(char *s, int len)
{
 char c;
 int i;

 for (i = 0; i < len; i++) {
   c = s[i];
   if (c == '\\') {
     putchar(c); putchar(c);
   }
   else if (isascii(c) && isprint(c))
     putchar(c);
   else
     printf("\\%03o", c);
 }
}

int ed(int e, char *s, char *prg)
{
 char *r;
 int res,enc;
 int inlen, outlen, outmax;

 inlen = strlen(s);
 outmax = inlen * 2;
 r = malloc(outmax + 1);
 if (r == NULL) exit(1);
 if (e)
 {
   char *h, *n;

   for (h = n = s; *h != '\0' ; h++, n++)
   {
     if (*h == '\\')
     {
       switch(*++h)
       {
          case '0':
		if (isdigit(*(h+1)) && isdigit(*(h+2)))
		{
			char oct[4];
			int v;

			strncpy(oct, h, 4);
			v = (int)strtol(oct, NULL, 8);
			*n = (char) v;
			inlen -= 3;
			h += 2;
		}
		else
		{
			*n = '\0';
			--inlen;
		}
		break;
          case 'n': *n = '\n';	--inlen; break;
          case 't': *n = '\t';	--inlen; break;
          default: *n = *h;	--inlen; break;
       }
     }
     else *n = *h;
   }
   res = encode64(s, inlen, r, outmax, &outlen);
 }
 else
   res = decode64(s, inlen, r, &outlen);
 if (res < 0) {
   fprintf(stderr,"%s: error %d on %s\n", prg, res, s);
   exit(1);
 }
 if (verbose) {
   printf("'");
   printstr(s, inlen);
   printf("' ->\n'", s, r);
 }
 printstr(r, outlen);
 if (verbose) {
   putchar('\'');
 }
 putchar('\n');
/*
 printf("'%s' ->\n'%s'\n", s, r);
*/
 free(r);
}

int main(int argc, char *argv[])
{
 char *prg,*s;
 int enc, l;

 enc = 0;
 prg = argv[0];
 while (--argc>0 && (*++argv)[0]=='-') {
   for (s=argv[0]+1; *s != '\0'; s++) {
     switch (*s) {
       case 'e': enc = 1;        break;
       case 'v': verbose = 1;    break;
       default : fprintf(stderr,"%s: illegal option %c\n",prg,*s);
                 fprintf(stderr,"-e: encode (decode is default)\n");
                 exit(1);
     }
   }
 }
 if (argc < 1) {
   l = 1024;
   s = malloc(l+1);
   while (fgets(s, l, stdin) != NULL) {
      s[strlen(s)-1] = '\0';
      ed(enc, s, prg);
   }
  }
 else {
   while (argc--) {
     ed(enc, *argv, prg);
     argv++;
   }
 }
 exit(0);
}
