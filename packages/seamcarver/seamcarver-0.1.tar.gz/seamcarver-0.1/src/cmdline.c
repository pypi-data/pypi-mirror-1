#include <stdio.h>
#include <stdlib.h>
#include "util.h"
#include "seamcarver.h"

unsigned char *read_ppm(char *filename, int *width, int *height) {
   FILE *f;
   int depth;
   unsigned char *rgb_data;

   f = fopen(filename, "rb");
   if (f == NULL) eprintf("could not open %s:", filename);
   if ( !(getc(f) == 'P' && getc(f) == '6') ) { 
      eprintf("not a PPM (P6) file."); 
   }
   fscanf(f, "%d %d", width, height);
   fscanf(f, "%d", &depth);
   if (depth != 255) {
      eprintf("depth must be 255");
   }
   getc(f);

   rgb_data = (unsigned char *)emalloc(3*(*width)*(*height)*sizeof(unsigned char));
   fread(rgb_data, sizeof(unsigned char), 3*(*width)*(*height), f);
   fclose(f);
   return rgb_data;
}

void write_ppm(char *filename, unsigned char *rgb_data, int width, int height) {
   FILE *f;
   f = fopen(filename, "wb");
   if (f == NULL) eprintf("could not open %s:", filename);
   fprintf(f, "P6\n%d %d\n%d\n", width, height, 255);
   fwrite(rgb_data, sizeof(unsigned char), 3*width*height, f);
   fclose(f);
}


int main(int argc, char **argv) {
   seamcarver_t sc;
   int width, height;
   int new_width, new_height;
   unsigned char *rgb_data;
   FILE *f;

   if ( argc != 5 ) {
      printf("%s input.ppm output.ppm width height\n", argv[0]);
      exit(2);
   }

   rgb_data = read_ppm(argv[1], &width, &height);
   sc = seamcarver_new(rgb_data, width, height, 0);
   free(rgb_data);

   sscanf(argv[3], "%d", &new_width);
   sscanf(argv[4], "%d", &new_height);

   rgb_data = seamcarver_retarget(sc, new_width, new_height);

   write_ppm(argv[2], rgb_data, new_width, new_height);

   seamcarver_free(sc);

   return 0;
}
