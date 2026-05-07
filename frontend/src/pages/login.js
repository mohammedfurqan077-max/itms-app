import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { Lock, Mail, RadioTower } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { getRoleHome } from "@/utils/roles";

export default function LoginPage() {
  const router = useRouter();
  const { login, ready, isAuthenticated, role } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (ready && isAuthenticated) {
      router.replace(getRoleHome(role));
    }
  }, [isAuthenticated, ready, role, router]);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
    } catch (loginError) {
      setError(loginError.response?.data?.message || loginError.message || "Unable to login");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-command-bg px-4 text-command-text">
      <section className="w-full max-w-md rounded border border-command-line bg-command-panel p-7 shadow-signal">
        <div className="mb-8 flex items-center gap-4">
          <div className="grid h-14 w-14 place-items-center rounded bg-command-cyan text-command-bg">
            <RadioTower size={30} strokeWidth={2.7} />
          </div>
          <div>
            <h1 className="text-3xl font-black">ITMS</h1>
            <p className="text-sm font-bold uppercase tracking-widest text-command-muted">Admin Control Login</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <label className="block">
            <span className="mb-2 block text-sm font-black uppercase text-command-muted">Email</span>
            <span className="flex min-h-14 items-center gap-3 rounded border border-command-line bg-command-bg px-4 focus-within:border-command-cyan">
              <Mail size={22} className="text-command-muted" />
              <input
                type="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="w-full bg-transparent text-lg font-bold text-command-text outline-none"
                autoComplete="email"
              />
            </span>
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-black uppercase text-command-muted">Password</span>
            <span className="flex min-h-14 items-center gap-3 rounded border border-command-line bg-command-bg px-4 focus-within:border-command-cyan">
              <Lock size={22} className="text-command-muted" />
              <input
                type="password"
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="w-full bg-transparent text-lg font-bold text-command-text outline-none"
                autoComplete="current-password"
              />
            </span>
          </label>

          {error && (
            <div role="alert" className="rounded border border-command-red/60 bg-command-red/10 px-4 py-3 text-sm font-bold text-command-red">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="min-h-16 w-full rounded bg-command-cyan px-5 text-lg font-black text-command-bg transition hover:bg-command-cyan/90 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "AUTHENTICATING" : "ENTER CONTROL ROOM"}
          </button>
        </form>
      </section>
    </main>
  );
}
