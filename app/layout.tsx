"use client";

import { Geist } from "next/font/google";
import { Geist_Mono } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import "./globals.css";
import { ThemeProvider } from "next-themes";
import { Navbar } from "@/components/Navbar";
import { Toaster } from "sonner";
import { useState } from "react";

const geistSans = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const handleSearch = (query: string) => {
    // Implement search functionality
    console.log("Searching for:", query);
  };

  const handleRandomMeme = () => {
    // Implement random meme functionality
    console.log("Getting random meme");
  };

  const handleMemeCreated = () => {
    // Implement meme created callback
    console.log("Meme created");
  };

  return (
    <ClerkProvider>
      <html lang="en" suppressHydrationWarning>
        <body
          className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        >
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            <div className="min-h-screen bg-background">
              <Navbar
                darkMode={darkMode}
                toggleDarkMode={toggleDarkMode}
                onSearch={handleSearch}
                onRandomMeme={handleRandomMeme}
                onMemeCreated={handleMemeCreated}
              />
              <main className="container py-6">{children}</main>
              <Toaster />
            </div>
          </ThemeProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
