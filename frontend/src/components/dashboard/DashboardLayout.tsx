import type {
  ReactNode,
} from "react";

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({
  children,
}: DashboardLayoutProps) {
  return (
    <main className="mx-auto max-w-7xl px-6 py-8">
      {children}
    </main>
  );
}