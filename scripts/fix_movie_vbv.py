#!/usr/bin/env python3
"""Standalone entry point for the PR #34 movie repair; report-only by default.

Diagnosis and algorithm: desidia-cyber.
Installed subtitles should use movie_tools/movie_install.py repair with their
existing receipt and subtitle bundle; see the release's movies/README.md.
"""
from movie_tools.fix_movie_vbv import main

if __name__ == '__main__':
    main()
