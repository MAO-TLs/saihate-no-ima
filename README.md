# Saihate no Ima — MAO English translation

Version 1.0.0. Translation patch and full Japanese/English script reader.

Download: https://github.com/MAO-TLs/saihate-no-ima/releases/download/v1.0.0/saihate-no-ima-v1.0.0.zip

Requires a legally obtained Japanese copy of **Saihate no Ima COMPLETE** (Farthest2015). Follow the patch archive's bundled README. The Windows script installer is `Install.cmd` and requires Python 3. Optional movie-subtitle installation requires external FFmpeg; see the bundled instructions.

Credits: Project Lead — MAO; Translator — GPT-6 Astra; Special Thanks — gambs.

## Version 1.0.0 hotfix — October 4, 2026

The refreshed download standardizes four name occurrences to θ and restores separate items in eight bullet lists. Both the game patch and reader are corrected. The version remains 1.0.0; chapter titles, native hyperlinks, layout settings, movie-subtitle files, and saves are unchanged.

If the earlier 1.0.0 patch is already installed, first restore it with `Restore.cmd` from the earlier package, then run `Install.cmd` from the refreshed download. Movie subtitles do not need to be reinstalled.

Download SHA-256: `6c00c2566a0c186a8f300920ebed523adebadf64158a5527781a0d751df00f38`.

## Website development

Run `npm ci`, `npm test`, `npm run build`, and `npm run test:build`. `npm run preview` serves the generated site at `http://127.0.0.1:4323/saihate-no-ima/`.

The website uses the shared MAO publication and reader templates. Hyperlink previews preserve the accepted bilingual source-bound passages and original images. Native visual effects are not emulated.
