import { useState } from "react";
import AutoModeModal from "@/components/AutoModeModal";
import ConfirmModal from "@/components/ConfirmModal";
import JawanLayout from "@/components/JawanLayout";
import SetTimeModal from "@/components/SetTimeModal";
import StatusMessage from "@/components/StatusMessage";
import VipModal from "@/components/VipModal";
import { useAuth } from "@/context/AuthContext";
import { controlApi } from "@/services/api";
import { addRecentAction } from "@/services/actionStore";
import { hasPermission } from "@/utils/permissions";

export default function UserControlContent() {
  const { user } = useAuth();
  const [message, setMessage] = useState(null);
  const [busy, setBusy] = useState(false);
  const [autoOpen, setAutoOpen] = useState(false);
  const [vipOpen, setVipOpen] = useState(false);
  const [setTimeOpen, setSetTimeOpen] = useState(false);
  const [pendingAction, setPendingAction] = useState(null);

  const canSetTime = hasPermission(user, "setTime");
  const canVip = hasPermission(user, "vip");

  async function executePendingAction() {
    if (!pendingAction) return;

    setBusy(true);
    setMessage(null);
    try {
      if (pendingAction.type === "switch_mode") await controlApi.switchMode({ mode: pendingAction.mode });
      if (pendingAction.type === "vip") await controlApi.vipOverride({ lane: pendingAction.lane });
      if (pendingAction.type === "manual_times") await controlApi.setManualTimes(pendingAction.times);

      addRecentAction(pendingAction.label);
      setMessage({ type: "success", text: `${pendingAction.label} completed.` });
      setPendingAction(null);
      setAutoOpen(false);
      setVipOpen(false);
      setSetTimeOpen(false);
    } catch (error) {
      setMessage({ type: "error", text: error.response?.data?.detail || error.response?.data?.message || error.message || `${pendingAction.label} failed.` });
    } finally {
      setBusy(false);
    }
  }

  return (
    <JawanLayout title="Control">
      <StatusMessage message={message} />
      <div className="grid gap-4">
        <button type="button" disabled={busy} onClick={() => setAutoOpen(true)} className="machine-btn machine-btn-auto disabled:opacity-60">
          AUTO
        </button>
        {canVip ? (
          <button type="button" disabled={busy} onClick={() => setVipOpen(true)} className="machine-btn machine-btn-vip disabled:opacity-60">
            VIP
          </button>
        ) : null}
        <button
          type="button"
          disabled={busy}
          onClick={() => setPendingAction({ type: "switch_mode", mode: "blinker", label: "Blinker", confirmMessage: "Turn ON/OFF Blinker Mode?" })}
          className="machine-btn machine-btn-blinker disabled:opacity-60"
        >
          BLINKER
        </button>
        <button
          type="button"
          disabled={!canSetTime || busy}
          onClick={() => setSetTimeOpen(true)}
          className="machine-btn machine-btn-manual disabled:cursor-not-allowed disabled:opacity-60"
        >
          SET TIME
        </button>
      </div>

      {!canSetTime ? <p className="mt-4 text-center text-sm font-bold text-slate-400">Set Time permission not assigned</p> : null}

      <AutoModeModal
        open={autoOpen}
        onClose={() => setAutoOpen(false)}
        onContinue={({ mode, label }) => setPendingAction({ type: "switch_mode", mode, label, confirmMessage: `Switch to ${label}?` })}
      />
      <VipModal open={vipOpen} onClose={() => setVipOpen(false)} onContinue={(lane) => setPendingAction({ type: "vip", lane, label: `VIP LAN ${lane}`, confirmMessage: `Activate VIP on LAN ${lane}?` })} />
      <SetTimeModal open={setTimeOpen} onClose={() => setSetTimeOpen(false)} onSave={(times) => setPendingAction({ type: "manual_times", times, label: "Set Time", confirmMessage: "Save manual timings?" })} />
      <ConfirmModal open={Boolean(pendingAction)} message={pendingAction?.confirmMessage} loading={busy} onCancel={() => setPendingAction(null)} onConfirm={executePendingAction} />
    </JawanLayout>
  );
}
