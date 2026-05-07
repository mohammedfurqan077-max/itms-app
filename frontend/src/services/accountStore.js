const STORAGE_KEY = "itms_created_accounts";

export function getStoredAccounts() {
  if (typeof window === "undefined") return [];

  try {
    const accounts = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    return Array.isArray(accounts) ? accounts : [];
  } catch {
    localStorage.removeItem(STORAGE_KEY);
    return [];
  }
}

export function saveStoredAccount(account) {
  if (typeof window === "undefined") return;

  const current = getStoredAccounts();
  const nextAccount = {
    id: account.id || account.email || `${Date.now()}`,
    name: account.name,
    email: account.email,
    role: account.role,
    status: account.status,
    permissions: account.permissions || []
  };
  const withoutDuplicate = current.filter((item) => item.email !== nextAccount.email);
  localStorage.setItem(STORAGE_KEY, JSON.stringify([nextAccount, ...withoutDuplicate]));
}
