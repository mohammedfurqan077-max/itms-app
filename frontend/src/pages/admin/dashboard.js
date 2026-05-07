import AdminLayout from "@/components/AdminLayout";
import PageLoadedMarker from "@/components/PageLoadedMarker";

export default function AdminDashboardPage() {
  return (
    <AdminLayout title="Dashboard">
      <PageLoadedMarker />
      <div className="machine-card p-6">
        <p className="text-4xl font-black text-white">Admin</p>
        <p className="mt-2 text-sm font-semibold text-slate-300">Dashboard loaded.</p>
      </div>
    </AdminLayout>
  );
}
