#pragma once

#include <stdlib.h>

short manchester_decode(double *buf, size_t buf_size);

short miller_decode(double *buf, size_t buf_size, short last);
