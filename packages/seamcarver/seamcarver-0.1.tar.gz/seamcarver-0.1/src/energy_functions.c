#include "energy_functions.h"
#include "util.h"
#include <string.h>
#include <stdio.h>

void efun_compute_e_1(unsigned char *energy,
		      unsigned char *l_data, int width, int height);
void efun_update_e_1(unsigned char *energy,
		     unsigned char *l_data, int width, int height);

void efun_compute_e_HoG(unsigned char *energy,
			unsigned char *l_data, int width, int height);
void efun_update_e_HoG(unsigned char *energy,
		       unsigned char *l_data, int width, int height);


/*  ------------------[ known energy functions ]------------------  */
efun_registered_t efun_known[] = {
   {"e_1", efun_compute_e_1, efun_update_e_1},
   {"e_HoG", efun_compute_e_HoG, efun_update_e_HoG},
   {NULL, NULL, NULL}
};
char *efun_names[NELEMS(efun_known)] = {NULL};

efun_registered_t *efun_get(int id) {
   if ( 0 <= id && id < NELEMS(efun_known)-1 )
      return &efun_known[id];
   else
      return NULL;
}

char **efun_list() {
   if ( efun_names[0] == NULL ) {
      efun_registered_t *p = efun_known;
      char **q = efun_names;
      do {
	 *q = p->name;
	 q++; p++;
      } while ( p->name != NULL );
   }
   return efun_names;
}


/*  -------------------[ e_1 energy function ]--------------------  */

/*
 * e1(I) = | (d/dx) I | + | (d/dy) I |
 */

void
efun_compute_e_1(unsigned char *energy,
		 unsigned char *l_data, int width, int height) {
   int r, c, pos;

   /* compute: energy = | (d/dx) I | */
   for (r=0; r < height; r++) {
      pos = r * width;
      energy[pos] = abs(l_data[pos+1] - l_data[pos])/2;
      pos++;
      for (c=1; c < (width-1); c++,pos++) {
	 energy[pos] = abs(l_data[pos+1] - l_data[pos-1])/2;
      }
      energy[pos] = abs(l_data[pos] - l_data[pos-1])/2;
   }

   /* compute: energy += | (d/dy) I | */
   for (c=0; c < width; c++) {
      pos = c;
      energy[pos] += abs(l_data[pos+width] - l_data[pos])/2;
      pos += width;
      for (r=1; r < (height-1); r++, pos+=width) {
	 energy[pos] += abs(l_data[pos+width] - l_data[pos-width])/2;
      }
      energy[pos] += abs(l_data[pos] - l_data[pos-width])/2;
   }
}

void
efun_update_e_1(unsigned char *energy, 
		unsigned char *l_data, int width, int height) {
   /* XXX: STUB IMPLEMENTATION: just recomputes everything */
   efun_compute_e_1(energy, l_data, width, height);
}


/*
 * eHoG energy function
 * --------------------
 * 
 * 
 */

void
efun_compute_e_HoG(unsigned char *energy,
		   unsigned char *l_data, int width, int height) {
   /* XXX: IMPLEMENT */
   eprintf("e_HoG energy function not implemented yet.");
}

void
efun_update_e_HoG(unsigned char *energy,
		  unsigned char *l_data, int width, int height) {
   /* XXX: STUB IMPLEMENTATION: just recomputes everything */
   efun_compute_e_HoG(energy, l_data, width, height);
}
