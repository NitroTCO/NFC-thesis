#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "buffer.h"

#define BG_THRESHOLD 1

typedef enum decode_t {Manchester, Miller} decode_t;
typedef char bit;

void decode(buffer *buf, double background_level, decode_t starting_mode);

bit manchester_decode(buffer *buf, int ith_bit);

bit miller_decode(buffer *buf, bit last, int ith_bit);

// Does the bits parity check.
int check_parity(bit *bit_list, int len);

// Seek the start of the message and set the file position indicator appropiately.
int find_start(buffer *buf, double background_level);
