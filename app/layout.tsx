import type { Metadata } from "next";
import "./globals.css";
import "./theme.css";
export const metadata: Metadata = {
  title: "Saihate no Ima | MAO",
  description: "The MAO English translation of Saihate no Ima, with the full bilingual script reader.",
  robots: { index: true, follow: true },
};
export default function RootLayout({children}: Readonly<{children: React.ReactNode}>) {
  return <html lang="en"><body>{children}</body></html>;
}
