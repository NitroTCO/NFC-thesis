#include <stdlib.h>
#include <math.h>
#include <stdio.h>
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

int check_parity(short *bit_list, int len) {
    // Step through the list in chunks of 9 (8 data + 1 parity)
    for (int i = 0; i < len - 8; i += 9) {
        short *byte_bits = &bit_list[i];
        if (i + 8 >= len) {
            break;
        }
        short parity_bit = bit_list[i + 8];
        // Calculate parity (Odd)
        int ones_count = 0;
        for (int j = 0; j < 8; j++) {
            if (byte_bits[j] == 1) {
                ones_count++;
            }
        }
        if ((ones_count + parity_bit) % 2 != 0) {
            printf("Warning parity check unsuccessful\n");
            return 0;
        }
    }
    return 1;
}
