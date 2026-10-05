# Saihate no Ima — MAO English translation

Version 1.1.1. Translation patch and full Japanese/English script reader.

Download: https://github.com/MAO-TLs/saihate-no-ima/releases/download/v1.1.1/saihate-no-ima-v1.1.1.zip

Requires a legally obtained Japanese copy of **Saihate no Ima COMPLETE** (Farthest2015). Follow the patch archive's bundled README. The Windows script installer is `Install.cmd` and requires Python 3. Optional movie-subtitle installation requires external FFmpeg; see the bundled instructions.

Credits: Project Lead — MAO; Translator — GPT-6 Astra; Special Thanks — gambs.

## Version 1.1.1 — October 6, 2026

Translates the in-game right-click menu and CG image-selection menu. The executable now loads game data beside itself, fixing copied installations that read Japanese scripts from an older registry path. Verification now rejects mixed original and English files. The story, bilingual reader, and movie subtitles are unchanged from v1.1.0.

Already on v1.1.0: close the game and run **Update-v1.1.0.cmd** from the new download. It accepts the original v1.1.0 executable or the earlier Windows path repair, verifies the English data, and backs up the executable. **Undo-v1.1.1-update.cmd** reverses the update; use that before restoring with your original v1.1.0 package. Fresh installations use **Install.cmd**. Movie subtitles do not need reinstalling. Saves are not modified; saves previously loaded from a separate registered installation remain in that folder.

The complete installer and direct updater passed local install/restore checks against the released files. Menu command IDs, flags, shortcuts, and existing settings dialogs are preserved. Confirmation on the affected native Windows machine remains pending.

v1.1.1 download SHA-256: `9666de7cd897515824d0219fd924ae2a570811f465a777fca9d8ac36096b6c9e`.

## Version 1.1.0 — October 5, 2026

Targeted source-bound corrections to character voice, forms of address, references, wordplay, and recurring wording are applied to both the game patch and bilingual reader. Standalone pause timing and dash spacing are now consistent with the source. This update contains 245 editorial corrections and 1,172 mechanical pause/spacing corrections; it is not a new full-script reread. Earlier interface, structured formatting, hyperlink, and movie-subtitle fixes remain included.

If v1.0.0 is installed, close the game and restore it with **Restore.cmd from the v1.0.0 package** before verifying and installing v1.1.0. Keep the packages and their backups. Saves are not patch targets. Optional movie-subtitle files and tools are unchanged and do not need to be reinstalled.

The packaged installer was verified on disposable copies, including restoration, upgrading, and interruption recovery. The matching reader passed its structural tests and production export checks. There was no new in-game or native Windows playtest, and no full-game playthrough.

v1.1.0 download SHA-256: `cb2c553e191c1600a3a2d4d400e0d304eaf0fe1be1df4324790f347fb1536d1e`.

## Version 1.0.0 hotfix — October 4, 2026

The refreshed download standardizes four name occurrences to θ and restores structured formatting across 52 source-reviewed reader passages: bullet and dashed lists, numbering, headings, tables, command blocks, and forum separators. The game patch corrects 35 affected structured passages; one four-item dialogue list uses a native continuation page. Hyperlink destinations and read-state IDs are preserved. The version remains 1.0.0; chapter titles, layout settings, movie-subtitle files, and saves are unchanged.

The same-version English cleanup also updates eight non-explicit passages in the reader and game: the approved affectionate nickname Immy, conventional English sounds, and redundant transliteration. The forum handle Super Kunoichi and source-written brand/compound names are retained. Context-dependent explicit passages are not rewritten by this hotfix.

The combined hotfix also corrects 39 non-explicit passages across 36 source-reviewed recurrence groups: repeated quotations, callbacks, dialogue, narration, and shared definitions with different native record boundaries. Context-dependent subjects, narrative tense, and sentence continuations are preserved rather than globally replaced. This is a targeted consistency correction, not a new full-script literary reread.

If the earlier 1.0.0 patch is already installed, first restore it with `Restore.cmd` from the earlier package, then run `Install.cmd` from the refreshed download. Movie subtitles do not need to be reinstalled.

Download SHA-256: `c2871cea0d711abc8447d41279833f58f4288b2f059465c88646b8ff277d2571`.

## Website development

Run `npm ci`, `npm test`, `npm run build`, and `npm run test:build`. `npm run preview` serves the generated site at `http://127.0.0.1:4323/saihate-no-ima/`.

The website uses the shared MAO publication and reader templates. Hyperlink previews preserve the accepted bilingual source-bound passages and original images. Native visual effects are not emulated.
