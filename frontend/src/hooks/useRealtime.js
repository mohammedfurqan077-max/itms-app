import { useCallback, useEffect, useState } from "react";
import { connectSocket } from "@/services/socket";

function toFeedItem(type, payload) {
  return {
    id: `${type}-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    type,
    payload,
    timestamp: payload?.timestamp || new Date().toISOString()
  };
}

export function useRealtime({ enabled = true, onModeChange, onVipTriggered, onSystemAlert } = {}) {
  const [feed, setFeed] = useState([]);
  const [connected, setConnected] = useState(false);

  const pushFeed = useCallback((item) => {
    setFeed((current) => [item, ...current].slice(0, 40));
  }, []);

  useEffect(() => {
    if (!enabled) return undefined;

    const socket = connectSocket();
    if (!socket) return undefined;

    const handleConnect = () => setConnected(true);
    const handleDisconnect = () => setConnected(false);
    const handleModeChange = (payload) => {
      pushFeed(toFeedItem("mode_change", payload));
      onModeChange?.(payload);
    };
    const handleVipTriggered = (payload) => {
      pushFeed(toFeedItem("vip_triggered", payload));
      onVipTriggered?.(payload);
    };
    const handleSystemAlert = (payload) => {
      pushFeed(toFeedItem("system_alert", payload));
      onSystemAlert?.(payload);
    };

    socket.on("connect", handleConnect);
    socket.on("disconnect", handleDisconnect);
    socket.on("mode_change", handleModeChange);
    socket.on("vip_triggered", handleVipTriggered);
    socket.on("system_alert", handleSystemAlert);

    setConnected(socket.connected);

    return () => {
      socket.off("connect", handleConnect);
      socket.off("disconnect", handleDisconnect);
      socket.off("mode_change", handleModeChange);
      socket.off("vip_triggered", handleVipTriggered);
      socket.off("system_alert", handleSystemAlert);
    };
  }, [enabled, onModeChange, onSystemAlert, onVipTriggered, pushFeed]);

  return { feed, connected, pushFeed };
}
