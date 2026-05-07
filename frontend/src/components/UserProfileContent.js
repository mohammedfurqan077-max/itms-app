import { useEffect, useState } from "react";
import JawanLayout from "@/components/JawanLayout";
import StatusMessage from "@/components/StatusMessage";
import { useAuth } from "@/context/AuthContext";
import { usersApi } from "@/services/api";

export default function UserProfileContent() {
  const { user } = useAuth();
  const [form, setForm] = useState({ name: "", email: "" });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    setForm({ name: user?.name || "", email: user?.email || "" });
  }, [user]);

  async function saveProfile(event) {
    event.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      const nextUser = { ...(user || {}), name: form.name, email: form.email };
      localStorage.setItem("itms_user", JSON.stringify(nextUser));
      if (user?.id) await usersApi.update(user.id, { name: form.name, email: form.email });
      setMessage({ type: "success", text: "Profile saved." });
    } catch (error) {
      setMessage({ type: "error", text: error.response?.data?.detail || error.response?.data?.message || error.message || "Profile save failed." });
    } finally {
      setLoading(false);
    }
  }

  return (
    <JawanLayout title="Profile">
      <StatusMessage message={message} />
      <form onSubmit={saveProfile} className="machine-panel p-5">
        <label className="mb-5 block">
          <span className="mb-2 block text-sm font-black text-slate-300">Name</span>
          <input value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} className="machine-input h-14 w-full rounded-xl px-4 text-lg font-bold outline-none focus:border-blue-500" />
        </label>
        <label className="mb-6 block">
          <span className="mb-2 block text-sm font-black text-slate-300">Email</span>
          <input type="email" value={form.email} onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))} className="machine-input h-14 w-full rounded-xl px-4 text-lg font-bold outline-none focus:border-blue-500" />
        </label>
        <button disabled={loading} className="machine-btn machine-btn-primary min-h-16 text-xl disabled:opacity-60">
          {loading ? "Saving" : "Save"}
        </button>
      </form>
    </JawanLayout>
  );
}
