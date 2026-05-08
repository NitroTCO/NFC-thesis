CC = gcc
CFLAGS = -std=c11 -Wextra -Wpedantic -g3 -fsanitize=address
LDFLAGS =
SRC = $(wildcard *.c)
HEADERS = $(wildcard *.h)

.PHONY: clean

all: main

main: $(SRC)
	$(CC) -o $@ $^ $(CFLAGS) $(LDFLAGS)

clean:
	rm -f *~ *.o main
