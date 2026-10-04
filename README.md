# Saihate no Ima — MAO English translation

Version 1.0.0. Translation patch and full Japanese/English script reader.

Download: https://github.com/MAO-TLs/saihate-no-ima/releases/download/v1.0.0/saihate-no-ima-v1.0.0.zip

Requires a legally obtained Japanese copy of **Saihate no Ima COMPLETE** (Farthest2015). Follow the patch archive's bundled README. The Windows script installer is `Install.cmd` and requires Python 3. Optional movie-subtitle installation requires external FFmpeg; see the bundled instructions.

Credits: Project Lead — MAO; Translator — GPT-6 Astra; Special Thanks — gambs.

## Version 1.0.0 hotfix — October 4, 2026

The refreshed download standardizes four name occurrences to θ and restores structured formatting across 52 source-reviewed reader passages: bullet and dashed lists, numbering, headings, tables, command blocks, and forum separators. The game patch corrects 35 affected structured passages; one four-item dialogue list uses a native continuation page. Hyperlink destinations and read-state IDs are preserved. The version remains 1.0.0; chapter titles, layout settings, movie-subtitle files, and saves are unchanged.

The same-version English cleanup also updates eight non-explicit passages in the reader and game: the approved affectionate nickname Immy, conventional English sounds, and redundant transliteration. The forum handle Super Kunoichi and source-written brand/compound names are retained. Context-dependent explicit passages are not rewritten by this hotfix.

The combined hotfix also corrects 39 non-explicit passages across 36 source-reviewed recurrence groups: repeated quotations, callbacks, dialogue, narration, and shared definitions with different native record boundaries. Context-dependent subjects, narrative tense, and sentence continuations are preserved rather than globally replaced. This is a targeted consistency correction, not a new full-script literary reread.

If the earlier 1.0.0 patch is already installed, first restore it with `Restore.cmd` from the earlier package, then run `Install.cmd` from the refreshed download. Movie subtitles do not need to be reinstalled.

Download SHA-256: `c2871cea0d711abc8447d41279833f58f4288b2f059465c88646b8ff277d2571`.

## Website development

Run `npm ci`, `npm test`, `npm run build`, and `npm run test:build`. `npm run preview` serves the generated site at `http://127.0.0.1:4323/saihate-no-ima/`.

The website uses the shared MAO publication and reader templates. Hyperlink previews preserve the accepted bilingual source-bound passages and original images. Native visual effects are not emulated.
