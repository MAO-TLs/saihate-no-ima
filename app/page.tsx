import { InstallAnchorRelease } from "./InstallAnchorRelease";
import { SiteNav } from "./SiteNav";
import { SiteFooter } from "./SiteFooter";
import index from "../public/script-data/index.json";
import { countLabel } from "./count-label.mjs";

export const dynamic = "force-static";

export default function Home() {
  return (
    <main>
      <InstallAnchorRelease />
      <section className="hero">
        <picture>
          <img
            className="hero-backdrop"
            src="./forest-hero.png"
            alt=""
            aria-hidden="true"
          />
        </picture>
        <SiteNav
          releaseHref="./"
          scriptHref="./script/"
          currentPage="release"
        />

        <div className="hero-grid shell">
          <div className="hero-copy">
            <p className="eyebrow">An English translation by MAO</p>
            <h1>
              SAIHATE
              <br />
              NO&nbsp;IMA
            </h1>
            <p className="dek">
              <em>Saihate no Ima</em>, now in English for the first time.
              A complete translation from the Japanese, with attention to
              accuracy, character voice, and natural literary English.
            </p>
            <div className="hero-actions">
              <a className="button button-primary" href="https://github.com/MAO-TLs/saihate-no-ima/releases/download/v1.1.5/saihate-no-ima-v1.1.5.zip">
                Download complete release
                <span aria-hidden="true">↓</span>
              </a>
              <a className="button button-secondary" href="./script/">
                Script
                <span aria-hidden="true">→</span>
              </a>
            </div>
            <p className="compatibility">
              18.2 MB · <a href="https://github.com/MAO-TLs/saihate-no-ima/releases/tag/v1.1.5">Release notes</a>
              {" · Version 1.1.5 · Windows + Wine · Japanese COMPLETE edition required"}
            </p>
          </div>

          <div aria-hidden="true" />
        </div>
      </section>

      <section className="release-strip" aria-label="Release information">
        <div className="shell release-grid">
          <div>
            <span className="release-label">Version</span>
            <strong>v1.1.5</strong>
          </div>
          <div>
            <span className="release-label">Script coverage</span>
            <strong>Main game</strong>
          </div>
          <div>
            <span className="release-label">Passages</span>
            <strong>{countLabel(index.totalLines, "passage")}</strong>
          </div>
          <div>
            <span className="release-label">Status</span>
            <strong className="release-status">Released</strong>
          </div>
        </div>
      </section>

      <section className="section shell">
        <div className="section-heading">
          <p className="eyebrow">Read online</p>
          <h2>Browse the complete script</h2>
          <p>
            Read the Japanese and MAO English script side by side, with scene
            search, corpus search, direct passage links, and hover-over hyperlinks.
            The reader contains {countLabel(index.totalLines, "bilingual passage")}.
          </p>
        <a className="text-link" href="./script/">
          Open the script browser <span aria-hidden="true">→</span>
        </a>
        </div>
      </section>

      <section className="install-section" id="install">
        <div className="section shell">
          <div className="install-heading">
            <div className="section-heading">
              <p className="eyebrow">Installation</p>
              <h2>How to install the patch</h2>
            </div>
            <p className="install-requirement">
              Requires your own legally obtained Windows copy of
              {" "}<em>Saihate no Ima COMPLETE</em> (Farthest2015).
              Other editions are not supported. Follow the installation instructions
              bundled with the download.
            </p>
          </div>

          <ol className="install-steps">
            <li>
              <span>01</span>
              <div>
                <h3>Back up the originals</h3>
                <p>Keep a backup of your unmodified Japanese installation and saves before applying the English patch.</p>
              </div>
            </li>
            <li>
              <span>02</span>
              <div>
                <h3>Apply the English patch</h3>
                <p>Download and extract the patch. For a fresh installation, run Install.cmd. Already on v1.1.4? Close the game and run Update-v1.1.4.cmd. Other older patches must first be restored with their matching package, or updated sequentially to v1.1.4 with its matching updater. Follow the bundled README for details.</p>
              </div>
            </li>
            <li>
              <span>03</span>
              <div>
                <h3>Start the game</h3>
                <p>Start the patched game as directed in the bundled README. Keep your original Japanese files and saves backed up.</p>
              </div>
            </li>
          </ol>
          <aside className="install-warning">
            <strong>Translation patch</strong>
            <p>This is an unofficial, noncommercial translation patch. It does not include the original game; your legally obtained supported Japanese installation is required.</p>
          </aside>
        </div>
      </section>

      <section className="section shell credits-section">
        <div className="section-heading">
          <p className="eyebrow">Credits</p>
          <h2>MAO Translations</h2>
        </div>
        <dl className="credits">
          <div>
            <dt>Project Lead</dt>
            <dd>MAO</dd>
          </div>
          <div>
            <dt>Translator</dt>
            <dd>GPT-6 Astra</dd>
          </div>
          <div>
            <dt>Special Thanks</dt>
            <dd>gambs</dd>
          </div>
        </dl>
      </section>

      <SiteFooter />
    </main>
  );
}
