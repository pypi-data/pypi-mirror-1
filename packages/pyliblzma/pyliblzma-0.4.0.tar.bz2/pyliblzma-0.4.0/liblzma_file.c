#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <sys/types.h>

#include <lzma.h>

#include "liblzma_file.h"

lzma_FILE *lzma_open_real(lzma_ret *lzma_error, lzma_options_lzma *options, FILE *fp)
{
	lzma_ret *ret = lzma_error;
	bool encoding = options ? true : false;
	lzma_FILE *lzma_file;
    
	if (!fp)
		return NULL;

	lzma_file = calloc(1, sizeof(*lzma_file));

	if (!lzma_file) {
		(void) fclose(fp);
		return NULL;
	}

	lzma_file->fp = fp;
	lzma_file->encoding = encoding;
	lzma_file->eof = false;
	lzma_file->strm = LZMA_STREAM_INIT_VAR;

	if (encoding) {
		lzma_options_alone alone;
		alone.uncompressed_size = LZMA_VLI_VALUE_UNKNOWN;
		alone.lzma = *options;
		*ret = lzma_alone_encoder(&lzma_file->strm, &alone);
	} else
		*ret = lzma_auto_decoder(&lzma_file->strm, 0, 0);

	if (*ret != LZMA_OK) {
		(void) fclose(fp);
		memset(lzma_file, 0, sizeof(*lzma_file));
		free(lzma_file);
		return NULL;
	}
	return lzma_file;
}

lzma_FILE *lzma_open(lzma_ret *lzma_error, const char *path, const char *mode)
{
	bool encoding;
	int level = LZMA_EASY_DEFAULT;
	FILE *fp;
	lzma_options_lzma *options = NULL;
	for (; *mode != '\0'; mode++) {
		if (*mode == 'w')
			encoding = true;
		else if (*mode == 'r')
			encoding = false;
		else if (*mode >= '1' && *mode <= '9')
			level = (int)(*mode - '0');
	}
	if(encoding)
		*options = lzma_preset_lzma[level - 1];
	fp = fopen(path, encoding ? "wb" : "rb");

	return lzma_open_real(lzma_error, options, fp);
}

int lzma_flush(lzma_FILE *lzma_file)
{
	return fflush(lzma_file->fp);
}

int lzma_close_real(lzma_ret *lzma_error, lzma_FILE *lzma_file)
{
	lzma_ret *ret = lzma_error;	
	size_t n;

	if (!lzma_file)
		return -1;
	if (lzma_file->encoding) {
		for (;;) {
			lzma_file->strm.avail_out = kBufferSize;
			lzma_file->strm.next_out = (uint8_t *)lzma_file->buf;
			*ret = lzma_code(&lzma_file->strm, LZMA_FINISH);
			if (*ret != LZMA_OK && *ret != LZMA_STREAM_END)
				return -1;
			n = kBufferSize - lzma_file->strm.avail_out;
			if (n && fwrite(lzma_file->buf, 1, n, lzma_file->fp) != n)
				return -1;
			if (*ret == LZMA_STREAM_END)
				break;
		}
	} else
		*ret = LZMA_OK;

	lzma_end(&lzma_file->strm);
	memset(lzma_file, 0, sizeof(*lzma_file));
	free(lzma_file);
	return 0;
}

int lzma_close(lzma_ret *lzma_error, lzma_FILE *lzma_file)
{
	int rc;
	rc = lzma_close_real(lzma_error, lzma_file);
	if(rc)
		return rc;
	rc = fclose(lzma_file->fp);
	return rc;
}

ssize_t lzma_read(lzma_ret *lzma_error, lzma_FILE *lzma_file, void *buf, size_t len)
{
	lzma_ret *ret = lzma_error;
	bool eof = false;
    
	if (!lzma_file || lzma_file->encoding)
		return -1;
	if (lzma_file->eof)
		return 0;

	lzma_file->strm.next_out = buf;
	lzma_file->strm.avail_out = len;
	for (;;) {
		if (!lzma_file->strm.avail_in) {
			lzma_file->strm.next_in = (uint8_t *)lzma_file->buf;
			lzma_file->strm.avail_in = fread(lzma_file->buf, 1, kBufferSize, lzma_file->fp);
			if (!lzma_file->strm.avail_in)
				eof = true;
		}
		*ret = lzma_code(&lzma_file->strm, LZMA_RUN);
		if (*ret == LZMA_STREAM_END) {
			lzma_file->eof = true;
			return len - lzma_file->strm.avail_out;
		}
		if (*ret != LZMA_OK)
			return -1;
		if (!lzma_file->strm.avail_out)
			return len;
		if (eof)
			return -1;
	}
}

ssize_t lzma_write(lzma_ret *lzma_error, lzma_FILE *lzma_file, void *buf, size_t len)
{
	lzma_ret *ret = lzma_error;
	size_t n;

	if (!lzma_file || !lzma_file->encoding)
		return -1;
	if (!len)
		return 0;

	lzma_file->strm.next_in = buf;
	lzma_file->strm.avail_in = len;
	for (;;) {
		lzma_file->strm.next_out = (uint8_t *)lzma_file->buf;
		lzma_file->strm.avail_out = kBufferSize;
		*ret = lzma_code(&lzma_file->strm, LZMA_RUN);
		if (*ret != LZMA_OK)
			return -1;
		n = kBufferSize - lzma_file->strm.avail_out;
		if (n && fwrite(lzma_file->buf, 1, n, lzma_file->fp) != n)
			return -1;
		if (!lzma_file->strm.avail_in)
			return len;
	}
}
