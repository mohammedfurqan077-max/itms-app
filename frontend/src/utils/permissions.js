const permissionAliases = {
  vip: ["vip"],
  setTime: ["set time", "set_time"]
};

function normalize(value) {
  return String(value || "").trim().toLowerCase();
}

export function getUserPermissions(user) {
  return Array.isArray(user?.permissions) ? user.permissions.map(normalize) : [];
}

export function hasPermission(user, key) {
  if (normalize(user?.role) === "admin") return true;

  const userPermissions = getUserPermissions(user);
  return (permissionAliases[key] || []).some((permission) => userPermissions.includes(permission));
}
