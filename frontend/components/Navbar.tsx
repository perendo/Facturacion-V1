"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getToken, getUser, clearAuth } from "@/lib/auth";
import type { User } from "@/lib/types";
import Button from "@/components/ui/Button";

const nav = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/clients", label: "Clientes" },
  { href: "/products", label: "Productos" },
  { href: "/invoices", label: "Facturas" },
];

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUserState] = useState<User | null>(null);
  const [mounted, setMounted] = useState(false);
  const [dark, setDark] = useState(false);

  useEffect(() => {
    setMounted(true);
    setUserState(getUser<User>());
    const isDark = document.documentElement.classList.contains("dark");
    setDark(isDark);
  }, []);

  const toggleTheme = () => {
    const next = !dark;
    setDark(next);
    if (next) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  };

  const token = mounted ? getToken() : null;
  if (!token) return null;

  const logout = () => {
    clearAuth();
    router.push("/login");
  };

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-6">
          <Link href="/dashboard" className="text-lg font-bold text-indigo-600">
            Facturación
          </Link>
          <nav className="hidden gap-1 md:flex">
            {nav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
                  pathname?.startsWith(item.href)
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-3">
          <span className="hidden text-sm text-slate-600 sm:inline">
            {user?.full_name || user?.email}
          </span>
          <Button variant="ghost" onClick={toggleTheme} aria-label="Cambiar tema">
            {dark ? "☀️" : "🌙"}
          </Button>
          <Button variant="ghost" onClick={logout}>
            Salir
          </Button>
        </div>
      </div>
    </header>
  );
}