import { AlertTriangle, CarFront, RadioTower } from "lucide-react";

const styles = {
  mode_change: {
    label: "MODE",
    icon: RadioTower,
    color: "text-command-yellow",
    border: "border-command-yellow/50"
  },
  vip_triggered: {
    label: "VIP",
    icon: CarFront,
    color: "text-command-red",
    border: "border-command-red/50"
  },
  system_alert: {
    label: "ALERT",
    icon: AlertTriangle,
    color: "text-command-red",
    border: "border-command-red/50"
  }
};

function summarize(item) {
  const payload = item.payload || {};
  if (item.type === "mode_change") {
    return `${payload.junction_name || payload.junction_id || "Junction"} -> ${String(payload.mode || "updated").toUpperCase()}`;
  }
  if (item.type === "vip_triggered") {
    return payload.message || `VIP override at ${payload.junction_name || payload.junction_id || "junction"}`;
  }
  return payload.message || payload.alert || "System alert received";
}

export default function ActivityFeed({ feed = [], connected = false }) {
  return (
    <aside className="hidden h-full w-80 shrink-0 border-l border-command-line bg-command-panel xl:flex xl:flex-col">
      <div className="border-b border-command-line px-5 py-5">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-black text-command-text">Activity</h2>
          <span className={`rounded px-3 py-1 text-xs font-black ${connected ? "bg-command-green text-command-bg" : "bg-command-red text-command-bg"}`}>
            {connected ? "LIVE" : "OFFLINE"}
          </span>
        </div>
      </div>

      <div className="status-scroll flex-1 space-y-3 overflow-y-auto p-4">
        {feed.length === 0 ? (
          <div className="rounded border border-command-line bg-command-panelSoft p-4 text-sm font-semibold text-command-muted">
            Awaiting live events
          </div>
        ) : (
          feed.map((item) => {
            const config = styles[item.type] || styles.system_alert;
            const Icon = config.icon;
            return (
              <article key={item.id} className={`rounded border ${config.border} bg-command-panelSoft p-4`}>
                <div className="mb-2 flex items-center gap-2">
                  <Icon size={18} className={config.color} />
                  <span className={`text-xs font-black ${config.color}`}>{config.label}</span>
                  <time className="ml-auto text-xs font-semibold text-command-muted">
                    {new Date(item.timestamp).toLocaleTimeString()}
                  </time>
                </div>
                <p className="text-sm font-bold leading-5 text-command-text">{summarize(item)}</p>
              </article>
            );
          })
        )}
      </div>
    </aside>
  );
}
