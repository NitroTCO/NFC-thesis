#include "decode.h"

// void save_buffer(FILE* fh, double *buffer, size_t buf_size) {
//     if (!fh or !buffer) {
//         return;
//     }
//     rewind(fh);
//     for (size_t i = 0; i < buf_size; i++) {
//         fprintf(fh, "%lf\n", buffer[i]);
//     }
//     exit(42);
// }

void decode(FILE *fh, double *buffer, double background_level, size_t buf_size, decode_t starting_mode) {
    if (!fh or !buffer) {
        fprintf(stderr, "decode: file or buffer NULL");
        exit(1);
    }
    fprintf(stderr, "decode\n");

    decode_t mode = starting_mode;
    bit last_bit = -1;
    bit decoded_bit;
    char read = fill_buffer(fh, buffer);
    if (read == -1) { return; }
    while (read) {
        switch (mode) {
        case Manchester:
            decoded_bit = manchester_decode(buffer, buf_size);
            switch (decoded_bit) {
            case -1:
                fprintf(stderr, "An error occurred during Manchester decoding\n");
                exit(2);
                break;
            case 2: // end of message
                mode = Miller;
                printf("\n");
                if (find_start(fh, buffer, background_level, buf_size)) {
                    return;
                };
                printf("Manchester decoding concluded. Switching...\n");
                continue;
            default:
                printf("%d", (int)decoded_bit);
                break;
            };
            break;
        case Miller:
            decoded_bit = miller_decode(buffer, buf_size, last_bit);
            switch (decoded_bit) {
            case -1:
                fprintf(stderr, "An error occured during Miller decoding\n");
                exit(2);
                break;
            case 2: // End of message
                //TODO: !!! APPEND 0 !!!
                printf("0\n");
                mode = Manchester;
                last_bit = -1;
                if (find_start(fh, buffer, background_level, buf_size)) {
                    return;
                }
                printf("Miller decoding concluded. Switching...\n");
                continue;
            default:
                last_bit = decoded_bit;
                printf("%d", (int)decoded_bit);
            }
            break;
        default:
            fprintf(stderr, "unknown decode method\n");
            exit(1);
        };
        read = fill_buffer(fh, buffer);
        if (read == -1) { return; }
    }
}

bit manchester_decode(double *buf, size_t buf_size) {
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

bit miller_decode(double *buf, size_t buf_size, bit last) {
    if (!buf) {
        fprintf(stderr, "miller_decode: buf NULL\n");
        return -1;
    }

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
    fprintf(stderr,  "%lf :||: %lf :||:||: %lf\n", before, after, fabs(before - after));
    if (fabs(before - after) > 0.1) {
        if (before < after) {
            return 1;
        } else {
            return 0;
        }
    } else if (last == 1) {
        return 2; // end of message (!!!DO STILL APPEND 0!!!)
    }
    return -1; // error
}

int check_parity(bit *bit_list, int len) {
    // Step through the list in chunks of 9 (8 data + 1 parity)
    for (int i = 0; i < len - 8; i += 9) {
        bit *byte_bits = &bit_list[i];
        if (i + 8 >= len) {
            break;
        }
        bit parity_bit = bit_list[i + 8];
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

int detect_change(double *buffer, double background_level, size_t buf_size) {
    if (!buffer) {
        fprintf(stderr, "detect_change: buffer NULL\n");
        exit(1);
    }
    for (size_t i = 0; i < buf_size; i++) {
        if (fabs(buffer[i] - background_level) > BG_ERROR_MARGIN) {
            return i;
        }
    }
    return -1;
}

int find_start(FILE *fh, double *buffer, double background_level, size_t buf_size) {
    if (!fh or !buffer) {
        fprintf(stderr, "find_start: file or buller NULL\n");
        exit(1);
    }
    fprintf(stderr, "find_start\n");
    int index = detect_change(buffer, background_level, buf_size);
    int acc = 0;
    while(index == -1) {
        acc++;
        if (fill_buffer(fh, buffer) == -1) {
            return 1;
        };
        index = detect_change(buffer, background_level, buf_size);
    }
    fprintf(stderr, "found starting point: %d after %d bit periods\n", index, acc);

    // Set filepointer to the found start
    fprintf(stderr, "%d\n", index-buf_size);
    if (fseek(fh, index-buf_size, SEEK_CUR)) {
        perror("find_communication");
        exit(1);
    }
    return 0;
}
