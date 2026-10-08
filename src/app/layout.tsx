import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import SiteHeader from "@/components/SiteHeader";
import SiteFooter from "@/components/SiteFooter";
import { SITE_NAME, SITE_ORIGIN } from "@/lib/site";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL(SITE_ORIGIN),
  title: {
    default: "TrendAhead — See what's gaining momentum before everyone else does",
    template: "%s — TrendAhead",
  },
  description:
    "TrendAhead detects topics gaining unusual attention before they become obviously mainstream, using public Wikipedia attention data and a transparent 0–100 score. Experimental.",
  openGraph: {
    siteName: SITE_NAME,
    type: "website",
    url: "/",
    title: "TrendAhead — See what's gaining momentum before everyone else does",
    description:
      "Discover topics gaining unusual attention early, measured from public Wikipedia attention data with a transparent 0–100 score.",
  },
  twitter: {
    card: "summary",
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <SiteHeader />
        <div className="flex flex-1 flex-col">{children}</div>
        <SiteFooter />
      </body>
    </html>
  );
}
