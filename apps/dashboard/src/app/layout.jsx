
import "./globals.css";
import { ThemeProvider, AuthProvider } from "@/context";

export const metadata = {
  title: "TalkFlow Analytics",
  description: "Enterprise Contact Center & AI Telemetry Dashboard",
};

export default function RootLayout({ children }) {
  return (
    <html
      lang="en"
      className="h-full antialiased dark"
    >
      <body className="min-h-full flex flex-col font-sans">
        <ThemeProvider>
          <AuthProvider>{children}</AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
