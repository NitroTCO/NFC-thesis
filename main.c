#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "decode.h"

#define or ||
#define and &&

#define BIT_PERIOD 9.44e-6
#define BG_ERROR_MARGIN 1


double FS = 0;
char *file_to_open = NULL;

int main(int argc, char *argv[]) {
    // paring arguments.
    char *default_file = "waveform-traces/trace-2026-03-30 16:20:55.750289-62.5Mss-12.5Mpts.txt";
    int help = 0;
    for (int i = 1; i < argc; i++) {
        if ((!strncmp(argv[i], "-h", 2) or !strncmp(argv[i], "--Help", 6)) and !help) {
            help = 1;
            printf("Usage:\n"
                   "    ./main [options]\n"
                   "Options:\n"
                   "    [-h | --Help]                  : Show this help message.\n"
                   "    [-f | --File] <trace-file>.txt : File with traces to decode.\n"
                   "    [-s | --Sample] <frequency>    : Sample frequency used to gather the data.\n");
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

    // 2. trace file.
    FILE *fh = fopen(file_to_open, "r");
    if (fh == NULL) {
        perror("main");
        exit(1);
    }
    printf("%d\n", (int)miller_decode(NULL, 0, 0));
    printf("%d\n", (int)manchester_decode(NULL, 0));
    printf("MAIN LOOP\n");
    // here read file and enter main loop.

    return 0;
}