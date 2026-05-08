#include <stdlib.h>
#include <math.h>
#include "decode.h"

short manchester_decode(double *buf, size_t buf_size) {
    if (!buf) { return -1; }

    double before = 0;
    double after = 0;
    for (size_t i = 0; i < buf_size; i++) {
        double x = buf[i];
        if (i < buf_size/2) {
            if (x > before) {
                before = x;
            }
        } else {
            if (x > after) {
                after = x;
            }
        }
    }
    if (fabs(before - after) < 0.001) {
        return 2; // end of message
    }
    return before > after ? 1 : 0;
}

short miller_decode(double *buf, size_t buf_size, short last) {
    if (!buf) { return -1; }

    double before = 0;
    double after = 0;
    for (size_t i = 0; i < buf_size; i++) {
        double x = buf[i];
        if (i < buf_size/2) {
            if (x > before) {
                before = x;
            }
        } else {
            if (x > after) {
                after = x;
            }
        }
    }
    if (fabs(before - after) > 0.1) {
        if (before < after) {
            return 1;
        } else {
            return 0;
        }
    } else if (last == 1) {
        return 3; // end of message (!!!DO STILL APPEND 0!!!)
    }
    return -1; // error
}
