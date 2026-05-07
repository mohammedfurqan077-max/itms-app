import { Edit, Trash2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import Layout from "@/components/Layout";
import PageLoadedMarker from "@/components/PageLoadedMarker";
import StatusMessage from "@/components/StatusMessage";
import { junctionsApi } from "@/services/api";

function rowsFrom(data) {
  if (Array.isArray(data)) return data;
  return data?.items || data?.junctions || data?.data || [];
}

export default function TotalJunctionPage() {
  const [form, setForm] = useState({ name: "", ip_address: "" });
  const [junctions, setJunctions] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const loadJunctions = useCallback(async () => {
    try {
      const response = await junctionsApi.list();
      setJunctions(rowsFrom(response.data));
    } catch (error) {
      setMessage({ type: "error", text: error.response?.data?.detail || error.response?.data?.message || error.message || "Unable to load junctions." });
    }
  }, []);

  useEffect(() => {
    loadJunctions();
  }, [loadJunctions]);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setMessage(null);
    const payload = {
      name: form.name,
      junction_name: form.name,
      ip_address: form.ip_address
    };

    try {
      if (editingId) {
        await junctionsApi.update(editingId, payload);
        setMessage({ type: "success", text: "Junction updated successfully." });
      } else {
        await junctionsApi.create(payload);
        setMessage({ type: "success", text: "Junction added successfully." });
      }
      setForm({ name: "", ip_address: "" });
      setEditingId(null);
      await loadJunctions();
    } catch (error) {
      setMessage({ type: "error", text: error.response?.data?.detail || error.response?.data?.message || error.message || "Unable to save junction." });
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(junction) {
    const id = junction.id || junction._id || junction.junction_id;
    if (!id) return;
    setMessage(null);
    try {
      await junctionsApi.remove(id);
      setMessage({ type: "success", text: "Junction deleted successfully." });
      await loadJunctions();
    } catch (error) {
      setMessage({ type: "error", text: error.response?.data?.detail || error.response?.data?.message || error.message || "Unable to delete junction." });
    }
  }

  function editJunction(junction) {
    setEditingId(junction.id || junction._id || junction.junction_id);
    setForm({
      name: junction.name || junction.junction_name || "",
      ip_address: junction.ip_address || junction.ip || ""
    });
  }

  return (
    <Layout title="Total Junction">
      <PageLoadedMarker />
      <StatusMessage message={message} />
      <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
        <form onSubmit={handleSubmit} className="rounded-xl bg-white p-6 shadow">
          <h2 className="mb-5 text-lg font-bold text-slate-900">Add Junction Form</h2>
          <label className="mb-5 block">
            <span className="mb-2 block text-sm font-semibold text-slate-700">Junction Name</span>
            <input
              value={form.name}
              onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
              required
              className="h-12 w-full rounded-lg border border-slate-300 px-4 text-sm outline-none focus:border-blue-500"
            />
          </label>
          <label className="mb-6 block">
            <span className="mb-2 block text-sm font-semibold text-slate-700">IP Address</span>
            <input
              value={form.ip_address}
              onChange={(event) => setForm((current) => ({ ...current, ip_address: event.target.value }))}
              required
              className="h-12 w-full rounded-lg border border-slate-300 px-4 text-sm outline-none focus:border-blue-500"
            />
          </label>
          <button disabled={loading} className="h-12 w-full rounded-lg bg-blue-600 text-sm font-bold text-white shadow hover:bg-blue-700 disabled:opacity-60">
            {loading ? "Saving..." : editingId ? "Update Junction" : "Add Junction"}
          </button>
        </form>

        <div className="rounded-xl bg-white p-6 shadow">
          <h2 className="mb-5 text-lg font-bold text-slate-900">Junction Table</h2>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[620px] text-left">
              <thead>
                <tr className="border-b border-slate-200 text-sm font-semibold text-slate-500">
                  <th className="px-4 py-3">#</th>
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">IP Address</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {junctions.map((junction, index) => (
                  <tr key={junction.id || junction._id || junction.junction_id || index} className="border-b border-slate-100">
                    <td className="px-4 py-4 text-sm text-slate-600">{index + 1}</td>
                    <td className="px-4 py-4 text-sm font-semibold text-slate-900">{junction.name || junction.junction_name || "-"}</td>
                    <td className="px-4 py-4 text-sm text-slate-600">{junction.ip_address || junction.ip || "-"}</td>
                    <td className="px-4 py-4">
                      <div className="flex gap-2">
                        <button type="button" onClick={() => editJunction(junction)} className="rounded-lg bg-blue-50 p-2 text-blue-600 hover:bg-blue-100">
                          <Edit size={18} />
                        </button>
                        <button type="button" onClick={() => handleDelete(junction)} className="rounded-lg bg-red-50 p-2 text-red-600 hover:bg-red-100">
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {junctions.length === 0 && (
                  <tr>
                    <td colSpan="4" className="px-4 py-5 text-sm font-semibold text-slate-500">
                      No junctions found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Layout>
  );
}
