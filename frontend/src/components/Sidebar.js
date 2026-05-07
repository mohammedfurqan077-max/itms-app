import { useRouter } from "next/router";
import { ChevronDown, ChevronRight, CircleUserRound, LayoutDashboard, LogOut, MapPin, SlidersHorizontal, Users } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/context/AuthContext";

const menuGroups = [
  {
    label: "Account",
    icon: Users,
    items: [
      { href: "/admin/account/add", label: "New Account Add" },
      { href: "/admin/account/list", label: "All Account" },
      { href: "/admin/account/check", label: "Check Account" }
    ]
  },
  {
    label: "Junction",
    icon: MapPin,
    items: [{ href: "/admin/junctions", label: "Total Junction" }]
  },
  {
    label: "Mode",
    icon: SlidersHorizontal,
    items: [
      { href: "/admin/mode/change", label: "Change Mode" },
      { href: "/admin/mode/history", label: "Change Mode History" }
    ]
  }
];

export default function Sidebar() {
  const router = useRouter();
  const { logout } = useAuth();
  const [openGroups, setOpenGroups] = useState({
    Account: router.pathname.includes("/account"),
    Junction: router.pathname.includes("/junction"),
    Mode: router.pathname.includes("/mode")
  });

  function toggleGroup(label) {
    setOpenGroups((current) => ({ ...current, [label]: !current[label] }));
  }

  function navigateTo(path) {
    router.push(path);
  }

  return (
    <aside className="flex h-full w-72 shrink-0 flex-col border-r border-slate-700/60 bg-[linear-gradient(180deg,#020617,#0f172a_48%,#020617)] text-white shadow-[12px_0_28px_rgba(0,0,0,0.48)]">
      <div className="border-b border-slate-700/60 px-6 py-6">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-[linear-gradient(145deg,#38bdf8,#1d4ed8)] text-white shadow-[4px_4px_10px_rgba(0,0,0,0.55),inset_0_1px_0_rgba(255,255,255,0.28)]">
            <CircleUserRound size={25} strokeWidth={2.5} />
          </div>
          <div>
            <p className="text-lg font-bold tracking-wide">ITMS</p>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Admin Panel</p>
          </div>
        </div>
      </div>

      <nav className="flex flex-1 flex-col gap-1 px-4 py-5">
        <button
          type="button"
          onClick={() => navigateTo("/admin/dashboard")}
          className={`mb-2 flex min-h-12 items-center gap-3 rounded-xl px-4 text-sm font-semibold transition ${
            router.pathname === "/admin/dashboard"
              ? "bg-[linear-gradient(145deg,#2563eb,#1e40af)] text-white shadow-[0_0_18px_rgba(37,99,235,0.55),inset_0_1px_0_rgba(255,255,255,0.22)]"
              : "text-slate-300 hover:bg-slate-900 hover:shadow-[0_0_14px_rgba(59,130,246,0.22)]"
          }`}
        >
          <LayoutDashboard size={20} />
          Dashboard
        </button>

        {menuGroups.map((group) => {
          const Icon = group.icon;
          const open = openGroups[group.label];
          const activeGroup = group.items.some((item) => router.pathname === item.href);
          return (
            <div key={group.label}>
              <button
                type="button"
                onClick={() => toggleGroup(group.label)}
                className={`flex min-h-12 w-full items-center gap-3 rounded-xl px-4 text-left text-sm font-semibold transition ${
                  activeGroup
                    ? "bg-[linear-gradient(145deg,#1e293b,#0f172a)] text-white shadow-[0_0_16px_rgba(14,165,233,0.28)]"
                    : "text-slate-300 hover:bg-slate-900 hover:shadow-[0_0_14px_rgba(59,130,246,0.2)]"
                }`}
              >
                <Icon size={20} />
                <span className="flex-1">{group.label}</span>
                {open ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
              </button>
              {open && (
                <div className="ml-10 mt-1 space-y-1 border-l border-slate-800 pl-3">
                  {group.items.map((item) => (
                    <button
                      key={item.href}
                      type="button"
                      onClick={() => navigateTo(item.href)}
                      className={`block w-full rounded-xl px-3 py-2 text-left text-sm font-medium transition ${
                        router.pathname === item.href
                          ? "bg-[linear-gradient(145deg,#2563eb,#1d4ed8)] text-white shadow-[0_0_14px_rgba(37,99,235,0.45)]"
                          : "text-slate-400 hover:bg-slate-900 hover:text-white hover:shadow-[0_0_10px_rgba(59,130,246,0.18)]"
                      }`}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </nav>

      <button
        type="button"
        onClick={logout}
        className="m-4 flex min-h-12 items-center justify-center gap-3 rounded-xl border border-slate-700 bg-[linear-gradient(145deg,#1e293b,#0f172a)] px-4 text-sm font-semibold text-slate-200 shadow-[4px_4px_10px_rgba(0,0,0,0.45),inset_0_1px_0_rgba(255,255,255,0.08)] transition hover:brightness-110"
      >
        <LogOut size={19} />
        Logout
      </button>
    </aside>
  );
}
