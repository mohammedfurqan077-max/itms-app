export default function PageLoadedMarker({ label = "Page Loaded" }) {
  return <div className="mb-4 rounded-xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-3 text-sm font-semibold text-cyan-200 shadow-[0_0_18px_rgba(34,211,238,0.12)]">{label}</div>;
}
