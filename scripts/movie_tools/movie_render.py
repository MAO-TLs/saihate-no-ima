"""Render source-owned opening movies into a NEW staging directory only.

No download, font installation, game replacement, save mutation, or release
approval occurs here. FFmpeg/ffprobe/libass and Arial are external prerequisites.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
from fractions import Fraction

from movie_bundle import (SCHEMA, SUPPORTED, file_hash, json_bytes, regular_file,
                          validate_approval_fields)
from movie_mpeg import finalize_file


def run(command, **kwargs):
    return subprocess.run(command, check=True, capture_output=True, text=True, **kwargs)


def executable(name):
    found = shutil.which(str(name))
    if not found:
        raise ValueError(f'External prerequisite is missing: {name}')
    return str(Path(found).resolve())


def inspect_timestamps(path, ffprobe, expected_frames):
    data = json.loads(run([ffprobe, '-v', 'error', '-select_streams', 'v:0',
                          '-show_entries', 'stream=time_base:frame=best_effort_timestamp,duration',
                          '-of', 'json', str(path)]).stdout)
    scale = Fraction(data['streams'][0]['time_base'])
    frames = data['frames']
    missing = [n for n,row in enumerate(frames) if 'best_effort_timestamp' not in row]
    # MPEG-1 may omit the final delayed frame's timestamp when several small
    # pictures share one PES packet. Its nominal duration is still explicit.
    # Do not invent an observed timestamp or tolerate missing interior timing.
    if missing and (missing != [len(frames)-1] or len(frames)<2 or
                    int(frames[-1].get('duration',0))*scale != Fraction(1,30)):
        raise ValueError('Movie has missing interior frame timestamps or invalid final timing')
    points = [int(row['best_effort_timestamp']) for row in frames if 'best_effort_timestamp' in row]
    if len(frames) != expected_frames:
        raise ValueError('Movie timestamp count differs from decoded frame count')
    if any(abs((b-a)*scale-Fraction(1,30)) > scale for a,b in zip(points,points[1:])):
        raise ValueError('Movie has dropped, duplicated, or irregular frame timestamps')
    return {'checked_frame_timestamps':len(points), 'frame_interval_seconds':'1/30',
            'continuous_frame_timestamps':not missing,
            'final_frame_uses_nominal_duration':bool(missing)}


def inspect_movie(path, ffmpeg, ffprobe):
    data = json.loads(run([ffprobe, '-v', 'error', '-count_frames',
                          '-show_entries', 'stream=codec_type,codec_name,width,height,avg_frame_rate,nb_read_frames,start_time,sample_rate,channels',
                          '-of', 'json', str(path)]).stdout)
    streams = data['streams']
    if len(streams) != 2:
        raise ValueError('Expected exactly one movie video and one audio stream')
    video = next(s for s in streams if s['codec_type'] == 'video')
    audio = next(s for s in streams if s['codec_type'] == 'audio')
    if (video['codec_name'], video['width'], video['height'], video['avg_frame_rate']) != ('mpeg1video', 800, 600, '30/1'):
        raise ValueError('Unexpected game movie video format')
    if (audio['codec_name'], audio['sample_rate'], audio['channels']) != ('mp2', '44100', 2):
        raise ValueError('Unexpected game movie audio format')
    if abs(float(video['start_time']) - float(audio['start_time'])) > 1 / 90000:
        raise ValueError('Audio/video start times differ')
    packet_hash = run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-i', str(path),
                       '-map', '0:a:0', '-c:a', 'copy', '-f', 'hash', '-hash', 'sha256', '-']).stdout.strip()
    if not packet_hash.startswith('SHA256='):
        raise ValueError('Audio packet hash was not produced')
    # Decode both entire streams; count_frames alone does not prove clean decode.
    run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-xerror', '-i', str(path), '-f', 'null', '-'])
    return {'video_frames': int(video['nb_read_frames']),
            'audio_packet_sha256': packet_hash.split('=', 1)[1],
            'video_start_seconds': video['start_time'],
            'audio_start_seconds': audio['start_time'], 'full_decode_passed': True,
            **inspect_timestamps(path, ffprobe, int(video['nb_read_frames']))}


def validate_bundle(bundle, allow_qa=False):
    manifest = json.loads(regular_file(bundle / 'movie-bundle.json').read_text(encoding='utf-8'))
    if manifest.get('schema') != SCHEMA or type(manifest.get('qa_only')) is not bool:
        raise ValueError('Unsupported movie bundle schema/mode')
    if manifest['qa_only'] and not allow_qa:
        raise ValueError('Unapproved QA bundle requires --qa; never install its output')
    if allow_qa and not manifest['qa_only']:
        raise ValueError('--qa is only for clearly labeled QA bundles')
    if len(manifest.get('movies', [])) != len(SUPPORTED):
        raise ValueError('Movie bundle must contain all three supported variants')
    for number, entry in enumerate(manifest['movies']):
        movie = f'mv{number:04d}.bin'
        source_hash, frames, audio_hash = SUPPORTED[number]
        expected = {'movie': movie, 'source_path': f'HD/{movie}',
                    'subtitle_track': f'movie-{number:02d}.ass',
                    'source_sha256': source_hash, 'expected_video_frames': frames,
                    'expected_audio_packet_sha256': audio_hash}
        if any(entry.get(key) != value for key, value in expected.items()):
            raise ValueError('Movie bundle binding/path differs from the supported edition')
        track = regular_file(bundle / entry['subtitle_track'])
        if file_hash(track) != entry['subtitle_track_sha256']:
            raise ValueError('Subtitle track checksum differs')
        if not manifest['qa_only']:
            approval = entry.get('editorial_approval')
            expected_binding = {key: entry[key] for key in
                                ('source_sha256', 'cue_manifest_sha256', 'subtitle_track_sha256')}
            validate_approval_fields(approval, expected_binding, track.read_bytes(), frames / 30)
    return manifest


def render_command(ffmpeg, source, destination):
    # Relative, copied ASS filename avoids FFmpeg filter quoting of user paths,
    # including Windows drive colons. No shell interprets any arguments.
    return [ffmpeg, '-hide_banner', '-loglevel', 'info', '-nostdin', '-n',
            '-i', str(source), '-map', '0:v:0', '-map', '0:a:0',
            '-vf', 'setpts=PTS-STARTPTS,ass=subtitles.ass',
            '-c:v', 'mpeg1video', '-pix_fmt', 'yuv420p', '-q:v', '1', '-threads', '1',
            '-enc_time_base', '1:30', '-fps_mode', 'passthrough', '-c:a', 'copy',
            '-f', 'mpeg', str(destination)]


def render_movies(game_root, bundle, output, ffmpeg='ffmpeg', ffprobe='ffprobe', qa=False):
    game_root, bundle, output = map(lambda p: Path(p).absolute(), (game_root, bundle, output))
    if os.path.lexists(output):
        raise FileExistsError('Choose a new render directory; existing data is preserved')
    resolved_output, resolved_game = output.resolve(), game_root.resolve()
    if (resolved_output.is_relative_to(resolved_game) or resolved_game.is_relative_to(resolved_output)
            or resolved_output.is_relative_to(bundle.resolve())):
        raise ValueError('Render output must be outside game files and the subtitle bundle')
    if any(p.is_symlink() for p in (output, *output.parents)):
        raise ValueError('Linked output directory is not supported')
    manifest = validate_bundle(bundle, qa)
    ffmpeg, ffprobe = executable(ffmpeg), executable(ffprobe)
    versions = {name: run([path, '-version']).stdout.splitlines()[0]
                for name, path in (('ffmpeg', ffmpeg), ('ffprobe', ffprobe))}
    if ' ass ' not in run([ffmpeg, '-hide_banner', '-filters']).stdout:
        raise ValueError('FFmpeg lacks the required libass ass filter')
    sources = []
    for entry in manifest['movies']:
        source = regular_file(game_root / entry['source_path'])
        if file_hash(source) != entry['source_sha256']:
            raise ValueError('User-owned original movie checksum differs; no output created')
        proof = inspect_movie(source, ffmpeg, ffprobe)
        if (proof['video_frames'] != entry['expected_video_frames'] or
                proof['audio_packet_sha256'] != entry['expected_audio_packet_sha256']):
            raise ValueError('Original frame/audio binding differs; no output created')
        sources.append((entry, source))
    output.mkdir(parents=True, exist_ok=False)
    work = output / 'render-work'
    work.mkdir()
    receipt = {'schema': 'saihate-movie-render-receipt-v1', 'qa_only': qa,
               'installed': False, 'native_playback_verified': False,
               'bundle_sha256': file_hash(bundle / 'movie-bundle.json'),
               'tool_versions': versions, 'movies': []}
    try:
        for entry, source in sources:
            # Recheck inputs immediately before each render. This is not a
            # sandbox against concurrent malicious local mutation.
            regular_file(source)
            if file_hash(source) != entry['source_sha256']:
                raise ValueError('Source changed during rendering')
            track = regular_file(bundle / entry['subtitle_track'])
            if file_hash(track) != entry['subtitle_track_sha256']:
                raise ValueError('Subtitle track changed during rendering')
            shutil.copyfile(track, work / 'subtitles.ass')
            candidate = work / entry['movie']
            command = render_command(ffmpeg, source, candidate)
            result = run(command, cwd=work)
            stream_end = finalize_file(candidate)
            # Do not silently accept a substituted font with different metrics.
            font_lines = [line for line in result.stderr.splitlines() if 'fontselect:' in line]
            if not font_lines or any(line.rsplit(',', 1)[-1].strip() not in
                                     ('Arial', 'ArialMT', 'Arial-Regular') for line in font_lines):
                raise ValueError('Arial was unavailable or a subtitle glyph used a fallback font')
            proof = inspect_movie(candidate, ffmpeg, ffprobe)
            if proof['video_frames'] != entry['expected_video_frames']:
                raise ValueError('Render changed the decoded video frame count')
            if proof['audio_packet_sha256'] != entry['expected_audio_packet_sha256']:
                raise ValueError('Render changed compressed original audio')
            if file_hash(source) != entry['source_sha256']:
                raise ValueError('Original movie changed during rendering')
            final = output / entry['movie']
            # New owned output directory; final name must still be unoccupied.
            if os.path.lexists(final):
                raise FileExistsError(final)
            candidate.rename(final)
            receipt['movies'].append({'movie': entry['movie'], 'sha256': file_hash(final),
                                       'size_bytes': final.stat().st_size,
                                       'source_sha256': entry['source_sha256'],
                                       'subtitle_track_sha256': entry['subtitle_track_sha256'],
                                       'font_selection': font_lines, 'stream_end': stream_end, **proof})
        receipt['render_complete'] = True
        with (output / 'movie-render-receipt.json').open('xb') as target:
            target.write(json_bytes(receipt))
    except Exception as error:
        receipt['render_complete'] = False
        receipt['error'] = str(error)
        with (output / 'FAILED-not-installable.json').open('xb') as target:
            target.write(json_bytes(receipt))
        raise
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game_root', type=Path)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--ffmpeg', default='ffmpeg')
    parser.add_argument('--ffprobe', default='ffprobe')
    parser.add_argument('--qa', action='store_true')
    args = parser.parse_args()
    receipt = render_movies(args.game_root, args.bundle, args.output, args.ffmpeg, args.ffprobe, args.qa)
    print(json.dumps({'render_complete': receipt['render_complete'], 'qa_only': args.qa,
                      'installed': False, 'movies': len(receipt['movies']), 'output': str(args.output)}))


if __name__ == '__main__':
    main()
