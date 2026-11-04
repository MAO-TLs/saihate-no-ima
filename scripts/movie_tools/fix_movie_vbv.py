#!/usr/bin/env python3
"""Repair the MPEG-1 VBV header behind the subtitled movie-end hang.

Diagnosis and PES-spanning repair algorithm: desidia-cyber, PR #34
https://github.com/MAO-TLs/saihate-no-ima/pull/34
Integrated by MAO with strict parsing and non-overwriting backups.
Reports only unless --write is supplied. For installed subtitles, prefer
movie_install.py repair so the existing original backups are verified.
"""
import argparse
import bisect
import os
from pathlib import Path
import stat
import struct

SEQUENCE_HEADER = bytes.fromhex('000001b3')
VBV_VALUE = 112
VBV_SHIFT = 3
VBV_MASK = 0x3ff


def video_payloads(data):
    """Yield bounded MPEG-1 PES payloads; never scan audio for video headers."""
    cursor = 0
    video_id = None
    while cursor < len(data):
        if len(data) - cursor < 4 or data[cursor:cursor+3] != b'\0\0\1':
            raise ValueError(f'Invalid MPEG program-stream boundary at {cursor}')
        code = data[cursor+3]
        if code == 0xba:
            if len(data) - cursor < 12 or data[cursor+4] >> 4 != 2:
                raise ValueError('Expected a complete MPEG-1 pack header')
            cursor += 12
        elif code == 0xb9:
            cursor += 4
            if cursor != len(data):
                raise ValueError('Premature MPEG program end')
        elif code >= 0xbb:
            if len(data) - cursor < 6:
                raise ValueError('Truncated PES length')
            size = struct.unpack_from('>H', data, cursor+4)[0]
            end = cursor + 6 + size
            if not size or end > len(data):
                raise ValueError('Unbounded or truncated MPEG packet')
            if 0xe0 <= code <= 0xef:
                if video_id not in (None, code):
                    raise ValueError('Multiple video streams are not supported')
                video_id = code
                start = cursor + 6
                while start < end and data[start] == 0xff:
                    start += 1
                if start < end and data[start] & 0xc0 == 0x40:
                    start += 2
                if start >= end:
                    raise ValueError('Truncated video PES header')
                kind = data[start] >> 4
                if kind in (2, 3):
                    start += 5 if kind == 2 else 10
                elif data[start] == 0x0f:
                    start += 1
                else:
                    raise ValueError('Unsupported MPEG-1 PES timestamp header')
                if start >= end:
                    raise ValueError('Missing video PES payload')
                yield start, end
            cursor = end
        else:
            raise ValueError(f'Unexpected program-stream code {code:#x}')


def patch_headers(data, value=VBV_VALUE):
    """Modify only VBV bits, including headers split across PES boundaries."""
    if type(value) is not int or not 0 <= value <= VBV_MASK:
        raise ValueError('VBV value must fit ten bits')
    segments = list(video_payloads(data))
    offsets, stream = [], bytearray()
    for start, end in segments:
        offsets.append(len(stream))
        stream += data[start:end]

    def file_offset(position):
        index = bisect.bisect_right(offsets, position) - 1
        return segments[index][0] + position - offsets[index]

    found, changes = [], []
    position = stream.find(SEQUENCE_HEADER)
    while position >= 0:
        if position + 12 > len(stream):
            raise ValueError('Truncated MPEG sequence header')
        fields = int.from_bytes(stream[position+4:position+12], 'big')
        if not fields & (1 << 13):
            raise ValueError('Invalid MPEG sequence-header marker')
        found.append(fields >> VBV_SHIFT & VBV_MASK)
        fields = fields & ~(VBV_MASK << VBV_SHIFT) | value << VBV_SHIFT
        for index, byte in enumerate(fields.to_bytes(8, 'big')):
            changes.append((file_offset(position + 4 + index), byte))
        position = stream.find(SEQUENCE_HEADER, position + 4)
    if not found:
        raise ValueError('No MPEG sequence headers')
    # Validate the entire input before making even an in-memory mutation.
    for offset, byte in changes:
        data[offset] = byte
    return found


def repair(path, write=False):
    path = Path(path)
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or getattr(info, 'st_file_attributes', 0) & 0x400:
        raise ValueError('Expected an ordinary, non-linked movie file')
    original = path.read_bytes()
    data = bytearray(original)
    found = patch_headers(data)
    print(f'{path}: {len(found)} sequence headers, VBV values {sorted(set(found))}')
    if data == original or not write:
        return
    if not info.st_mode & 0o222 or getattr(info, 'st_file_attributes', 0) & 1:
        raise ValueError('Read-only movie; no permissions were changed')
    backup = path.with_name(path.name + '.vbv-bak')
    temporary = path.with_name(path.name + '.vbv-tmp')
    if backup.exists() or backup.is_symlink() or temporary.exists() or temporary.is_symlink():
        raise ValueError('Existing backup/temporary retained; inspect it before retrying')
    for target, content in [(backup, original), (temporary, data)]:
        with target.open('xb') as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
    if path.read_bytes() != original:
        raise ValueError('Movie changed during repair; backup and temporary retained')
    os.chmod(temporary, stat.S_IMODE(info.st_mode))
    os.replace(temporary, path)
    print(f'{path}: repaired; original retained at {backup}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('movies', nargs='+', type=Path)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    for movie in args.movies:
        repair(movie, args.write)


if __name__ == '__main__':
    main()
