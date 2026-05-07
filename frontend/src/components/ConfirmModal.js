export default function ConfirmModal({ open, title = "Confirm Action", message, loading, onCancel, onConfirm }) {
  if (!open) return null;

  return (
    <div className="machine-modal-backdrop fixed inset-0 z-40 grid place-items-center p-4">
      <div className="machine-panel w-full max-w-md p-6">
        <h2 className="text-xl font-black text-white">{title}</h2>
        <p className="mt-4 text-base font-semibold text-slate-300">{message}</p>
        <div className="mt-6 grid grid-cols-2 gap-3">
          <button type="button" onClick={onCancel} disabled={loading} className="machine-btn machine-btn-cancel min-h-14 px-4 py-3 text-base">
            Cancel
          </button>
          <button type="button" onClick={onConfirm} disabled={loading} className="machine-btn machine-btn-primary min-h-14 px-4 py-3 text-base disabled:opacity-60">
            {loading ? "Working" : "Confirm"}
          </button>
        </div>
      </div>
    </div>
  );
}
