import { useState } from "react";

const autoModes = [
  { label: "Jump Auto", value: "auto_jump" },
  { label: "Circle Auto", value: "auto_circle" }
];

export default function AutoModeModal({ open, onClose, onContinue }) {
  const [mode, setMode] = useState("auto_jump");

  if (!open) return null;

  const selected = autoModes.find((item) => item.value === mode);

  return (
    <div className="machine-modal-backdrop fixed inset-0 z-30 grid place-items-center p-4">
      <form
        onSubmit={(event) => {
          event.preventDefault();
          onContinue({ mode, label: selected?.label || mode });
        }}
        className="machine-panel w-full max-w-md p-6"
      >
        <h2 className="mb-5 text-xl font-black text-white">Select Auto Mode</h2>
        <label className="block">
          <span className="mb-2 block text-sm font-bold text-slate-300">Auto Mode</span>
          <select
            value={mode}
            onChange={(event) => setMode(event.target.value)}
            className="machine-input h-14 w-full rounded-xl px-4 text-lg font-bold outline-none focus:border-blue-500"
          >
            {autoModes.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
        </label>
        <div className="mt-6 grid grid-cols-2 gap-3">
          <button type="button" onClick={onClose} className="machine-btn machine-btn-cancel min-h-14 px-4 py-3 text-base">
            Cancel
          </button>
          <button className="machine-btn machine-btn-primary min-h-14 px-4 py-3 text-base">Continue</button>
        </div>
      </form>
    </div>
  );
}
