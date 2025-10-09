// src/app/layout.tsx
import ThemeRegistry from '@/theme/ThemeRegistry';

export const metadata = {
  title: 'Password Manager',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ThemeRegistry>{children}</ThemeRegistry>
      </body>
    </html>
  );
}