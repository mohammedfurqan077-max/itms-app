import { useState } from "react";

const defaultTimes = { lane1_time: 30, lane2_time: 30, lane3_time: 30, lane4_time: 30 };

export default function SetTimeModal({ open, onClose, onSave }) {
  const [times, setTimes] = useState(defaultTimes);

  if (!open) return null;

  function updateLane(lane, value) {
    setTimes((current) => ({ ...current, [lane]: Number(value) }));
  }

  return (
    <div className="machine-modal-backdrop fixed inset-0 z-30 grid place-items-end p-4 sm:place-items-center">
      <form
        onSubmit={(event) => {
          event.preventDefault();
          onSave(times);
        }}
        className="machine-panel w-full max-w-md p-5"
      >
        <h2 className="mb-5 text-xl font-black text-white">Set Time</h2>
        <div className="grid gap-4">
          {[1, 2, 3, 4].map((lane) => (
            <label key={lane} className="block">
              <span className="mb-2 block text-sm font-bold text-slate-300">LAN {lane} Time</span>
              <input
                type="number"
                min="5"
                max="300"
                value={times[`lane${lane}_time`]}
                onChange={(event) => updateLane(`lane${lane}_time`, event.target.value)}
                className="machine-input h-14 w-full rounded-xl px-4 text-lg font-bold outline-none focus:border-blue-500"
              />
            </label>
          ))}
        </div>
        <div className="mt-6 grid grid-cols-2 gap-3">
          <button type="button" onClick={onClose} className="machine-btn machine-btn-cancel min-h-14 px-4 py-3 text-base">
            Cancel
          </button>
          <button className="machine-btn machine-btn-primary min-h-14 px-4 py-3 text-base">
            Save Time
          </button>
        </div>
      </form>
    </div>
  );
}
