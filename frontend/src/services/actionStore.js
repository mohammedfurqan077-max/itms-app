const STORAGE_KEY = "itms_jawan_actions";

export function getRecentActions() {
  if (typeof window === "undefined") return [];

  try {
    const actions = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    return Array.isArray(actions) ? actions : [];
  } catch {
    localStorage.removeItem(STORAGE_KEY);
    return [];
  }
}

export function addRecentAction(label, status = "success") {
  if (typeof window === "undefined") return [];

  const action = {
    id: `${Date.now()}`,
    label,
    status,
    timestamp: new Date().toISOString()
  };
  const next = [action, ...getRecentActions()].slice(0, 12);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  return next;
}
