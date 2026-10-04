import { SiteNav } from "../SiteNav";
import { SiteFooter } from "../SiteFooter";
import { ScriptBrowser } from "./ScriptBrowser";
export default function ScriptPage() { return <main className="reader-page">
  <header className="reader-header"><SiteNav releaseHref="../" scriptHref="./" currentPage="script" />
  <div className="reader-intro shell"><p className="eyebrow">Script version · 1.0.0</p><h1>Script browser</h1><p>Read <em>Saihate no Ima</em> beside its Japanese source, search the script, and follow its hyperlinks. Hover over a hyperlink to read its original Japanese or English destination. Source images are preserved; native game effects are not emulated.</p></div></header>
  <ScriptBrowser />
  <SiteFooter /></main>; }
