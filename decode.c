#include "decode.h"

void decode(FILE *trace, double background_level, decode_t starting_mode, double fs) {
    find_start(trace, background_level);
    decode_t mode = starting_mode;
    double read;
    decoded_bits *decoded;
    do {
        read = next(trace);
        bit last_bit = 2;
        switch (mode) {
        case Miller:
            decoded = miller_decode(trace, fs, background_level);
            decoded->print(decoded);
            if (!check_parity(decoded)) {
                dynarr_free(decoded);
                fclose(trace);
                exit(1);
            }
            find_start(trace, background_level);
            mode = Manchester;
            dynarr_free(decoded);
            break;

        case Manchester:
            decoded = manchester_decode(trace, fs, background_level);
            decoded->print(decoded);
            if (!check_parity(decoded)) {
                dynarr_free(decoded);
                fclose(trace);
                exit(1);
            }
            find_start(trace, background_level);
            mode = Miller;
            dynarr_free(decoded);
            break;

        default:
            fprintf(stderr, "unknown decode method\n");
            exit(1);
        }
    } while (read);
}

void find_start(FILE *trace, double background_level) {
    int acc = 0;
    double x = next(trace);
    while (x) {
        acc++;
        if (fabs(x - background_level) > BG_THRESHOLD) {
            return;
        }
        x = next(trace);
    }
}

decoded_bits *miller_decode(FILE *trace, double fs, double background_level) {
    fprintf(stderr, "miller_decode: ");
    decoded_bits *decoded = dynarr_init();

    double before = background_level;
    double after = background_level;
    int acc = 0;
    int i = 0;
    double x = next(trace);
    bit last_bit = -1;
    FILE *save = fopen("test.txt", "a");
    fprintf(save, "%lf\n", x);
    do {
        acc += 1;

        // bit period expired, decode
        if (acc/fs > BIT_PERIOD) {
            if (fabs(before - after) > BG_THRESHOLD) {
                if (before < after) {
                    decoded->append(decoded, 1);
                } else {
                    decoded->append(decoded, 0);
                }
            } else if (last_bit == 0) {
                // no more change detected, check if last was 0
                //   (where the end should have been detected) to make sure it
                //   is actually the end of message
                break;
            }
            before = background_level;
            after = background_level;
            acc = 0;
            if (decoded->size > 0) {
                last_bit = decoded->values[decoded->size - 1];
            }
            continue;
        }

        if (acc/fs > BIT_PERIOD/2) {
            if (x > after) {
                after = x;
            }
        } else {
            if (x > before) {
                before = x;
            }
        }
        x = next(trace);
        fprintf(save, "%lf\n", x);
    } while (x);

    fclose(save);
    return decoded;
}

decoded_bits *manchester_decode(FILE *trace, double fs, double background_level) {
    fprintf(stderr, "manchester_decode: ");
    decoded_bits *decoded = dynarr_init();

    double before = background_level;
    double after = background_level;
    int acc = 0;
    int i = 0;
    double x = next(trace);
    bit last_bit = -1;
    FILE *save = fopen("test.txt", "a");
    fprintf(save, "%lf\n", x);
    do {
        acc += 1;

        // bit period expired, decode
        if (acc/fs > BIT_PERIOD) {
            if (fabs(before - background_level) < BG_THRESHOLD and
                fabs(after - background_level) < BG_THRESHOLD) {
                    break;
            }
            decoded->append(decoded, before > after ? 1 : 0);

            before = background_level;
            after = background_level;
            acc = 0;
            continue;
        }

        if (acc/fs > BIT_PERIOD/2) {
            if (x > after) {
                after = x;
            }
        } else {
            if (x > before) {
                before = x;
            }
        }

        x = next(trace);
        fprintf(save, "%lf\n", x);
    } while (x);

    fclose(save);
    return decoded;
}

int check_parity(decoded_bits *decoded) {
    bit *bit_list = &(decoded->values[1]);
    // Step through the list in chunks of 9 (8 data + 1 parity)
    for (size_t i = 0; i < decoded->size - 8; i += 9) {
        bit *byte_bits = &bit_list[i];
        if (i + 8 >= decoded->size) {
            break;
        }
        bit parity_bit = bit_list[i + 8];
        // Calculate parity (Odd)
        int ones_count = 0;
        for (int j = 0; j < 8; j++) {
            ones_count += byte_bits[j];
        }
        if ((ones_count + parity_bit) % 2 == 0) {
            printf("Warning parity check unsuccessful\n");
            return 0;
        }
    }
    return 1;
}

double next(FILE *trace) {
    char *success;
    char line[MAX_LINE_READ];
    success = fgets(line, MAX_LINE_READ, trace);
    fseek(trace, -1, SEEK_CUR); // Somehow it skips the first character of every line except for the first...
    if (!success) {
        return 0;
    } else if (fgetc(trace) == EOF) {
        fprintf(stderr, "End of file reached\n");
        return 0;
    }
    return strtod(line, NULL);
}
