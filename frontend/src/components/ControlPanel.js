import { useState } from "react";
import AutoModeModal from "@/components/AutoModeModal";
import ConfirmModal from "@/components/ConfirmModal";
import SetTimeModal from "@/components/SetTimeModal";
import VipModal from "@/components/VipModal";
import { controlApi } from "@/services/api";

export default function ControlPanel({ onCommandSuccess }) {
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [autoOpen, setAutoOpen] = useState(false);
  const [vipOpen, setVipOpen] = useState(false);
  const [setTimeOpen, setSetTimeOpen] = useState(false);
  const [pendingAction, setPendingAction] = useState(null);

  async function executePendingAction() {
    if (!pendingAction) return;

    setBusy(true);
    setFeedback(null);
    try {
      if (pendingAction.type === "switch_mode") {
        await controlApi.switchMode({ mode: pendingAction.mode });
      }
      if (pendingAction.type === "vip") {
        await controlApi.vipOverride({ lane: pendingAction.lane });
      }
      if (pendingAction.type === "manual_times") {
        await controlApi.setManualTimes(pendingAction.times);
      }

      setFeedback({ type: "success", message: `${pendingAction.label} completed.` });
      onCommandSuccess?.(pendingAction);
      setPendingAction(null);
      setAutoOpen(false);
      setVipOpen(false);
      setSetTimeOpen(false);
    } catch (error) {
      setFeedback({ type: "error", message: error.response?.data?.detail || error.response?.data?.message || error.message || "Command failed." });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <button type="button" disabled={busy} onClick={() => setAutoOpen(true)} className="machine-btn machine-btn-auto min-h-20 text-xl disabled:opacity-60">
          AUTO
        </button>
        <button type="button" disabled={busy} onClick={() => setVipOpen(true)} className="machine-btn machine-btn-vip min-h-20 text-xl disabled:opacity-60">
          VIP
        </button>
        <button type="button" disabled={busy} onClick={() => setSetTimeOpen(true)} className="machine-btn machine-btn-manual min-h-20 text-xl disabled:opacity-60">
          SET TIME
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() =>
            setPendingAction({
              type: "switch_mode",
              mode: "blinker",
              label: "Blinker",
              confirmMessage: "Turn ON/OFF Blinker Mode?"
            })
          }
          className="machine-btn machine-btn-blinker min-h-20 text-xl disabled:opacity-60"
        >
          BLINKER
        </button>
      </div>

      {feedback && (
        <div
          role="alert"
          className={`rounded border px-4 py-3 text-sm font-bold ${
            feedback.type === "success" ? "border-emerald-200 bg-emerald-50 text-emerald-700" : "border-red-200 bg-red-50 text-red-700"
          }`}
        >
          {feedback.message}
        </div>
      )}

      <AutoModeModal
        open={autoOpen}
        onClose={() => setAutoOpen(false)}
        onContinue={({ mode, label }) =>
          setPendingAction({
            type: "switch_mode",
            mode,
            label,
            confirmMessage: `Switch to ${label}?`
          })
        }
      />
      <VipModal
        open={vipOpen}
        onClose={() => setVipOpen(false)}
        onContinue={(lane) =>
          setPendingAction({
            type: "vip",
            lane,
            label: `VIP LAN ${lane}`,
            confirmMessage: `Activate VIP on LAN ${lane}?`
          })
        }
      />
      <SetTimeModal
        open={setTimeOpen}
        onClose={() => setSetTimeOpen(false)}
        onSave={(times) =>
          setPendingAction({
            type: "manual_times",
            times,
            label: "Set Time",
            confirmMessage: "Save manual timings?"
          })
        }
      />
      <ConfirmModal
        open={Boolean(pendingAction)}
        message={pendingAction?.confirmMessage}
        loading={busy}
        onCancel={() => setPendingAction(null)}
        onConfirm={executePendingAction}
      />
    </div>
  );
}
