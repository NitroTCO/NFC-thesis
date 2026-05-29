#include "dyn_arr.h"

int dynarr_grow(dynarr *da) {
    da->capacity *= 2;
    bit *new_values = realloc(da->values, da->capacity * sizeof(bit));
    if (new_values == NULL) {
        return 1;
    }
    da->values = new_values;
    return 0;
}

int append(dynarr *da, bit value) {
    if (da->size >= da->capacity) {
        if (dynarr_grow(da)) {
            return 1;
        }
    }
    da->values[da->size] = value;
    da->size++;
    return 0;
}

void print(dynarr *da) {
    for (size_t i = 0; i < da->size; i++) {
        printf("%d", (int)da->values[i]);
        if ((i+1) % 8 == 0) {
            printf(" ");
        }
    }
    printf("\n");
}

dynarr *dynarr_init(void) {
    dynarr *da = malloc(sizeof(dynarr));
    bit *values = malloc(sizeof(bit) * INIT_CAPACITY);
    da->values = values;
    da->capacity = INIT_CAPACITY;
    da->size = 0;

    da->append = &append;
    da->print = &print;
}

void dynarr_free(dynarr *da) {
    free(da->values);
    free(da);
}

