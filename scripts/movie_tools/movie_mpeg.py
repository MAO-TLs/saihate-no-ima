"""Finish MPEG-1 program streams for the game's DirectShow playback path."""
import struct
try:
    from .fix_movie_vbv import patch_headers, VBV_VALUE
except ImportError:
    from fix_movie_vbv import patch_headers, VBV_VALUE

SEQUENCE_END = bytes.fromhex('000001b7')
PROGRAM_END = bytes.fromhex('000001b9')


def packets(data):
    cursor = 0
    while cursor < len(data):
        if len(data) - cursor < 4:
            raise ValueError('Truncated MPEG start code')
        if data[cursor:cursor+3] != b'\0\0\1':
            raise ValueError(f'Invalid MPEG program-stream boundary at {cursor}')
        code = data[cursor+3]
        if code == 0xba:
            if len(data) - cursor < 12:
                raise ValueError('Truncated MPEG pack header')
            if data[cursor+4] >> 4 == 2:
                end = cursor + 12
            elif data[cursor+4] >> 6 == 1:
                if len(data) - cursor < 14:
                    raise ValueError('Truncated MPEG-2 pack header')
                end = cursor + 14 + (data[cursor+13] & 7)
            else:
                raise ValueError('Invalid MPEG pack header')
        elif code == 0xb9:
            end = cursor + 4
        elif code >= 0xbb:
            if len(data) - cursor < 6:
                raise ValueError('Truncated MPEG packet header')
            size = struct.unpack_from('>H', data, cursor+4)[0]
            if not size:
                raise ValueError('Unbounded PES packet is not supported')
            end = cursor + 6 + size
        else:
            raise ValueError(f'Unexpected program-stream code {code:#x}')
        if end > len(data):
            raise ValueError('Truncated MPEG packet')
        yield cursor, end, code
        cursor = end


def finalize(data):
    entries = list(packets(data))
    video = [(start, end) for start, end, code in entries if 0xe0 <= code <= 0xef]
    if not video:
        raise ValueError('No MPEG video packets')
    if any(code == 0xb9 for _, _, code in entries[:-1]):
        raise ValueError('Premature program end')
    start, end = video[-1]
    result = bytearray(data)
    added_sequence = not data[start:end].endswith(SEQUENCE_END)
    if added_sequence:
        size = end - start - 6
        if size + 4 > 65535:
            raise ValueError('No room for sequence end in final video PES')
        result[end:end] = SEQUENCE_END
        struct.pack_into('>H', result, start+4, size+4)
    added_program = entries[-1][2] != 0xb9
    if added_program:
        result.extend(PROGRAM_END)
    list(packets(result))
    values = patch_headers(result)
    return bytes(result), {'sequence_end_added': added_sequence, 'program_end_added': added_program,
                           'vbv_headers': len(values), 'vbv_before': sorted(set(values)),
                           'vbv_after': VBV_VALUE}


def finalize_file(path):
    before = path.read_bytes()
    after, proof = finalize(before)
    if after != before:
        path.write_bytes(after)
    return proof
