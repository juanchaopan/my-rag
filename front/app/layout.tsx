import type { Metadata } from "next";
import "./globals.css";


export const metadata: Metadata = {
  title: "LangChain Docs RAG Example",
  description: "juanchaopan@gmail.com",
  icons: {
    icon: "/langchain-favicon.png",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
