#ifndef LIBLZMA_FILE_H
#define LIBLZMA_FILE_H 1

#include "liblzma.h"

#define kBufferSize (1 << 15)

typedef struct lzma_file {
	uint8_t buf[kBufferSize];
	lzma_stream strm;
	FILE *fp;
	bool encoding;
	bool eof;
} lzma_FILE;

lzma_FILE *lzma_open_real(lzma_ret *lzma_error, lzma_options_lzma *options, FILE *fp);

lzma_FILE *lzma_open(lzma_ret *ret, const char *path, const char *mode);

int lzma_flush(lzma_FILE *lzma_file);

int lzma_close_real(lzma_ret *lzma_error, lzma_FILE *lzma_file);

int lzma_close(lzma_ret *ret, lzma_FILE *lzma_file);

ssize_t lzma_read(lzma_ret *ret, lzma_FILE *lzma_file, void *buf, size_t len);

ssize_t lzma_write(lzma_ret *ret, lzma_FILE *lzma_file, void *buf, size_t len);

#endif /* LIBLZMA_FILE_H */
