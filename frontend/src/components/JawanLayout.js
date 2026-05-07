import { Activity, LogOut, SlidersHorizontal, UserRound } from "lucide-react";
import { useRouter } from "next/router";
import { useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { normalizeRole } from "@/utils/roles";

const navItems = [
  { href: "/user/dashboard", label: "Dashboard", icon: Activity },
  { href: "/user/control", label: "Control", icon: SlidersHorizontal },
  { href: "/user/profile", label: "Profile", icon: UserRound }
];

export default function UserLayout({ title, children }) {
  const router = useRouter();
  const { ready, isAuthenticated, role, logout } = useAuth();

  useEffect(() => {
    if (!ready) return;
    if (!isAuthenticated) {
      router.replace("/login");
      return;
    }
    if (normalizeRole(role) !== "jawan") {
      router.replace("/admin/dashboard");
    }
  }, [isAuthenticated, ready, role, router]);

  if (!ready || !isAuthenticated || normalizeRole(role) !== "jawan") {
    return (
      <div className="machine-bg grid min-h-screen place-items-center text-white">
        <div className="machine-card px-6 py-5 text-lg font-black">Loading user</div>
      </div>
    );
  }

  return (
    <div className="machine-bg min-h-screen text-white">
      <header className="sticky top-0 z-10 border-b border-slate-700/60 bg-slate-950/80 px-4 py-4 shadow-[0_10px_30px_rgba(0,0,0,0.38)] backdrop-blur">
        <div className="mx-auto flex max-w-3xl items-center justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Jawan Control</p>
            <h1 className="text-xl font-black">{title}</h1>
          </div>
          <button type="button" onClick={logout} className="rounded-xl bg-[linear-gradient(145deg,#1e293b,#0f172a)] p-3 text-slate-300 shadow-[4px_4px_10px_rgba(0,0,0,0.45),inset_0_1px_0_rgba(255,255,255,0.08)]">
            <LogOut size={21} />
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-4 pb-28 pt-5">{children}</main>

      <nav className="fixed bottom-0 left-0 right-0 border-t border-slate-700/60 bg-slate-950/90 px-3 py-3 shadow-[0_-12px_30px_rgba(0,0,0,0.42)] backdrop-blur">
        <div className="mx-auto grid max-w-3xl grid-cols-3 gap-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = router.pathname === item.href;
            return (
              <button
                key={item.href}
                type="button"
                onClick={() => router.push(item.href)}
                className={`flex min-h-16 flex-col items-center justify-center gap-1 rounded-2xl text-xs font-black ${
                  active
                    ? "bg-[linear-gradient(145deg,#2563eb,#1e40af)] text-white shadow-[0_0_18px_rgba(37,99,235,0.5),inset_0_1px_0_rgba(255,255,255,0.2)]"
                    : "bg-[linear-gradient(145deg,#1e293b,#0f172a)] text-slate-400 shadow-[3px_3px_9px_rgba(0,0,0,0.35)]"
                }`}
              >
                <Icon size={22} />
                {item.label}
              </button>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
