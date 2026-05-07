import { Eye, EyeOff } from "lucide-react";
import { useState } from "react";

const permissions = ["Set Time", "Auto Jump Auto", "Auto Circle Auto", "Blinker (Yellow)", "VIP"];

export default function AccountForm({ value, onChange, onSubmit, buttonLabel, loading }) {
  const [showPassword, setShowPassword] = useState(false);
  const isJawan = value.role === "Jawan";

  function updateField(field, fieldValue) {
    if (field === "role" && fieldValue === "Admin") {
      onChange({ ...value, role: fieldValue, permissions: [] });
      return;
    }
    onChange({ ...value, [field]: fieldValue });
  }

  function togglePermission(permission) {
    const current = value.permissions || [];
    const next = current.includes(permission) ? current.filter((item) => item !== permission) : [...current, permission];
    updateField("permissions", next);
  }

  return (
    <form onSubmit={onSubmit} className="rounded-xl bg-white p-6 shadow">
      <div className="grid gap-5 md:grid-cols-2">
        <label className="block">
          <span className="mb-2 block text-sm font-semibold text-slate-700">Name</span>
          <input
            value={value.name}
            onChange={(event) => updateField("name", event.target.value)}
            required
            className="h-12 w-full rounded-lg border border-slate-300 px-4 text-sm outline-none focus:border-blue-500"
          />
        </label>

        <label className="block">
          <span className="mb-2 block text-sm font-semibold text-slate-700">Email</span>
          <input
            type="email"
            value={value.email}
            onChange={(event) => updateField("email", event.target.value)}
            required
            className="h-12 w-full rounded-lg border border-slate-300 px-4 text-sm outline-none focus:border-blue-500"
          />
        </label>

        <label className="block">
          <span className="mb-2 block text-sm font-semibold text-slate-700">Password</span>
          <span className="flex h-12 items-center rounded-lg border border-slate-300 bg-white px-4 focus-within:border-blue-500">
            <input
              type={showPassword ? "text" : "password"}
              value={value.password}
              onChange={(event) => updateField("password", event.target.value)}
              required
              className="w-full text-sm outline-none"
            />
            <button type="button" onClick={() => setShowPassword((current) => !current)} className="text-slate-500">
              {showPassword ? <EyeOff size={19} /> : <Eye size={19} />}
            </button>
          </span>
        </label>

        <label className="block">
          <span className="mb-2 block text-sm font-semibold text-slate-700">Role</span>
          <select
            value={value.role}
            onChange={(event) => updateField("role", event.target.value)}
            className="h-12 w-full rounded-lg border border-slate-300 bg-white px-4 text-sm outline-none focus:border-blue-500"
          >
            <option>Admin</option>
            <option>Jawan</option>
          </select>
        </label>

        <label className="block">
          <span className="mb-2 block text-sm font-semibold text-slate-700">Status</span>
          <select
            value={value.status}
            onChange={(event) => updateField("status", event.target.value)}
            className="h-12 w-full rounded-lg border border-slate-300 bg-white px-4 text-sm outline-none focus:border-blue-500"
          >
            <option>Active</option>
            <option>Inactive</option>
          </select>
        </label>
      </div>

      {isJawan ? (
        <div className="mt-6">
          <p className="mb-3 text-sm font-semibold text-slate-700">Permissions</p>
          <div className="grid gap-3 rounded-lg border border-slate-200 bg-slate-50 p-4 sm:grid-cols-2 lg:grid-cols-3">
            {permissions.map((permission) => (
              <label key={permission} className="flex items-center gap-3 text-sm font-medium text-slate-700">
                <input
                  type="checkbox"
                  checked={(value.permissions || []).includes(permission)}
                  onChange={() => togglePermission(permission)}
                  className="h-4 w-4 rounded border-slate-300 text-blue-600"
                />
                {permission}
              </label>
            ))}
          </div>
        </div>
      ) : null}

      <div className="mt-6 flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="h-12 rounded-lg bg-blue-600 px-8 text-sm font-bold text-white shadow hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Saving..." : buttonLabel}
        </button>
      </div>
    </form>
  );
}
