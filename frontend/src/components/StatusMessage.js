export default function StatusMessage({ message }) {
  if (!message?.text) return null;

  return (
    <div
      role="alert"
      className={`mb-5 rounded-xl border px-4 py-3 text-sm font-semibold shadow-[4px_4px_12px_rgba(0,0,0,0.22)] ${
        message.type === "success" ? "border-emerald-400/30 bg-emerald-500/12 text-emerald-200" : "border-red-400/30 bg-red-500/12 text-red-200"
      }`}
    >
      {message.text}
    </div>
  );
}
