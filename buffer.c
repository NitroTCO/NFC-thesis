#include "buffer.h"

double _FS = 0;

void set_fs(double fs) {
    _FS = fs;
}

double *make_buffer(void) {
    size_t buf_size = (size_t)(_BUF_SIZE);
    double *buffer = calloc(buf_size, sizeof(double));
    if (!buffer) {
        return NULL;
    }
    buffer[0] = 0.0;
    return buffer;
}

int fill_buffer(FILE *fh, double *buffer) {
    if (!fh or !buffer) {
        fprintf(stderr, "fill_buffer: file or buffer NULL\n");
        exit(1);
    }
    int index = 0;
    char *success;
    while (index < _BUF_SIZE) {
        char line[MAX_LINE_READ];
        success = fgets(line, MAX_LINE_READ, fh);
        fseek(fh, -1, SEEK_CUR); // Somehow it skips the first character of every line except for the first...
        if (!success) {
            return 0;
        } else if (fgetc(fh) == EOF) {
            fprintf(stderr, "End of file reached\n");
            return -1;
        }
        buffer[index] = strtod(line, NULL);
        index++;
    }
    return 1;
}
