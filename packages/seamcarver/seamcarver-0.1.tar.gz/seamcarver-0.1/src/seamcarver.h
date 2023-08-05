#ifndef _SEAMCARVER_H
#define _SEAMCARVER_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct seamcarver_struct *seamcarver_t;

seamcarver_t
seamcarver_new(unsigned char *rgb_data, int width, int height, 
	       int energy_function);

void
seamcarver_free(seamcarver_t);

unsigned char *
seamcarver_get_rgb_data(seamcarver_t);

unsigned char *
seamcarver_get_energy_data(seamcarver_t);

unsigned char *
seamcarver_retarget(seamcarver_t, int new_width, int new_height);
   
#ifdef __cplusplus
};
#endif

#endif /* _SEAMCARVER_H */
