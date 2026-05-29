#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "dyn_arr.h"

#define BG_THRESHOLD 1.5
#define BIT_PERIOD 9.44e-6
#define MAX_LINE_READ 255

typedef enum decode_t {Manchester, Miller} decode_t;
typedef char bit;
typedef dynarr decoded_bits;

void decode(FILE *trace, double background_level, decode_t starting_mode, double fs);

// Seek the start of the message and set the file position indicator appropiately.
void find_start(FILE *trace, double background_level);

decoded_bits *manchester_decode(FILE *trace, double fs, double background_level);

decoded_bits *miller_decode(FILE *trace, double fs, double backgound_level);

// Does the bits parity check.
int check_parity(decoded_bits *bit_list);

double next(FILE *trace);
