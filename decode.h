#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "buffer.h"

#define BG_ERROR_MARGIN 1
typedef enum decode_t {Manchester, Miller} decode_t;
typedef char bit;

void decode(FILE *fh, double *buffer, double background_level, size_t buf_size, decode_t starting_mode);

bit manchester_decode(double *buf, size_t buf_size);

bit miller_decode(double *buf, size_t buf_size, bit last);

// Does the bits parity check.
int check_parity(bit *bit_list, int len);

// Seek the start of the message and set the file position indicator appropiately.
int find_start(FILE *fh, double *buffer, double background_level, size_t buf_size);
