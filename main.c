#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "decode.h"
#include "buffer.h"

// "Language extension" stuff
#define or ||
#define and &&

// Constants
#define BIT_PERIOD      9.44e-6 // seconds
#define BUF_SIZE        (BIT_PERIOD*FS)
#define MAX_LINE_READ   255 // Max characters to read from a single line in trace file.


double FS = 0;
char *file_to_open = NULL;

void find_communication(FILE *fh, double *buffer, decode_t starting_mode) {
    if (!fh or !buffer) {
        fprintf(stderr, "find_communication: file or buffer NULL");
        exit(1);
    }
    fprintf(stderr, "find_communication\n");

    fill_buffer(fh, buffer);
    double background_level = buffer[0];

    find_start(fh, buffer, background_level, (size_t)BUF_SIZE);

    decode(fh, buffer, background_level, (size_t)BUF_SIZE, starting_mode);
}

int main(int argc, char *argv[]) {
    // paring arguments.
    char *default_file = "smoothed_signal.txt";
    for (int i = 1; i < argc; i++) {
        if ((!strncmp(argv[i], "-h", 2) or !strncmp(argv[i], "--Help", 6))) {
            printf("Usage:\n"
                   "    ./main [options]\n"
                   "Options:\n"
                   "    [-h | --Help]                  : Show this help message.\n"
                   "    [-f | --File] <trace-file>.txt : File with traces to decode.\n"
                   "    [-s | --Sample] <frequency>    : Sample frequency used to gather the data.\n");
            exit(0);
        } else if (!strncmp(argv[i], "-f", 2) or !strncmp(argv[i], "--File", 6)) {
            file_to_open = argv[i+1];
            i++;
        } else if (!strncmp(argv[i], "-s", 2) or !strncmp(argv[i], "--Sample", 8)) {
            FS = strtod(argv[i+1], NULL);
            i++;
        } else {
            fprintf(stderr, "Unknown argument: %s\n", argv[i]);
            exit(1);
        }
    }
    if (!file_to_open) {
        printf("Defaulting to trace file: %s\n", default_file);
        file_to_open = default_file;
    }
    if (!FS) {
        printf("Defaulting to a sample frequency of 62.5e6 Hz\n");
        FS = 62.5e6;
    }
    set_fs(FS);

    // 2. Open trace file.
    FILE *fh = fopen(file_to_open, "r");
    if (fh == NULL) {
        perror("main");
        exit(1);
    }

    // 3. Make buffer and read file.
    double *buffer = make_buffer();
    if (!buffer) {
        fprintf(stderr, "Failed initializing buffer!\n");
        exit(1);
    }
    find_communication(fh, buffer, Miller);
    free(buffer);

    fclose(fh);

    return 0;
}