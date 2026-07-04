import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "MealGenie v2 | Your AI Kitchen Assistant",
  description: "Snap a picture of your fridge and let our AI Swarm of Chefs, Nutritionists, and Sommeliers craft your perfect meal.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark h-full antialiased">
      <body className={`${inter.className} min-h-full flex flex-col bg-background text-foreground transition-colors duration-300`}>
        {children}
      </body>
    </html>
  );
}
