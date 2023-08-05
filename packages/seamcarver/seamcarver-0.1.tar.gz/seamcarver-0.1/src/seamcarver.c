#include <stdlib.h>
#include <string.h>
#include "seamcarver.h"
#include "energy_functions.h"
#include "util.h"

typedef struct seamcarver_struct {
   /* --[ image ]-- */
   int width;
   int height;
   unsigned char *rgb_data; /* RGB data */
   unsigned char *l_data; /* L data */

   /* --[ energy ]-- */
   int energy_function;
   void (*compute_energy)(unsigned char *, unsigned char *, int, int);
   void (*update_energy)(unsigned char *, unsigned char *, int, int);
   unsigned char *energy;

   /* --[ seams ]-- */
   int *seam; /* temporary seam, to avoid allocation/desallocation */

   /* --[ dynamic programming matrix ]-- */
   int **cost;
} struct_seamcarver_struct;

seamcarver_t 
seamcarver_new(unsigned char *rgb_data, int width, int height, 
	       int energy_function) {
   seamcarver_t sc;
   efun_registered_t *efun = efun_get(energy_function);
   int i;

   /*  ----------------------[ sanity checks ]-----------------------  */
   if (rgb_data == NULL || width <= 0 || height <= 0) { return NULL; }
   if (efun == NULL) { return NULL; }

   /*  --------------------------[ image ]---------------------------  */
   sc = (seamcarver_t)emalloc(sizeof(*sc));
   sc->width = width;
   sc->height = height;
   sc->rgb_data =
      (unsigned char *)ememdup(rgb_data,
                               3*width*height*sizeof(unsigned char));
   /* convert image to rgb to simplify energy computation */
   sc->l_data = convert_rgb_to_grayscale(sc->rgb_data, width, height);

   /*  --------------------------[ energy ]--------------------------  */
   sc->energy_function = energy_function;
   sc->energy = (unsigned char *)emalloc(width*height*sizeof(unsigned char));
   sc->compute_energy = efun->compute_energy;
   sc->update_energy = efun->update_energy;
   sc->compute_energy(sc->energy, sc->l_data, width, height); /* XXX */

   /*  --------------------------[ seams ]---------------------------  */
   /* allocate a temporary seam */
   sc->seam = (int *)emalloc(((width>height)?width:height)*sizeof(int));

   /*  ----------------[ dynamic programming matrix ]----------------  */
   sc->cost = (int **)emalloc(height*sizeof(int*));
   for (i=0; i<height; ++i)
      sc->cost[i] = (int *)emalloc(width*sizeof(int));

   return sc;
}

void
seamcarver_free(seamcarver_t sc) {
   free(sc->rgb_data);
   free(sc->l_data);
   free(sc->energy);
   free(sc->seam);
   free(sc);
}

unsigned char *
seamcarver_get_rgb_data(seamcarver_t sc) {
   return sc->rgb_data;
}

unsigned char *
seamcarver_get_energy_data(seamcarver_t sc) {
   return sc->energy;
}

/*  --------------------[ auxiliar functions ]--------------------  */

inline int
min2(int a, int b) {
   return (a < b)?a:b;
}

inline int 
min3(int a, int b, int c) {
   if ( a < b )
      return (a < c) ? a : c;
   else
      return (b < c) ? b : c;
}

void
seamcarver_find_minimum_horizontal_seam(seamcarver_t sc) {
}

void
seamcarver_remove_horizontal_seam(seamcarver_t sc) {
   int height = sc->height, width = sc->width;
   int r, c;
   int *s = sc->seam;
   unsigned char *rgb_source = sc->rgb_data;
   unsigned char *rgb_dest = sc->rgb_data;
   unsigned char *l_source = sc->l_data;
   unsigned char *l_dest = sc->l_data;

   for (r=0; r < height; r++) {
      /* copy the part of the line before the seam */
      for(c=0; c < width; c++) {
	 if ( s[c] == r ) {
	    rgb_source +=3;
	    l_source ++;
	 } else {
	    *rgb_dest++ = *rgb_source++;
	    *rgb_dest++ = *rgb_source++;
	    *rgb_dest++ = *rgb_source++;
	    *l_dest++ = *l_source++;
	 }
      }
   }
   sc->height--;
}

void
seamcarver_find_minimum_vertical_seam(seamcarver_t sc) {
   int width = sc->width, height = sc->height;
   unsigned char *energy = sc->energy;
   int r, c, min;
   int **cost = sc->cost;
   int *s = sc->seam;
   unsigned char *e;
   int *line;

   /* first row is initialized to the actual energy */
   for (c=0; c < width; c++) {
      cost[0][c] = energy[c];
   }

   /* fill dynamic programming matrix */
   e = &(energy[width]); /* start of second row */
   for (r=1; r < height; r++ ) {
      cost[r][0] = *e + min2(cost[r-1][0], cost[r-1][1]); e++;
      for (c=1; c < width-1; c++) {
	 cost[r][c] = *e + min3(cost[r-1][c-1], cost[r-1][c], cost[r-1][c+1]);
	 e++;
      }
      cost[r][width-1] = *e + min2(cost[r-1][width-2], cost[r-1][width-1]); e++;
   }

   /* find the minimum cost at the last line*/
   line = cost[height-1];
   min = 0;
   for (c=1; c < width; c++)
      if (line[c] < line[min])
	 min = c;

   /* rebuild the path */
   s[height-1] = min;
   for (r=height-2; r >= 0; r--) {
      c = s[r+1];
      if ( c == 0 ) { /* special case */
	 if (cost[r][c] < cost[r][c+1])
	    s[r] = c;
	 else
	    s[r] = c+1;
      } else if ( c == width-1 ) { /* special case */
	 if (cost[r][c-1] < cost[r][c])
	    s[r] = c-1;
	 else
	    s[r] = c;
      } else { /* general case */
	 if ( cost[r][c-1] < cost[r][c] ) {
	    if ( cost[r][c-1] < cost[r][c+1] )
	       s[r] = c-1;
	    else
	       s[r] = c+1;
	 } else {
	    if ( cost[r][c] < cost[r][c+1] )
	       s[r] = c;
	    else
	       s[r] = c+1;
	 }
      }
   }
}

void
seamcarver_remove_vertical_seam(seamcarver_t sc) {
   int height = sc->height, width = sc->width;
   int r, c;
   int *s = sc->seam;
   unsigned char *rgb_source = sc->rgb_data;
   unsigned char *rgb_dest = sc->rgb_data;
   unsigned char *l_source = sc->l_data;
   unsigned char *l_dest = sc->l_data;

   for (r=0; r < height; r++) {
      /* copy the part of the line before the seam */
      for(c=0; c < width; c++) {
	 if ( s[r] != c ) {
	    rgb_dest[0] = rgb_source[0];
	    rgb_dest[1] = rgb_source[1];
	    rgb_dest[2] = rgb_source[2];
	    l_dest[0] = l_source[0];

	    rgb_dest += 3; l_dest += 1;
	 }
	 rgb_source += 3; l_source += 1;
      }
   }
   sc->width--;
}

/*  -------------------------[ retarget ]-------------------------  */
unsigned char *
seamcarver_retarget(seamcarver_t sc, int new_width, int new_height) {
   int deltaw, deltah;
   if (new_width > sc->width || new_height > sc->height) {
      return NULL; /* XXX: we don't support stretching yet */
   }

   deltaw = new_width - sc->width;
   deltah = new_height - sc->height;

   while ( deltaw < 0 ) {
      sc->compute_energy(sc->energy, sc->l_data, sc->width, sc->height);
      seamcarver_find_minimum_vertical_seam(sc);
      seamcarver_remove_vertical_seam(sc);
      deltaw++;
   }

   while ( deltah < 0 ) {
      sc->compute_energy(sc->energy, sc->l_data, sc->width, sc->height);
      seamcarver_find_minimum_horizontal_seam(sc);
      seamcarver_remove_horizontal_seam(sc);
      deltah++;
   }
   return sc->rgb_data;
}
