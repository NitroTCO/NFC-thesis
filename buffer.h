#pragma once
#include <stdio.h>
#include <stdlib.h>

// "Language extension" stuff
#define or ||
#define and &&

// Constants
#define BIT_PERIOD      9.44e-6 // seconds
#define _BUF_SIZE        BIT_PERIOD * _FS
#define MAX_LINE_READ   255 // Max characters to read from a single line in trace file.

void set_fs(double fs);

double *make_buffer(void);

int fill_buffer(FILE *fh, double *buffer);
