# Saihate no Ima — MAO English translation

Version 1.0.0. Translation patch and full Japanese/English script reader.

Download: https://github.com/MAO-TLs/saihate-no-ima/releases/download/v1.0.0/saihate-no-ima-v1.0.0.zip

Requires a legally obtained Japanese copy of **Saihate no Ima COMPLETE** (Farthest2015). Follow the patch archive's bundled README. The Windows script installer is `Install.cmd` and requires Python 3. Optional movie-subtitle installation requires external FFmpeg; see the bundled instructions.

Credits: Project Lead — MAO; Translator — GPT-6 Astra; Special Thanks — gambs.

## Website development

Run `npm ci`, `npm test`, `npm run build`, and `npm run test:build`. `npm run preview` serves the generated site at `http://127.0.0.1:4323/saihate-no-ima/`.

The website uses the shared MAO publication and reader templates. Hyperlink previews preserve the accepted bilingual source-bound passages and original images. Native visual effects are not emulated.
