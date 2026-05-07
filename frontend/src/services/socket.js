import { io } from "socket.io-client";

const SOCKET_URL =
  process.env.NEXT_PUBLIC_SOCKET_URL ||
  (process.env.NODE_ENV === "production" ? "" : "http://localhost:8000");

let socket;

export function getSocket() {
  if (typeof window === "undefined") return null;
  if (!SOCKET_URL) {
    return null;
  }

  if (!socket) {
    socket = io(SOCKET_URL, {
      autoConnect: false,
      transports: ["websocket"],
      auth: (callback) => {
        callback({
          token: localStorage.getItem("itms_token")
        });
      }
    });
  }

  return socket;
}

export function connectSocket() {
  const activeSocket = getSocket();
  if (activeSocket && !activeSocket.connected) {
    activeSocket.connect();
  }
  return activeSocket;
}

export function disconnectSocket() {
  if (socket?.connected) {
    socket.disconnect();
  }
}
