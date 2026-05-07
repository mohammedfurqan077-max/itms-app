import { useState } from "react";
import AccountForm from "@/components/AccountForm";
import Layout from "@/components/Layout";
import PageLoadedMarker from "@/components/PageLoadedMarker";
import StatusMessage from "@/components/StatusMessage";
import { authApi } from "@/services/api";
import { saveStoredAccount } from "@/services/accountStore";

const emptyAccount = {
  name: "",
  email: "",
  password: "",
  role: "Admin",
  status: "Active",
  permissions: []
};

function toPayload(account) {
  const payload = {
    name: account.name,
    email: account.email,
    password: account.password,
    role: account.role.toLowerCase(),
    status: account.status.toLowerCase()
  };

  if (account.role === "Jawan") {
    payload.permissions = account.permissions;
  }

  return payload;
}

export default function NewAccountPage() {
  const [account, setAccount] = useState(emptyAccount);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      const response = await authApi.register(toPayload(account));
      saveStoredAccount({
        ...account,
        id: response.data?.user?.id || response.data?.id || account.email
      });
      setMessage({ type: "success", text: "Account saved successfully." });
      setAccount(emptyAccount);
    } catch (error) {
      setMessage({ type: "error", text: error.response?.data?.detail || error.response?.data?.message || error.message || "Unable to save account." });
    } finally {
      setLoading(false);
    }
  }

  return (
    <Layout title="New Account Add">
      <PageLoadedMarker />
      <StatusMessage message={message} />
      <AccountForm value={account} onChange={setAccount} onSubmit={handleSubmit} buttonLabel="Save" loading={loading} />
    </Layout>
  );
}
