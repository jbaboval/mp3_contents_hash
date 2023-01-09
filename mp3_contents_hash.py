""" MP3 Contents hasher

License: Apache 2.0
Adapted from https://github.com/pylon/streamp3/tree/master/streamp3

Hashes just the audio frame contents of MP3 files. This allows comparison
of files that have metadata that has been needlessly molested when indexed
by unscrupulious media players.
"""
import hashlib
from io import BytesIO

class MP3ContentsStream:
    """ MP3 Frame Stream

    sum = hashlib.md5()
    with open('my.mp3', 'rb') as mp3_file:
        chunk_stream = MP3ContentsHash(mp3_file)
        for chunk in chunk_stream:
            sum.update(chunk) 

    Args:
        stream (stream): the IO stream to attach
    """

    def __init__(self, stream):
        if isinstance(stream, bytes):
            stream = BytesIO(stream)

        self._stream = stream
        self._mp3_buffer = b''

        self._read_id3()

    def __iter__(self):
        """ return an iterator over the decoded stream """
        remains = True
        while remains:
            
            if len(self._mp3_buffer) < 4096:
                if not self._read_buffer():
                    remains = False
            
            size = min(4096, len(self._mp3_buffer))
            chunk = self._mp3_buffer[:size]
            self._mp3_buffer = self._mp3_buffer[size:]
            
            if chunk:
                yield chunk
            else:
                break

    def _read_id3(self):
        if not self._read_buffer():
            return False

        # decode the container id
        if self._mp3_buffer[:3] != 'ID3'.encode('ascii'):
            return False

        # decode the container flags
        flags = self._mp3_buffer[5]

        # decode the container size
        size = ((int(self._mp3_buffer[9]) << 0)
                | (int(self._mp3_buffer[8]) << 7)
                | (int(self._mp3_buffer[7]) << 14)
                | (int(self._mp3_buffer[6]) << 21))

        # add the header bytes
        size += 10

        # tack on another 10 if there is a footer
        if flags & 0x10:
            size += 10

        # load the container body
        while len(self._mp3_buffer) < size:
            if not self._read_buffer():
                return False

        # advance the buffer past the container
        self._mp3_buffer = self._mp3_buffer[size:]

        return True
    
    def _read_buffer(self):
        chunk = self._stream.read(8192)

        if not chunk:
            return False

        self._mp3_buffer += chunk
        return True