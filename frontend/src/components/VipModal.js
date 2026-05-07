import { useState } from "react";

export default function VipModal({ open, onClose, onContinue }) {
  const [lane, setLane] = useState("1");

  if (!open) return null;

  return (
    <div className="machine-modal-backdrop fixed inset-0 z-30 grid place-items-end p-4 sm:place-items-center">
      <form
        onSubmit={(event) => {
          event.preventDefault();
          onContinue(Number(lane));
        }}
        className="machine-panel w-full max-w-md p-5"
      >
        <h2 className="mb-5 text-xl font-black text-white">Activate VIP Mode</h2>
        <label className="block">
          <span className="mb-2 block text-sm font-bold text-slate-300">Select LAN</span>
          <select
            value={lane}
            onChange={(event) => setLane(event.target.value)}
            className="machine-input h-14 w-full rounded-xl px-4 text-lg font-bold outline-none focus:border-blue-500"
          >
            <option value="1">LAN 1</option>
            <option value="2">LAN 2</option>
            <option value="3">LAN 3</option>
            <option value="4">LAN 4</option>
          </select>
        </label>
        <div className="mt-6 grid grid-cols-2 gap-3">
          <button type="button" onClick={onClose} className="machine-btn machine-btn-cancel min-h-14 px-4 py-3 text-base">
            Cancel
          </button>
          <button className="machine-btn machine-btn-primary min-h-14 px-4 py-3 text-base">
            Continue
          </button>
        </div>
      </form>
    </div>
  );
}
