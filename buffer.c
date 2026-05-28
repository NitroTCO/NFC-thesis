#include "buffer.h"

/*                  *
 * Internal Methods *
 *                  */

double next(buffer *buf) {
    if (!buf) {
        fprintf(stderr, "next: buffer NULL");
        exit(1);
    }
    buf->next_index = (buf->next_index + 1) % buf->size;
    if (buf->next_index == buf->start) {
        buf->iter_finished = 1;
    }
    return buf->values[buf->next_index];
}

int fill(buffer *buf) {
    return buf->partial_fill(buf, buf->size);
}

int partial_fill(buffer *buf, size_t chunk_size) {
    if (!buf) {
        fprintf(stderr, "fill: buffer NULL");
        exit(1);
    }
    size_t index = 0;
    char *success;
    while (index < chunk_size) {
        char line[MAX_LINE_READ];
        success = fgets(line, MAX_LINE_READ, buf->trace);
        fseek(buf->trace, -1, SEEK_CUR); // Somehow it skips the first character of every line except for the first...
        if (!success) {
            return -1;
        } else if (fgetc(buf->trace) == EOF) {
            fprintf(stderr, "End of file reached\n");
            return 1;
        }
        buf->values[(buf->start + index) % buf->size] = strtod(line, NULL);
        index++;
    }
    return 0;
}

void save(buffer *buf, char *mode) {
    FILE *save = fopen("test.txt", mode);
    for (size_t i = 0; i < buf->size; i++) {
        fprintf(save, "%lf\n", buf->values[(buf->start + i) % buf->size]);
    }
    fclose(save);
}

/*                    *
 * External functions *
 *                    */

buffer *init_buffer(FILE *trace, double fs) {
    buffer *buf = malloc(sizeof(buffer));
    if (!buf) { return NULL; }
    size_t buf_size = (size_t)(BIT_PERIOD * fs);
    double *vals = malloc(sizeof(double)*buf_size);
    if (!vals) {
        free(buf);
        return NULL;
    }
    buf->values = vals;
    buf->start = 0;
    buf->fs = fs;
    buf->size = buf_size;
    buf->next_index = -1;
    buf->iter_finished = 0;
    buf->trace = trace;
    buf->next = &next;
    buf->fill = &fill;
    buf->partial_fill = &partial_fill;
    buf->save = &save;

    return buf;
}

void free_buffer(buffer *buf) {
    if (!buf) {
        fprintf(stderr, "free_buffer: buffer NULL");
        return;
    }
    fclose(buf->trace);
    free(buf->values);
    free(buf);
}
