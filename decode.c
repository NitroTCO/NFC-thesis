#include "decode.h"

void decode(buffer *buf, double background_level, decode_t starting_mode) {
    if (!buf) {
        fprintf(stderr, "decode: buffer NULL");
        exit(1);
    }
    fprintf(stderr, "decode\n");

    decode_t mode = starting_mode;
    bit last_bit = -1;
    bit decoded_bit;
    char read = find_start(buf, background_level);
    int ith_bit = 1;

    if (read == -1) { return; }
    while (!read) {
        switch (mode) {
        case Manchester:
            decoded_bit = manchester_decode(buf, ith_bit);
            buf->save(buf, "a");
            switch (decoded_bit) {
            case -1:
                fprintf(stderr, " An error occurred during Manchester decoding\n");
                exit(2);
                break;
            case 2: // end of message
                mode = Miller;
                printf("\n");
                printf("Manchester decoding concluded. Switching...\n");
                exit(42);
                ith_bit = 1;
                if (find_start(buf, background_level)  == -1) {
                    return;
                };
                continue;
            default:
                fprintf(stderr, "%d", decoded_bit);
                break;
            };
            break;
        case Miller:
            decoded_bit = miller_decode(buf, last_bit, ith_bit);
            switch (decoded_bit) {
            case -1:
                fprintf(stderr, " An error occured during Miller decoding\n");
                exit(2);
                break;
            case 2: // End of message
                //TODO: !!! APPEND 0 !!!
                printf("0\n");
                printf("Miller decoding concluded. Switching...\n");
                ith_bit = 1;
                mode = Manchester;
                last_bit = -1;
                if (find_start(buf, background_level)) {
                    return;
                }
                continue;
            default:
                last_bit = decoded_bit;
                fprintf(stderr, "%d", (int)decoded_bit);
            }
            break;
        default:
            fprintf(stderr, "unknown decode method\n");
            exit(1);
        };
        read = buf->fill(buf);
        ith_bit++;
    }
}

bit manchester_decode(buffer *buf, int ith_bit) {
    if (!buf) { return -1; }

    double before = 0;
    double after = 0;
    size_t i = 0;
    while (!buf->iter_finished) {
        double x = buf->next(buf);
        if (i < buf->size/2) {
            if (x > before) {
                before = x;
            }
        } else {
            if (x > after) {
                after = x;
            }
        }
        i++;
    }
    buf->iter_finished = 0;
    if (fabs(before - after) < 0.1) {
        return 2; // end of message
    }
    return before > after ? 1 : 0;
}

bit miller_decode(buffer *buf, bit last, int ith_bit) {
    if (!buf) {
        fprintf(stderr, "miller_decode: buf NULL\n");
        return -1;
    }

    double before = 0;
    double after = 0;
    size_t i = 0;
    while (!buf->iter_finished) {
        double x = buf->next(buf);
        if (i < buf->size/2) {
            if (x > before) {
                before = x;
            }
        } else {
            if (x > after) {
                after = x;
            }
        }
        i++;
    }
    buf->iter_finished = 0;
    if (ith_bit % 9 == 0) {
        if (last == 1) {
            return 2; // end of message (!!!DO STILL APPEND 0!!!)
        }
    }
    if (fabs(before - after) > 0.1) {
        if (before < after) {
            return 1;
        } else {
            return 0;
        }
    }
    return 0;
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

int find_start(buffer *buf, double background_level) {
    if (!buf) {
        fprintf(stderr, "find_start: buffer NULL\n");
        return -1;
    }
    fprintf(stderr, "find_start\n");
    double x;
    int success;
    while (1) {
        success = buf->fill(buf);
        if (success != 0) {
            return success;
        }
        buf->iter_finished = 0;
        while (!buf->iter_finished) {
            x = buf->next(buf);
            if (fabs(x - background_level) > BG_THRESHOLD) {
                goto out_of_loops;
            }
        }
    }
    out_of_loops:
    buf->iter_finished = 0;
    fprintf(stderr, "Start Found!\n");
    buf->partial_fill(buf, (buf->size + buf->next_index) % buf->size);
    buf->start = buf->next_index;
    return 0;
}
