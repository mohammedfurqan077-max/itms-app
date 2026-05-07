import { useCallback, useEffect, useMemo, useState } from "react";
import JawanLayout from "@/components/JawanLayout";
import StatusMessage from "@/components/StatusMessage";
import { dashboardApi, junctionsApi } from "@/services/api";
import { getRecentActions } from "@/services/actionStore";
import { useRealtime } from "@/hooks/useRealtime";

function readRows(data) {
  if (Array.isArray(data)) return data;
  return data?.items || data?.junctions || data?.data || [];
}

export default function UserDashboardContent() {
  const [junction, setJunction] = useState(null);
  const [systemState, setSystemState] = useState(null);
  const [actions, setActions] = useState([]);
  const [message, setMessage] = useState(null);

  const applyRealtime = useCallback((payload) => {
    setSystemState((current) => ({ ...(current || {}), mode: payload.mode || current?.mode, status: payload.status || current?.status }));
    setActions(getRecentActions());
  }, []);

  useRealtime({
    onModeChange: applyRealtime,
    onVipTriggered: applyRealtime,
    onSystemAlert: applyRealtime
  });

  useEffect(() => {
    setActions(getRecentActions());

    async function loadDashboard() {
      try {
        const [junctionResponse, stateResponse] = await Promise.all([junctionsApi.list(), dashboardApi.getSystemState()]);
        setJunction(readRows(junctionResponse.data)[0] || null);
        setSystemState(stateResponse.data);
      } catch (error) {
        setMessage({ type: "error", text: error.response?.data?.detail || error.response?.data?.message || error.message || "Unable to load dashboard." });
      }
    }

    loadDashboard();
  }, []);

  const cards = useMemo(
    () => [
      { label: "Junction Name", value: junction?.name || junction?.junction_name || "Not assigned" },
      { label: "Status", value: systemState?.status || junction?.status || "Running" },
      { label: "Mode", value: systemState?.mode || systemState?.current_mode || junction?.mode || "Auto" },
      { label: "Temperature", value: junction?.temperature ? `${junction.temperature} C` : systemState?.temperature ? `${systemState.temperature} C` : "N/A" }
    ],
    [junction, systemState]
  );

  return (
    <JawanLayout title="Dashboard">
      <StatusMessage message={message} />
      <section className="grid gap-3 sm:grid-cols-2">
        {cards.map((card) => (
          <div key={card.label} className="machine-card p-5">
            <p className="text-xs font-black uppercase tracking-wide text-cyan-300/80">{card.label}</p>
            <p className="mt-2 text-3xl font-black text-white">{card.value}</p>
          </div>
        ))}
      </section>

      <section className="machine-panel mt-5 p-5">
        <h2 className="mb-4 text-lg font-black text-white">Recent Actions</h2>
        <div className="space-y-3">
          {actions.length === 0 ? (
            <p className="text-sm font-semibold text-slate-400">No recent actions</p>
          ) : (
            actions.map((action) => (
              <div key={action.id} className="machine-card flex items-center justify-between px-4 py-3">
                <span className="text-sm font-bold text-white">{action.label}</span>
                <time className="text-xs font-semibold text-slate-400">{new Date(action.timestamp).toLocaleTimeString()}</time>
              </div>
            ))
          )}
        </div>
      </section>
    </JawanLayout>
  );
}
