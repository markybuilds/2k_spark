import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";
import { ThemeProvider } from "@/components/theme";
import { RefreshProvider } from "@/contexts/refresh-context";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "2K Flash - NBA 2K25 eSports Match Prediction System",
  description: "Accurate predictions for NBA 2K25 eSports matches in the H2H GG League",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen flex flex-col`}
      >
        <ThemeProvider defaultTheme="dark">
          <RefreshProvider>
            <Header />
            <main className="flex-1 container-centered py-10">
              {children}
            </main>
            <Footer />
          </RefreshProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
