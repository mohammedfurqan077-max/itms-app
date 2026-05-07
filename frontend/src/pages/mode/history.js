import { useCallback, useEffect, useState } from "react";
import Layout from "@/components/Layout";
import PageLoadedMarker from "@/components/PageLoadedMarker";
import StatusMessage from "@/components/StatusMessage";
import { commandsApi } from "@/services/api";

function rowsFrom(data) {
  if (Array.isArray(data)) return data;
  return data?.items || data?.commands || data?.data || [];
}

function modeBadge(mode) {
  const value = mode || "-";
  return <span className="rounded-full bg-slate-200 px-3 py-1 text-xs font-bold text-slate-700">{value}</span>;
}

export default function ChangeModeHistoryPage() {
  const [commands, setCommands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);

  const loadCommands = useCallback(async () => {
    setMessage(null);
    try {
      const response = await commandsApi.list();
      setCommands(rowsFrom(response.data));
    } catch (error) {
      setMessage({ type: "error", text: error.response?.data?.detail || error.response?.data?.message || error.message || "Unable to load mode history." });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCommands();
  }, [loadCommands]);

  return (
    <Layout title="Change Mode History">
      <PageLoadedMarker />
      <StatusMessage message={message} />
      <div className="rounded-xl bg-white p-6 shadow">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[780px] text-left">
            <thead>
              <tr className="border-b border-slate-200 text-sm font-semibold text-slate-500">
                <th className="px-4 py-3">USER</th>
                <th className="px-4 py-3">ROLE</th>
                <th className="px-4 py-3">MODE TRANSITION</th>
                <th className="px-4 py-3">TIMESTAMP</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="4" className="px-4 py-5 text-sm font-semibold text-slate-500">
                    Loading history
                  </td>
                </tr>
              ) : commands.length === 0 ? (
                <tr>
                  <td colSpan="4" className="px-4 py-5 text-sm font-semibold text-slate-500">
                    No history found
                  </td>
                </tr>
              ) : (
                commands.map((command, index) => {
                  const fromMode = command.from_mode || command.previous_mode || "Circle_auto";
                  const toMode = command.to_mode || command.mode || command.command_type || "Yellow";
                  const finalMode = command.final_mode || command.next_mode || "Circle_auto";
                  return (
                    <tr key={command.id || command._id || command.timestamp || index} className="border-b border-slate-100">
                      <td className="px-4 py-4 text-sm font-semibold text-slate-900">{command.user || command.user_name || "-"}</td>
                      <td className="px-4 py-4 text-sm text-slate-600">{command.role || "-"}</td>
                      <td className="px-4 py-4">
                        <div className="flex items-center gap-2 text-sm">
                          {modeBadge(fromMode)}
                          <span className="font-bold text-slate-400">&rarr;</span>
                          {modeBadge(toMode)}
                          <span className="font-bold text-slate-400">&rarr;</span>
                          {modeBadge(finalMode)}
                        </div>
                      </td>
                      <td className="px-4 py-4 text-sm text-slate-600">
                        {command.timestamp ? new Date(command.timestamp).toLocaleString() : "-"}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  );
}
