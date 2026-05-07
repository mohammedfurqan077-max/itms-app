import ControlPanel from "@/components/ControlPanel";

const stateStyles = {
  online: "border-command-green text-command-green",
  offline: "border-command-red text-command-red",
  auto: "border-command-green text-command-green",
  manual: "border-command-yellow text-command-yellow",
  vip: "border-command-red text-command-red"
};

export default function JunctionCard({ junction, onCommandSuccess }) {
  const status = String(junction.status || "online").toLowerCase();
  const mode = String(junction.mode || "auto").toLowerCase();
  const stateClass = stateStyles[status === "offline" ? "offline" : mode] || stateStyles.auto;

  return (
    <article className={`rounded border bg-command-panel p-5 shadow-signal ${stateClass}`}>
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl font-black text-command-text">{junction.name || junction.code || "Junction"}</h3>
          <p className="mt-1 text-sm font-bold uppercase text-command-muted">{junction.location || junction.area || "Live control"}</p>
        </div>
        <div className={`rounded border px-3 py-1 text-sm font-black uppercase ${stateClass}`}>{status === "offline" ? "offline" : mode}</div>
      </div>
      <ControlPanel junction={junction} onCommandSuccess={onCommandSuccess} />
    </article>
  );
}
