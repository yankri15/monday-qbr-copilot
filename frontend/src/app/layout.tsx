import type { Metadata } from "next";
import Image from "next/image";

import "./globals.css";

export const metadata: Metadata = {
  title: "QBR Co-Pilot",
  description: "monday.com-inspired customer success workspace for preparing QBR drafts.",
};

function TopBar() {
  return (
    <header className="sticky top-0 z-30 border-b border-[color:var(--color-border-strong)] bg-[color:var(--color-surface-glass)] backdrop-blur-xl">
      <div className="mx-auto flex w-full max-w-[1440px] items-center justify-between gap-6 px-5 py-4 sm:px-8">
        <div className="flex items-center gap-4">
          <div>
            <Image
              src="https://dapulse-res.cloudinary.com/image/upload/f_auto,q_auto/remote_mondaycom_static/img/monday-logo-x2.png"
              alt="monday.com"
              width={176}
              height={36}
              priority
              className="h-8 w-auto object-contain"
            />
            <h1 className="text-lg font-semibold tracking-[-0.03em] text-[color:var(--color-text-main)]">
              QBR Co-Pilot
            </h1>
          </div>
        </div>

        <div className="hidden items-center gap-3 rounded-full border border-[color:var(--color-border-soft)] bg-white/72 px-4 py-2 text-sm text-[color:var(--color-text-subtle)] shadow-[0_8px_24px_rgba(30,37,66,0.08)] md:flex">
          <span className="h-2.5 w-2.5 rounded-full bg-[color:var(--color-accent-mint)]" />
          QBR draft workspace for CSMs
        </div>
      </div>
    </header>
  );
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased" data-scroll-behavior="smooth">
      <body className="min-h-full">
        <div className="min-h-screen bg-[color:var(--color-page)] text-[color:var(--color-text-main)]">
          <div className="pointer-events-none fixed inset-0 opacity-90">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(91,108,255,0.2),_transparent_30%),radial-gradient(circle_at_top_right,_rgba(111,63,245,0.16),_transparent_25%),linear-gradient(180deg,_rgba(255,255,255,0.55),_rgba(244,247,255,0.96))]" />
            <div className="absolute inset-x-0 top-0 h-px bg-[linear-gradient(90deg,transparent,rgba(91,108,255,0.35),transparent)]" />
          </div>
          <div className="relative flex min-h-screen flex-col">
            <TopBar />
            <main className="mx-auto flex w-full max-w-[1440px] flex-1 flex-col px-5 py-6 sm:px-8 sm:py-8">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
