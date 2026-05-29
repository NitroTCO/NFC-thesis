#pragma once

#include <stdio.h>
#include <stdlib.h>

#define and &&

#define INIT_CAPACITY 16

typedef char bit;

typedef struct dynarr {
    bit *values;
    size_t size;
    size_t capacity;
    int (*append)(struct dynarr*, bit);
    void (*print)(struct dynarr*);
} dynarr;

dynarr *dynarr_init(void);

void dynarr_free(dynarr *da);
