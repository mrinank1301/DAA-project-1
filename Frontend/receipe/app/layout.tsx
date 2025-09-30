import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Link from "next/link";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "FlavorGraph - Intelligent Recipe Navigator",
  description: "Discover perfect recipes based on your available ingredients using intelligent algorithms powered by Graph Theory, Backtracking & Greedy Algorithms",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <nav className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <Link href="/" className="flex items-center gap-2">
                <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-600 to-teal-600">
                  🍳 FlavorGraph
                </span>
              </Link>
              <div className="flex items-center gap-6">
                <Link
                  href="/"
                  className="text-gray-600 hover:text-emerald-600 font-medium transition-colors"
                >
                  Home
                </Link>
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-600 hover:text-emerald-600 font-medium transition-colors"
                >
                  API Docs
                </a>
              </div>
            </div>
          </div>
        </nav>
        {children}
        <footer className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white mt-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            {/* Main Footer Content */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
              {/* Brand Section */}
              <div className="text-center md:text-left">
                <div className="flex items-center justify-center md:justify-start gap-2 mb-4">
                  <span className="text-3xl">🍳</span>
                  <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-teal-400">
                    FlavorGraph
                  </span>
                </div>
                <p className="text-gray-300 text-sm leading-relaxed">
                  Discover perfect recipes based on your available ingredients using intelligent algorithms.
                </p>
              </div>

              {/* Features Section */}
              <div className="text-center">
                <h3 className="text-lg font-semibold mb-4 text-emerald-400">Powered By</h3>
                <div className="space-y-2 text-sm text-gray-300">
                  <div className="flex items-center justify-center gap-2">
                    <span className="text-emerald-400">●</span>
                    <span>Graph Theory</span>
                  </div>
                  <div className="flex items-center justify-center gap-2">
                    <span className="text-teal-400">●</span>
                    <span>Backtracking Algorithm</span>
                  </div>
                  <div className="flex items-center justify-center gap-2">
                    <span className="text-cyan-400">●</span>
                    <span>Greedy Algorithm</span>
                  </div>
                </div>
              </div>

              {/* Quick Links */}
              <div className="text-center md:text-right">
                <h3 className="text-lg font-semibold mb-4 text-emerald-400">Quick Links</h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <Link href="/" className="text-gray-300 hover:text-emerald-400 transition-colors">
                      Home
                    </Link>
                  </div>
                  <div>
                    <a
                      href="http://localhost:8000/docs"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-300 hover:text-emerald-400 transition-colors"
                    >
                      API Documentation
                    </a>
                  </div>
                  <div>
                    <a
                      href="http://localhost:8000/api/v1/health"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-300 hover:text-emerald-400 transition-colors"
                    >
                      API Health
                    </a>
                  </div>
                </div>
              </div>
            </div>

            {/* Divider */}
            <div className="border-t border-gray-700 my-8"></div>

            {/* Bottom Section */}
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <div className="text-sm text-gray-400">
                © 2025 FlavorGraph. Built with ❤️ for food lovers.
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-400">
                <span className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                  Backend Active
                </span>
                <span className="hidden md:inline">|</span>
                <span>Next.js 15 × React 19</span>
              </div>
            </div>
          </div>

          {/* Decorative Bottom Bar */}
          <div className="h-1 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500"></div>
        </footer>
      </body>
    </html>
  );
}
