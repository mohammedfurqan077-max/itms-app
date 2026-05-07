import { Edit } from "lucide-react";
import { useRouter } from "next/router";
import { useCallback, useEffect, useState } from "react";
import Layout from "@/components/Layout";
import PageLoadedMarker from "@/components/PageLoadedMarker";
import StatusMessage from "@/components/StatusMessage";
import { usersApi } from "@/services/api";
import { getStoredAccounts } from "@/services/accountStore";

function rowsFrom(data) {
  if (Array.isArray(data)) return data;
  return data?.items || data?.users || data?.data || [];
}

function mergeAccounts(apiUsers, storedUsers) {
  const merged = [...apiUsers];
  storedUsers.forEach((storedUser) => {
    if (!merged.some((user) => user.email === storedUser.email)) {
      merged.unshift(storedUser);
    }
  });
  return merged;
}

function statusClass(status) {
  return String(status).toLowerCase() === "active" ? "machine-badge-green" : "machine-badge-gray";
}

export default function AllAccountPage() {
  const router = useRouter();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);

  const loadUsers = useCallback(async () => {
    setMessage(null);
    try {
      const response = await usersApi.list();
      setUsers(mergeAccounts(rowsFrom(response.data), getStoredAccounts()));
    } catch (error) {
      const storedAccounts = getStoredAccounts();
      setUsers(storedAccounts);
      setMessage({
        type: storedAccounts.length ? "success" : "error",
        text: storedAccounts.length
          ? "Showing accounts created in this browser. Backend GET /users is not available."
          : error.response?.data?.detail || error.response?.data?.message || error.message || "Unable to load accounts."
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  return (
    <Layout title="All Account">
      <PageLoadedMarker />
      <StatusMessage message={message} />
      <div className="machine-panel p-6">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-black text-white">All Account</h2>
          <button
            type="button"
            onClick={() => router.push("/admin/account/add")}
            className="machine-btn machine-btn-primary min-h-12 w-auto px-5 py-3 text-sm"
          >
            Add New
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] border-separate border-spacing-y-2 text-left">
            <thead>
              <tr className="text-sm font-semibold text-slate-400">
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="5" className="machine-card px-4 py-5 text-sm font-semibold text-slate-300">
                    Loading accounts
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan="5" className="machine-card px-4 py-5 text-sm font-semibold text-slate-300">
                    No accounts found
                  </td>
                </tr>
              ) : (
                users.map((user, index) => (
                  <tr key={user.id || user._id || user.email || index} className="machine-table-row text-slate-100">
                    <td className="rounded-l-xl px-4 py-4 text-sm font-semibold text-white">{user.name || "-"}</td>
                    <td className="px-4 py-4 text-sm text-slate-300">{user.email || "-"}</td>
                    <td className="px-4 py-4 text-sm font-semibold text-slate-200">{user.role || "-"}</td>
                    <td className="px-4 py-4">
                      <span className={`rounded-full px-3 py-1 text-xs font-bold ${statusClass(user.status || "active")}`}>{user.status || "Active"}</span>
                    </td>
                    <td className="rounded-r-xl px-4 py-4">
                      <button
                        type="button"
                        onClick={() => router.push(`/admin/account/check?id=${user.id || user._id || user.email || ""}`)}
                        className="inline-flex items-center gap-2 rounded-xl bg-[linear-gradient(145deg,#1d4ed8,#1e40af)] px-3 py-2 text-sm font-semibold text-white shadow-[3px_3px_8px_rgba(0,0,0,0.35),inset_0_1px_0_rgba(255,255,255,0.16)] transition hover:brightness-110"
                      >
                        <Edit size={16} />
                        Edit
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  );
}
