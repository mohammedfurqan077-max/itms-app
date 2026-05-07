import { useEffect } from "react";
import { useRouter } from "next/router";
import Sidebar from "@/components/Sidebar";
import { useAuth } from "@/context/AuthContext";
import { normalizeRole } from "@/utils/roles";

export default function AdminLayout({ children, title }) {
  const router = useRouter();
  const { ready, isAuthenticated, role } = useAuth();

  useEffect(() => {
    if (!ready) return;
    if (!isAuthenticated) {
      router.replace("/login");
      return;
    }
    if (normalizeRole(role) !== "admin") {
      router.replace("/user/dashboard");
    }
  }, [isAuthenticated, ready, role, router]);

  if (!ready || !isAuthenticated || normalizeRole(role) !== "admin") {
    return (
      <div className="machine-bg grid min-h-screen place-items-center text-slate-100">
        <div className="machine-card px-6 py-5 text-lg font-semibold">Loading admin</div>
      </div>
    );
  }

  return (
    <div className="machine-bg flex h-screen overflow-hidden text-slate-100">
      <Sidebar />
      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex min-h-20 items-center border-b border-slate-700/60 bg-slate-950/70 px-8 shadow-[0_10px_30px_rgba(0,0,0,0.35)] backdrop-blur">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-cyan-300/80">Admin Panel</p>
            <h1 className="text-2xl font-black text-white">{title}</h1>
          </div>
        </header>
        <section className="status-scroll min-h-0 flex-1 overflow-y-auto p-8">{children}</section>
      </main>
    </div>
  );
}
