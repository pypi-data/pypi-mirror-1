import httplib

_UNKNOWN = 'UNKNOWN'


class myHTTPResponse(httplib.HTTPResponse):
    def _read_chunked(self, amt):
        assert self.chunked != _UNKNOWN
        chunk_left = self.chunk_left
        value = ''

        # XXX This accumulates chunks by repeated string concatenation,
        # which is not efficient as the number or size of chunks gets big.
        while True:
            if chunk_left is None:
                line = self.fp.readline()
                i = line.find(';')
                if i >= 0:
                    line = line[:i] # strip chunk-extensions
                try:
                    chunk_left = int(line, 16)
                except ValueError:
                    # the chunked encoding somehow got messed up
                    # return what we got so far and ignore the rest
                    self.close()
                    return value
                if chunk_left == 0:
                    break
            if amt is None:
                value += self._safe_read(chunk_left)
            elif amt < chunk_left:
                value += self._safe_read(amt)
                self.chunk_left = chunk_left - amt
                return value
            elif amt == chunk_left:
                value += self._safe_read(amt)
                self._safe_read(2)  # toss the CRLF at the end of the chunk
                self.chunk_left = None
                return value
            else:
                value += self._safe_read(chunk_left)
                amt -= chunk_left

            # we read the whole chunk, get another
            self._safe_read(2)      # toss the CRLF at the end of the chunk
            chunk_left = None

        # read and discard trailer up to the CRLF terminator
        ### note: we shouldn't have any trailers!
        while True:
            line = self.fp.readline()
            if line == '\r\n':
                break

        # we read everything; close the "file"
        self.close()

        return value

httplib.HTTPConnection.response_class = myHTTPResponse


