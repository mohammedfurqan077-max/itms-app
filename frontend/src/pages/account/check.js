import { useState } from "react";
import AccountForm from "@/components/AccountForm";
import Layout from "@/components/Layout";
import PageLoadedMarker from "@/components/PageLoadedMarker";
import StatusMessage from "@/components/StatusMessage";
import { usersApi } from "@/services/api";

const initialAccount = {
  id: "",
  name: "Admin User",
  email: "admin@itms.com",
  password: "password123",
  role: "Admin",
  status: "Active",
  permissions: ["Set Time", "Auto Circle Auto", "VIP"]
};

export default function CheckAccountPage() {
  const [account, setAccount] = useState(initialAccount);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      await usersApi.update(account.id || account.email, {
        name: account.name,
        email: account.email,
        password: account.password,
        role: account.role.toLowerCase(),
        status: account.status.toLowerCase(),
        permissions: account.permissions
      });
      setMessage({ type: "success", text: "Account updated successfully." });
    } catch (error) {
      setMessage({ type: "error", text: error.response?.data?.detail || error.response?.data?.message || error.message || "Unable to update account." });
    } finally {
      setLoading(false);
    }
  }

  return (
    <Layout title="Check Account">
      <PageLoadedMarker />
      <StatusMessage message={message} />
      <AccountForm value={account} onChange={setAccount} onSubmit={handleSubmit} buttonLabel="Update" loading={loading} />
    </Layout>
  );
}
