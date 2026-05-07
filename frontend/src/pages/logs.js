import { useCallback, useEffect, useState } from "react";
import Layout from "@/components/Layout";
import { commandsApi } from "@/services/api";

const statusStyles = {
  success: "border-command-green text-command-green",
  completed: "border-command-green text-command-green",
  failed: "border-command-red text-command-red",
  error: "border-command-red text-command-red",
  pending: "border-command-yellow text-command-yellow"
};

export default function LogsPage() {
  const [commands, setCommands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadCommands = useCallback(async () => {
    setError("");
    try {
      const response = await commandsApi.list();
      setCommands(Array.isArray(response.data) ? response.data : response.data?.items || []);
    } catch (requestError) {
      setError(requestError.response?.data?.message || requestError.message || "Unable to load commands");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCommands();
  }, [loadCommands]);

  return (
    <Layout title="Command Logs" onModeChange={loadCommands} onVipTriggered={loadCommands} onSystemAlert={loadCommands}>
      {error && (
        <div role="alert" className="mb-5 rounded border border-command-red/60 bg-command-red/10 px-4 py-3 text-base font-bold text-command-red">
          {error}
        </div>
      )}

      {loading ? (
        <div className="rounded border border-command-line bg-command-panel p-6 text-lg font-black">Loading command history</div>
      ) : (
        <section className="space-y-3">
          {commands.length === 0 ? (
            <div className="rounded border border-command-line bg-command-panel p-6 text-lg font-black text-command-muted">No command logs found</div>
          ) : (
            commands.map((command) => {
              const status = String(command.status || "pending").toLowerCase();
              return (
                <article key={command.id || command._id || command.timestamp} className="rounded border border-command-line bg-command-panel p-5 shadow-signal">
                  <div className="flex flex-wrap items-center gap-4">
                    <div className="min-w-0 flex-1">
                      <p className="text-xl font-black text-command-text">{String(command.command_type || command.type || "command").toUpperCase()}</p>
                      <time className="mt-1 block text-sm font-bold text-command-muted">
                        {command.timestamp ? new Date(command.timestamp).toLocaleString() : "No timestamp"}
                      </time>
                    </div>
                    <span className={`rounded border px-4 py-2 text-sm font-black uppercase ${statusStyles[status] || statusStyles.pending}`}>
                      {status}
                    </span>
                  </div>
                </article>
              );
            })
          )}
        </section>
      )}
    </Layout>
  );
}
