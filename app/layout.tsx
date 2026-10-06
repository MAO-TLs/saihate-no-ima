import type { Metadata } from "next";
import { SITE_BASE_PATH } from "../site-target.mjs";
import "./globals.css";
import "./theme.css";
export const metadata: Metadata = {
  title: "Saihate no Ima | MAO",
  description: "The MAO English translation of Saihate no Ima, with the full bilingual script reader.",
  robots: { index: true, follow: true },
  icons: {
    icon: [
      { url: `${SITE_BASE_PATH}/favicon.ico`, sizes: "16x16 32x32 48x48", type: "image/x-icon" },
      { url: `${SITE_BASE_PATH}/favicon.png`, sizes: "32x32", type: "image/png" },
      { url: `${SITE_BASE_PATH}/favicon.svg`, sizes: "any", type: "image/svg+xml" },
    ],
    apple: { url: `${SITE_BASE_PATH}/apple-touch-icon.png`, sizes: "180x180", type: "image/png" },
  },
};
export default function RootLayout({children}: Readonly<{children: React.ReactNode}>) {
  return <html lang="en"><body>{children}</body></html>;
}
