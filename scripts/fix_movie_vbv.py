#!/usr/bin/env python3
"""Repair subtitled movies that hang the game when playback ends.

Rendering with `-q:v 1` and no `-bufsize` leaves vbv_buffer_size_value = 3 in
every MPEG-1 sequence header. Windows' MPEG Video Decoder then underflows at the
end of the stream, so the graph never posts EC_COMPLETE and the game waits on
the last frame. The original and working movies use 112; no other byte changes.

Usage: python fix_movie_vbv.py HD/mv0000.bin HD/mv0001.bin HD/mv0002.bin [--write]
Without --write the movies are only reported. --write keeps a .vbv-bak copy.
"""
import argparse
import bisect
import os
import shutil
import struct
from pathlib import Path

SEQUENCE_HEADER = bytes.fromhex('000001b3')
VBV_VALUE = 112
VBV_SHIFT = 3
VBV_MASK = 0x3ff


def video_payloads(data):
    """Yield (start, end) of each MPEG-1 video PES payload in a program stream."""
    cursor = 0
    while cursor < len(data):
        if data[cursor:cursor+3] != b'\0\0\1':
            raise ValueError(f'Invalid MPEG program-stream boundary at {cursor}')
        code = data[cursor+3]
        if code == 0xba:
            if data[cursor+4] >> 4 != 2:
                raise ValueError('Only MPEG-1 program streams are supported')
            cursor += 12
        elif code == 0xb9:
            cursor += 4
        elif code >= 0xbb:
            end = cursor + 6 + struct.unpack_from('>H', data, cursor+4)[0]
            if 0xe0 <= code <= 0xef:
                start = cursor + 6
                while data[start] == 0xff:
                    start += 1
                if data[start] & 0xc0 == 0x40:
                    start += 2
                start += {2: 5, 3: 10}.get(data[start] >> 4, 1)
                yield start, end
            cursor = end
        else:
            raise ValueError(f'Unexpected program-stream code {code:#x}')


def patch_headers(data, value=VBV_VALUE):
    """Set vbv_buffer_size_value in every sequence header; return the values found.

    Headers are located in the video elementary stream, not the file: audio could
    imitate a start code, and some headers straddle two PES packets.
    """
    segments = list(video_payloads(data))
    offsets, stream, length = [], bytearray(), 0
    for start, end in segments:
        offsets.append(length)
        stream += data[start:end]
        length += end - start

    def file_offset(position):
        index = bisect.bisect_right(offsets, position) - 1
        return segments[index][0] + position - offsets[index]

    found = []
    position = stream.find(SEQUENCE_HEADER)
    while position >= 0:
        fields = int.from_bytes(stream[position+4:position+12], 'big')
        found.append(fields >> VBV_SHIFT & VBV_MASK)
        fields = fields & ~(VBV_MASK << VBV_SHIFT) | value << VBV_SHIFT
        for index, byte in enumerate(fields.to_bytes(8, 'big')):
            data[file_offset(position + 4 + index)] = byte
        position = stream.find(SEQUENCE_HEADER, position + 4)
    if not found:
        raise ValueError('No MPEG sequence headers')
    return found


def repair(path, write):
    data = bytearray(path.read_bytes())
    found = patch_headers(data)
    print(f'{path}: {len(found)} sequence headers, vbv values {sorted(set(found))}')
    if set(found) == {VBV_VALUE} or not write:
        return
    shutil.copy2(path, path.with_name(path.name + '.vbv-bak'))
    temporary = path.with_name(path.name + '.vbv-tmp')
    temporary.write_bytes(data)
    os.replace(temporary, path)
    print(f'{path}: repaired')


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('movies', nargs='+', type=Path)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    for movie in args.movies:
        repair(movie, args.write)


if __name__ == '__main__':
    main()
