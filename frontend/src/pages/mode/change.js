import { useState } from "react";
import AutoModeModal from "@/components/AutoModeModal";
import ConfirmModal from "@/components/ConfirmModal";
import Layout from "@/components/Layout";
import PageLoadedMarker from "@/components/PageLoadedMarker";
import SetTimeModal from "@/components/SetTimeModal";
import StatusMessage from "@/components/StatusMessage";
import VipModal from "@/components/VipModal";
import { controlApi } from "@/services/api";

export default function ChangeModePage() {
  const [message, setMessage] = useState(null);
  const [busy, setBusy] = useState(false);
  const [autoOpen, setAutoOpen] = useState(false);
  const [vipOpen, setVipOpen] = useState(false);
  const [setTimeOpen, setSetTimeOpen] = useState(false);
  const [pendingAction, setPendingAction] = useState(null);

  async function executePendingAction() {
    if (!pendingAction) return;

    setBusy(true);
    setMessage(null);
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
    <Layout title="Change Mode">
      <PageLoadedMarker />
      <StatusMessage message={message} />
      <div className="machine-panel mx-auto max-w-4xl p-6">
        <div className="grid gap-6 md:grid-cols-2">
          <button disabled={busy} onClick={() => setAutoOpen(true)} className="machine-btn machine-btn-auto disabled:opacity-60">
            AUTO
          </button>
          <button disabled={busy} onClick={() => setVipOpen(true)} className="machine-btn machine-btn-vip disabled:opacity-60">
            VIP
          </button>
          <button disabled={busy} onClick={() => setSetTimeOpen(true)} className="machine-btn machine-btn-manual disabled:opacity-60">
            SET TIME
          </button>
          <button
            disabled={busy}
            onClick={() =>
              setPendingAction({
                type: "switch_mode",
                mode: "blinker",
                label: "Blinker",
                confirmMessage: "Turn ON/OFF Blinker Mode?"
              })
            }
            className="machine-btn machine-btn-blinker disabled:opacity-60"
          >
            BLINKER
          </button>
        </div>
      </div>

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
    </Layout>
  );
}
