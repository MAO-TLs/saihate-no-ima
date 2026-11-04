"""Compile reviewed movie cues to plain, bottom-centered English subtitles.

This creates an ASS track, not an installed movie. Cue times are relative to
the first decoded movie frame, not the MPEG container's nonzero start time.
"""
import argparse
import hashlib
import json
from pathlib import Path


def ass_time(seconds):
    centiseconds = round(seconds * 100)
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    whole, fraction = divmod(remainder, 100)
    return f'{hours}:{minutes:02d}:{whole:02d}.{fraction:02d}'


def manifest_fingerprint(manifest):
    """Bind generated tracks to the exact draft, including review metadata."""
    canonical = json.dumps(manifest, ensure_ascii=False, sort_keys=True,
                           separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(canonical).hexdigest()


def reading_speed_report(manifest, threshold=22):
    """Expose rushed cues for editorial review without silently shortening text."""
    results = []
    for index, cue in enumerate(manifest['cues']):
        duration = cue['end'] - cue['start']
        if duration <= 0:
            raise ValueError('Reading-speed audit requires positive cue durations')
        characters = len(' '.join(cue['english'].split()))
        speed = characters / duration
        results.append({'cue_index': index, 'source_binding': cue['source_binding'],
                        'characters': characters, 'duration_seconds': round(duration, 3),
                        'characters_per_second': round(speed, 2),
                        'needs_readability_review': speed > threshold})
    return {'threshold_characters_per_second': threshold,
            'cue_count': len(results),
            'flagged_cue_count': sum(c['needs_readability_review'] for c in results),
            'cues': results,
            'note': 'Editorial warning only; this does not prove timing, source coverage, or game playback.'}


def compile_ass(manifest, preview_range=None):
    if not manifest.get('caption_review_complete') and preview_range is None:
        raise ValueError('Full caption review must be completed before compilation')
    cues = manifest['cues']
    if preview_range is not None:
        start, end = preview_range
        if not (0 <= start < end <= manifest['duration_seconds']):
            raise ValueError('Invalid bounded preview range')
        if any(c['start'] < end and c['end'] > start and
               not (start <= c['start'] < c['end'] <= end) for c in cues):
            raise ValueError('Preview boundaries must not cut a cue')
        cues = [c for c in cues if start <= c['start'] < c['end'] <= end]
    if not cues:
        raise ValueError('An empty subtitle track is not a localized movie')
    lines = ['[Script Info]',
             f'; Cue manifest SHA-256: {manifest_fingerprint(manifest)}',
             'ScriptType: v4.00+', 'PlayResX: 800',
             'PlayResY: 600', 'WrapStyle: 0', 'ScaledBorderAndShadow: yes', '',
             '[V4+ Styles]',
             'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
             'Style: Default,Arial,26,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,1,2,32,32,24,1', '',
             '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
    previous_end = 0
    if preview_range is not None:
        lines.insert(1, '; BOUNDED QA PREVIEW ONLY - NOT A RELEASE SUBTITLE TRACK')
    for cue in cues:
        start, end, text = cue['start'], cue['end'], cue['english']
        if not (0 <= start < end <= manifest['duration_seconds']):
            raise ValueError('Cue exceeds movie timeline or has invalid duration')
        if start < previous_end:
            raise ValueError('Overlapping cues require editorial consolidation')
        if not cue.get('source_binding') or not cue.get('timing_reviewed'):
            raise ValueError('Each cue needs a source binding and reviewed frame timing')
        if not text.strip() or any(c in text for c in '{}\\'):
            raise ValueError('Empty text or ASS override syntax is forbidden')
        rows = text.splitlines()
        if len(rows) > 2 or any(len(row) > 58 for row in rows):
            raise ValueError('Subtitles need at most two readable fitted rows')
        rendered = r'\N'.join(rows)
        lines.append(f'Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{rendered}')
        previous_end = end
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('source_movie', type=Path)
    parser.add_argument('output_ass', type=Path)
    parser.add_argument('--preview-range', nargs=2, type=float, metavar=('START', 'END'))
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    if hashlib.sha256(args.source_movie.read_bytes()).hexdigest() != manifest['source_sha256']:
        raise ValueError('Cue manifest does not bind this movie variant')
    if args.output_ass.exists():
        raise FileExistsError('Choose a new output path; existing tracks are preserved')
    track = compile_ass(manifest, args.preview_range)
    args.output_ass.write_text(track, encoding='utf-8')
    print(json.dumps({'cues': sum(line.startswith('Dialogue:') for line in track.splitlines()), 'ass': str(args.output_ass),
                      'cue_manifest_sha256': manifest_fingerprint(manifest),
                      'subtitle_track_sha256': hashlib.sha256(track.encode('utf-8')).hexdigest(),
                      'source_movie_sha256': manifest['source_sha256'],
                      'preview_only': args.preview_range is not None,
                      'movie_produced': False, 'installed': False}))


if __name__ == '__main__':
    main()
