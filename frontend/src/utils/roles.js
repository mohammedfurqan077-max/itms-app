export function normalizeRole(role) {
  return String(role || "").trim().toLowerCase();
}

export function getRoleHome(role) {
  return normalizeRole(role) === "admin" ? "/admin/dashboard" : "/user/dashboard";
}
