import { useEffect } from "react";
import { useRouter } from "next/router";
import { useAuth } from "@/context/AuthContext";
import { getRoleHome } from "@/utils/roles";

export default function RoleRedirect() {
  const router = useRouter();
  const { ready, isAuthenticated, role } = useAuth();

  useEffect(() => {
    if (!ready) return;
    router.replace(isAuthenticated ? getRoleHome(role) : "/login");
  }, [isAuthenticated, ready, role, router]);

  return null;
}
