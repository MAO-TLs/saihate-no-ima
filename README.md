# v1.1.10 — Issue #29 fixes


- Repair the movie completion handler so the story continues after playback. Improve optional movie encoding quality and preserve frame timing.
- Rebuild chapter, CG, music and system-voice menus with consistent type sizes, baselines and complete labels. Restore the previous story-font renderer.
- Remove English ruby overlays and rewrite affected passages to retain their meaning in the prose.
- Repair report, profile, mail, forum and blog layouts; preserve lists, fit enlarged text, and correct clickable anchors and copied blog titles.
- Use measured font widths for regular dialogue. Reflow backlog prose to its own width while preserving paragraph/list breaks and joining source continuations.
- Include all 113 reviewed English gallery voice captions and repair gallery navigation.

**Updating v1.1.9:** close the game, extract this package, and run **Update-v1.1.9.cmd**. It verifies the installation, backs up all 165 changed targets, and preserves saves, settings and movies. **Undo-v1.1.10-update.cmd** restores v1.1.9. Keep all previous packages and backups.

**Fresh installation:** run **Install.cmd** on an unmodified Japanese COMPLETE installation. **Restore.cmd** reverses that fresh installation. For earlier English releases, restore with the matching package first or update sequentially to v1.1.9. Python 3.10+ is required.

**Previously subtitled movies:** the game-data updater does not replace movies. To obtain the encoding corrections, restore the original movies using the old package's movie_install.py restore command and matching subtitle bundle/render receipt. Then render into a new folder using this release, verify and install. Follow **movies/README.md**. No game video or audio is included.

Verification covers all issue screenshots and the reported font regressions, all 113 native gallery caption displays and returns, dialogue/backlog/list regressions, hyperlink navigation, sampled scrolling cadence, and natural completion of the reported movie followed by continued dialogue. These checks span isolated macOS/Wine QA builds; the shipped game targets match the final checked candidate. Windows hardware, a full-game playthrough, direct listening to every gallery clip, and frame-perfect playback on every system are not claimed.

The embedded symbol font is derived from Noto Sans JP under the SIL Open Font License 1.1; see SYMBOL-FONT-LICENSE.txt.

SHA-256: `05eb779d7d9e80a220db543e8a8e3ffb31037100f40eb644c7ba2d6cf0389f68`

---

# Saihate no Ima — MAO English translation

Version 1.1.9. Translation patch and full Japanese/English script reader.

Download: https://github.com/MAO-TLs/saihate-no-ima/releases/download/v1.1.9/saihate-no-ima-v1.1.9.zip

Requires a legally obtained Japanese copy of **Saihate no Ima COMPLETE** (Farthest2015). Follow the patch archive's bundled README. The Windows script installer is `Install.cmd` and requires Python 3.10+. Optional movie-subtitle installation requires external FFmpeg; see the bundled instructions.

Credits: Project Lead — MAO; Translator — GPT-6 Astra; Special Thanks — gambs.

## Version 1.1.9 — Text corrections

- Correct 39 textual records across the game and bilingual reader, including dialogue responses, references, wordplay and narrative continuity.
- Keep search and hyperlink previews synchronized with the corrected text, including the relocated span of an existing hyperlink.
- Repair six affected dialogue wraps associated with issue #26.

The executable and ten scenario files change. All earlier fixes are retained. Fonts, rendering, saves, settings and movie files are unchanged.

**Already on v1.1.8:** close the game, extract this download, and run **Update-v1.1.8.cmd**. The updater verifies the complete English installation, backs up the 11 changed files and applies only those changes. **Undo-v1.1.9-update.cmd** restores the v1.1.8 files; use it before restoring with the matching older package or undoing older updates. Keep all packages and backups.

**Fresh installation:** run **Install.cmd** on an unmodified Japanese COMPLETE installation. **Restore.cmd** reverses a fresh v1.1.9 installation. For older releases, restore with the matching package first, or update sequentially to v1.1.8 with the matching updaters. Python 3.10+ is required. Saves, settings, and movie files are not updater targets.

Opening-movie subtitles remain a separate optional installation: follow **movies/README.md** using your own movies. Install.cmd does not install movie subtitles. Previously installed subtitles do not need reinstalling.

Verification includes source-bound text projection, routing and read-ID preservation, unchanged control payloads and hyperlink destinations, reader/search/hover synchronization, final continuation-offset checks, PE layout validation, and reversible installation/update tests. This increment has not received a new in-game playtest; native Windows and a full-game playthrough were not tested.

The embedded symbol font is derived from Noto Sans JP under the SIL Open Font License 1.1; see SYMBOL-FONT-LICENSE.txt.

Download SHA-256: `da322bca060c2f0c3dd0c40cd7f6475eb257cfb39e73f307f881e8b907d4e42a`.

## Version 1.1.8 — Interface and text-layout repairs

Incremental repairs for issue #23:

- Complete the display-title inventory, including 71 previously omitted titles, without changing chapter routing keys.
- Translate truncated save labels without changing saved comments or save data.
- Repair wrapping in two custom panels, including portrait-column pagination and hyperlink placement.
- Clarify four connected dialogue records in the game and reader.

The executable and three scenario files change. All earlier fixes are retained. Georgia, the embedded symbol font, glyph rasterization, outline and shadow behavior remain unchanged. No experimental font-rendering changes are included.

**Already on v1.1.7:** close the game, extract this download, and run **Update-v1.1.7.cmd**. The updater verifies the complete English installation, backs up the 4 changed files and applies only those changes. **Undo-v1.1.8-update.cmd** restores the v1.1.7 files; use it before restoring with the matching older package or undoing older updates. Keep all packages and backups.

**Fresh installation:** run **Install.cmd** on an unmodified Japanese COMPLETE installation. **Restore.cmd** reverses a fresh v1.1.8 installation. For older releases, restore with the matching package first, or update sequentially to v1.1.7 with the matching updaters. Python 3.10+ is required. Saves, settings, and movie files are not updater targets.

Opening-movie subtitles remain a separate optional installation: follow **movies/README.md** using your own movies. Install.cmd does not install movie subtitles. Previously installed subtitles do not need reinstalling.

Verification includes title-hook emulation for all 418 executable routing titles, routing and read-ID preservation checks, reader synchronization, PE layout validation, and reversible installation/update tests. Under Wine, truncated save labels and both affected panels were visually checked; the relocated panel hyperlink also worked. Chapter History displayed existing checkpoint titles correctly, but the three specific later titles reported in the issue were not visually verified. Native Windows and a full-game playthrough were not tested.

The embedded symbol font is derived from Noto Sans JP under the SIL Open Font License 1.1; see SYMBOL-FONT-LICENSE.txt.

Download SHA-256: `3f34f25a93b6af10df4fdee5d2039e91f05bf71b2e00452a93103c1aeaffc3bd`.

## Version 1.1.7 — Interface and text-layout repairs

Repairs for the confirmed UI and layout defects reported in issue #21:

- Translate copied chapter-title display strings and remaining mapped native interface labels and dialogs without changing chapter routing keys or save locations.
- Add page breaks to overlong full-page text append chains, repair unnecessary sentence divisions, and restore missing line breaks in six structured lists.
- Standardize nine inconsistent speaker-name labels in the game and reader.

The executable and 56 scenario files change. All earlier fixes are retained. Georgia, the embedded symbol font, glyph rasterization, outline and shadow behavior remain unchanged. The separately reported distorted-letter appearance has not been confirmed fixed; this release does not include experimental font-rendering changes.

**Already on v1.1.6:** close the game, extract this download, and run **Update-v1.1.6.cmd**. The updater verifies the complete English installation, backs up the 57 changed files and applies only those changes. **Undo-v1.1.7-update.cmd** restores the v1.1.6 files; use it before restoring with the matching older package or undoing older updates. Keep all packages and backups.

**Fresh installation:** run **Install.cmd** on an unmodified Japanese COMPLETE installation. **Restore.cmd** reverses a fresh v1.1.7 installation. For older releases, restore with the matching package first, or update sequentially to v1.1.6 with the matching updaters. Python 3.10+ is required. Saves, settings, and movie files are not updater targets.

Opening-movie subtitles remain a separate optional installation: follow **movies/README.md** using your own movies. Install.cmd does not install movie subtitles. Previously installed subtitles do not need reinstalling.

Verification includes all 172 scenario scripts, text preservation apart from the nine name labels, routing and read-ID preservation, explicit full-page append-chain budgets, native-hook emulation including relocated image addresses, PE section adjacency, and reversible package installation/update tests. English chapter-selection labels and the exit-dialog caption were observed in an isolated Wine test copy. Native Windows, the reported Chapter History screen, and every repaired page have not been runtime-verified; no full-game playthrough is claimed.

The embedded symbol font is derived from Noto Sans JP under the SIL Open Font License 1.1; see SYMBOL-FONT-LICENSE.txt.

Download SHA-256: `16016327a3b7232f4e1d9728fbb9ea0f5891b3cd7680e7dd0e24537b55811180`.

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
