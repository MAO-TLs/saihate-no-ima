# Saihate no Ima — MAO English translation

Version 1.1.6. Translation patch and full Japanese/English script reader.

Download: https://github.com/MAO-TLs/saihate-no-ima/releases/download/v1.1.6/saihate-no-ima-v1.1.6.zip

Requires a legally obtained Japanese copy of **Saihate no Ima COMPLETE** (Farthest2015). Follow the patch archive's bundled README. The Windows script installer is `Install.cmd` and requires Python 3.10+. Optional movie-subtitle installation requires external FFmpeg; see the bundled instructions.

Credits: Project Lead — MAO; Translator — GPT-6 Astra; Special Thanks — gambs.

## Version 1.1.6 — October 9, 2026

Fixes scenario-advancement crashes caused by empty ruby-reading commands. Eleven commands across five scenario files now use native no-op slots. Visible translation, meaningful annotations, instruction positions, branches, hyperlinks and read-text tracking are unchanged. The executable, menus, embedded font, routing index and movies are byte-identical to v1.1.5.

Already on v1.1.5: close the game and run **Update-v1.1.5.cmd**. It verifies the complete English installation and backs up five scenario files before replacing them. **Undo-v1.1.6-update.cmd** reverses the update. Fresh installations use **Install.cmd**, with **Restore.cmd** for restoration. For older releases, restore with the matching package first, or update sequentially to v1.1.5 with the matching updaters. Keep all packages and backups. Saves and settings are untouched; installed movie subtitles need no reinstallation.

The exact empty-ruby payload reproduced a runtime abort in an isolated neutral Wine fixture; the replacement advanced normally. All 172 scenario scripts were scanned, and byte-preservation, fresh install/restore, update/undo, preflight rejection and rollback tests passed. Native Windows, the reported route and a full-game playthrough have not been verified.

v1.1.6 download SHA-256: `c907173f2204ea4cf87837de59ee730c05d587dec256a9037b6b5d2c55a00b71`.

## Version 1.1.5 — October 8, 2026

Applies four source-bound English corrections found in a script-wide critical-edition pass. They repair an actor assignment, a viewpoint referent, a recurrence mismatch, and an over-specified fragment. The game, bilingual reader, and searchable corpus use the same corrected wording.

Already on v1.1.4: close the game and run **Update-v1.1.4.cmd**. It verifies the complete English installation, backs up four scenario files and replaces only those files. **Undo-v1.1.5-update.cmd** reverses this update to v1.1.4; use it before restoring with the matching v1.1.4 package or undoing an older update. Fresh installations use **Install.cmd** and can be reversed with **Restore.cmd**. For older releases, restore with the matching package first, or update sequentially to v1.1.4 with its matching updater. Keep all packages and backups.

All other game files, the executable, routing index, menus, embedded symbol font, layout settings and movies are unchanged from v1.1.4. Saves and settings are not updater targets. All 46,618 source records and 426 scene bindings were included in the source-wide audit; source binding, native re-extraction, exact recurrence, control-flow preservation, line capacity, fresh install/restore, update/undo and interruption rollback checks passed locally. No new runtime playtest or full-game playthrough is claimed.

v1.1.5 download SHA-256: `d32d36ce157ab4f6fbdbb6280ca21e44b46c62b42ddc3a4e38b182ab13520711`.

## Version 1.1.4 — October 8, 2026

Corrects one dialogue line in both the game and bilingual reader to preserve a deliberate change of self-reference without adding a story explanation. The searchable corpus has the same correction, and reader data uses a new cache revision.

Already on v1.1.3: close the game and run **Update-v1.1.3.cmd**. It verifies the complete English installation, backs up one scenario file and replaces only that file. **Undo-v1.1.4-update.cmd** reverses this update to v1.1.3; use it before restoring with the matching v1.1.3 package or undoing an older update. Fresh installations use **Install.cmd** and can be reversed with **Restore.cmd**. For older releases, restore with the matching package first, or update to v1.1.3 with its matching updater. Keep all packages and backups.

All other game files, the executable, routing index, menus, embedded symbol font, layout settings and movies are unchanged from v1.1.3. Saves and settings are not updater targets. Source binding, native re-extraction, control-flow preservation, line capacity, fresh install/restore, update/undo and interruption rollback checks passed locally. No new runtime playtest or full-game playthrough is claimed.

v1.1.4 download SHA-256: `def4e7ab1fc1ff76c327851e8e45163bf12ac1958d1c1c003cc5713b9ed70140`.

## Version 1.1.3 — October 8, 2026

Corrects a malformed executable layout introduced by v1.1.2's embedded symbol font. An 8 KB unmapped gap between two added sections violated Windows PE image requirements and caused the reported “This app can't run on your PC” launch failure. The rebuilt executable places the sections contiguously, regenerates cache references and corrects the image size. New regression checks reject the old layout before packaging.

Already on v1.1.2: close the game and run **Update-v1.1.2.cmd**, even if the game currently cannot launch. It verifies the English files, backs up the executable and replaces only that executable. **Undo-v1.1.3-update.cmd** reverses this update; use it before restoring with your matching v1.1.2 package or undoing an older update. Fresh installations use **Install.cmd** and can be reversed with **Restore.cmd**. For older releases, restore with the matching package first. Keep all packages and backups.

Chapter scripts, the routing-index crash correction, reader text, movie subtitles, menus, English window title and original save-folder name are retained. The updater does not modify saves, settings or movies. PE layout, x86 font-hook execution, ASLR, fresh installer/restore, update/undo and interruption rollback checks passed locally. Native Windows launch confirmation remains pending; a full-game playthrough is not claimed.

v1.1.3 download SHA-256: `05a2a7867bf1c97527479061dc9a2d12c6d1fce9e1b1e01909f6e9f5c01819b3`.

## Version 1.1.2 — October 7, 2026

Fixes the reported chapter-transition crash by correcting the separate routing index across all affected chapters. Embeds a private, open-license symbol font for missing yen signs, stars, arrows, brackets and other script symbols; ordinary English keeps the selected font. The window title is now **Saihate no Ima Complete**, without changing the internal save-folder name. Story translation, reader text and movie subtitles are unchanged.

Already on v1.1.1: close the game and run **Update-v1.1.1.cmd**. It verifies the English game files, backs up the executable and chapter index, and updates only those two files. **Undo-v1.1.2-update.cmd** returns them to v1.1.1; use that before restoring with your matching older package. Fresh installations use **Install.cmd**; **Restore.cmd** reverses a fresh v1.1.2 installation. Keep all backups. Saves, settings and installed movie subtitles are not modified.

The failing branch was reproduced and replayed past its former crash point under Wine. Embedded symbols and the English caption were visually checked in the running engine. Local installer, direct update/undo and interruption rollback tests passed. Native Windows confirmation and a full-game playthrough are not claimed.

v1.1.2 download SHA-256: `162c3b3d93e88f81a07684ff6b6e8edd08dc0e4df2122f54f589d4859d868bc2`.

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
