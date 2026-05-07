import { useMemo } from "react";
import L from "leaflet";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import ControlPanel from "@/components/ControlPanel";

const modeColors = {
  vip: "#ff4d4d",
  manual: "#ffd447",
  auto: "#1fd16b",
  offline: "#89949a"
};

function markerColor(junction) {
  if (String(junction.status || "").toLowerCase() === "offline") return modeColors.offline;
  return modeColors[String(junction.mode || "auto").toLowerCase()] || modeColors.auto;
}

function makeIcon(color) {
  return L.divIcon({
    className: "",
    html: `<div class="marker-dot" style="background:${color};color:${color}"></div>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
    popupAnchor: [0, -10]
  });
}

export default function TrafficMap({ junctions, onCommandSuccess }) {
  const center = useMemo(() => {
    const first = junctions.find((junction) => junction.latitude || junction.lat);
    return first ? [Number(first.latitude || first.lat), Number(first.longitude || first.lng)] : [28.6139, 77.209];
  }, [junctions]);

  return (
    <div className="h-[calc(100vh-8.5rem)] overflow-hidden rounded border border-command-line shadow-signal">
      <MapContainer center={center} zoom={12} scrollWheelZoom className="h-full w-full">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {junctions.map((junction) => {
          const lat = Number(junction.latitude || junction.lat);
          const lng = Number(junction.longitude || junction.lng);
          if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;
          const id = junction.id || junction._id || junction.junction_id || `${lat}-${lng}`;

          return (
            <Marker key={id} position={[lat, lng]} icon={makeIcon(markerColor(junction))}>
              <Popup minWidth={330}>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-black text-command-text">{junction.name || "Junction"}</h3>
                    <p className="mt-1 text-sm font-bold uppercase text-command-muted">
                      {String(junction.status || "online")} / {String(junction.mode || "auto")}
                    </p>
                  </div>
                  <ControlPanel junction={junction} onCommandSuccess={onCommandSuccess} />
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
