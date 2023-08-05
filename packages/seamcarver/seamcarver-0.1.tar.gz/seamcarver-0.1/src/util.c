#include "util.h"
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <errno.h>

/* eprintf: print error message and exit */
void
eprintf(char *fmt, ...)
{
        va_list args;

        fflush(stdout);

        va_start(args, fmt);
        vfprintf(stderr, fmt, args);
        va_end(args);

        if (fmt[0] != '\0' && fmt[strlen(fmt)-1] == ':')
                fprintf(stderr, " %s", strerror(errno));
        fprintf(stderr, "\n");
        exit(2); /* conventional value for failed execution */
}

/* emalloc: malloc and report if error */
void *
emalloc(size_t SIZE) {
   void *p;
   p = malloc(SIZE);
   if (p == NULL)
      eprintf("malloc of %u bytes failed:", SIZE);
   return p;
}

/* ememdup: copy SIZE bytes from FROM to a malloc'ed buffer and return it */
void *
ememdup(void *FROM, size_t SIZE) {
   void *TO = emalloc(SIZE);
   memmove(TO, FROM, SIZE);
   return TO;
}

/*
 * Convert the image from rgb to grayscale. We use the ITU-R 601-2
 * luma transform.
 *    L = R * 299/100 + G * 587/100 + B * 114/1000;
 */
unsigned char *
convert_rgb_to_grayscale(unsigned char *rgb_data, int width, int height) {
   unsigned char *l_data =
      (unsigned char *)malloc(width*height*sizeof(unsigned char));
   int i, j;
   for (i=0, j=0; i<3*width*height; i+=3, j+=1) {
      l_data[j] = (299*rgb_data[i  ] +          /* R */
                   587*rgb_data[i+1] +          /* G */
                   114*rgb_data[i+2]) / 1000.;  /* B */
   }
   return l_data;
}
