#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "decode.h"

// "Language extension" stuff
#define or ||
#define and &&

double FS = 0;
char *file_to_open = NULL;

void find_communication(FILE *trace, decode_t starting_mode) {
    if (!trace) {
        fprintf(stderr, "find_communication: trace NULL");
        exit(1);
    }

    double background_level = next(trace);
    if (!background_level) {
        return;
    }

    decode(trace, background_level, starting_mode, FS);
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

    // 2. Open trace file.
    FILE *trace = fopen(file_to_open, "r");
    if (trace == NULL) {
        perror("main");
        exit(1);
    }

    // 3. Decode communication.
    find_communication(trace, Miller);

    return 0;
}