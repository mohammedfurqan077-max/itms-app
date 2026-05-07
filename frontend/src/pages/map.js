import dynamic from "next/dynamic";
import { useCallback, useEffect, useState } from "react";
import Layout from "@/components/Layout";
import { junctionsApi } from "@/services/api";

const TrafficMap = dynamic(() => import("@/components/TrafficMap"), {
  ssr: false,
  loading: () => <div className="rounded border border-command-line bg-command-panel p-6 text-lg font-black">Loading map</div>
});

export default function MapPage() {
  const [junctions, setJunctions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadJunctions = useCallback(async () => {
    setError("");
    try {
      const response = await junctionsApi.list();
      setJunctions(Array.isArray(response.data) ? response.data : response.data?.items || []);
    } catch (requestError) {
      setError(requestError.response?.data?.message || requestError.message || "Unable to load junctions");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadJunctions();
  }, [loadJunctions]);

  const applyRealtimeUpdate = useCallback((payload) => {
    setJunctions((current) =>
      current.map((junction) => {
        const id = junction.id || junction._id || junction.junction_id;
        if (String(id) !== String(payload.junction_id)) return junction;
        return { ...junction, ...payload, id };
      })
    );
  }, []);

  return (
    <Layout title="Live Map" onModeChange={applyRealtimeUpdate} onVipTriggered={(payload) => applyRealtimeUpdate({ ...payload, mode: "vip" })} onSystemAlert={loadJunctions}>
      {error && (
        <div role="alert" className="mb-5 rounded border border-command-red/60 bg-command-red/10 px-4 py-3 text-base font-bold text-command-red">
          {error}
        </div>
      )}

      {loading ? (
        <div className="rounded border border-command-line bg-command-panel p-6 text-lg font-black">Loading junctions</div>
      ) : (
        <TrafficMap junctions={junctions} onCommandSuccess={loadJunctions} />
      )}
    </Layout>
  );
}
