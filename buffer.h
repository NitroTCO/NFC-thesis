#pragma once
#include <stdio.h>
#include <stdlib.h>

// "Language extension" stuff
#define or ||
#define and &&

// Constants
#define BIT_PERIOD      9.44e-6 // seconds
#define MAX_LINE_READ   255 // Max characters to read from a single line in trace file.

typedef struct buffer {
    double *values;
    double fs;
    size_t size;
    int start;
    FILE *trace;
    int next_index;
    int iter_finished;
    int (*fill)(struct buffer*);
    int (*partial_fill)(struct buffer*, size_t);
    double (*next)(struct buffer*);
    void (*save)(struct buffer*, char*);
} buffer;

buffer *init_buffer(FILE *trace, double fs);

void free_buffer(buffer *buf);
