import React from "react";
import { useQuery } from "@tanstack/react-query";
import api from "../../services/api";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Spinner } from "../../components/ui/Spinner";
import { UserCheck, ShieldAlert, Key, Shield } from "lucide-react";

export const UserManagement: React.FC = () => {
  // Fetch users list
  const { data: users, isLoading, error } = useQuery({
    queryKey: ["usersList"],
    queryFn: async () => {
      const res = await api.get("/admin/users");
      return res.data;
    },
  });

  return (
    <div className="space-y-8">
      {/* Title */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground flex items-center gap-3">
            <UserCheck className="text-primary" size={28} />
            User Account Security Control
          </h1>
          <p className="text-muted-foreground mt-1">
            Audit system user accounts, roles, access levels, and authentication parameters.
          </p>
        </div>
      </div>

      {isLoading ? (
        <div className="h-[40vh] flex items-center justify-center">
          <Spinner size="lg" />
        </div>
      ) : error ? (
        <Card className="p-8 border-l-4 border-l-rose-500 bg-rose-500/5 text-rose-300">
          <div className="flex gap-3">
            <ShieldAlert size={24} className="shrink-0 text-rose-400" />
            <div>
              <h4 className="font-bold text-foreground">Access Denied / Failed to Load Users</h4>
              <p className="text-xs text-muted-foreground mt-1">
                Verify you are authenticated with an admin user account. Only admin credentials possess access privileges to retrieve user accounts listing.
              </p>
            </div>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {/* Active Users Table */}
          <Card hoverable={false} className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-sm font-bold text-foreground">Registered User Profiles</h3>
              <Badge variant="info">Active Directories</Badge>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-muted-foreground border-collapse">
                <thead>
                  <tr className="border-b border-border text-[10px] font-semibold text-foreground uppercase tracking-wider bg-muted/20">
                    <th className="py-3 px-4">Full Name</th>
                    <th className="py-3 px-4">Username</th>
                    <th className="py-3 px-4">Email</th>
                    <th className="py-3 px-4 text-center">Assigned Role</th>
                    <th className="py-3 px-4 text-center">Status</th>
                    <th className="py-3 px-4 text-right">Logins</th>
                    <th className="py-3 px-4">Last Authentication</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u: any) => (
                    <tr key={u.user_id} className="border-b border-border hover:bg-muted/15 transition-colors">
                      <td className="py-3.5 px-4 font-semibold text-foreground">
                        {u.full_name || "Platform Account"}
                      </td>
                      <td className="py-3.5 px-4 font-mono">{u.username}</td>
                      <td className="py-3.5 px-4 font-mono">{u.email}</td>
                      <td className="py-3.5 px-4 text-center">
                        <Badge variant={u.role?.name === "admin" ? "danger" : "neutral"} className="flex items-center gap-1 w-fit mx-auto">
                          {u.role?.name === "admin" ? <Key size={10} /> : <Shield size={10} />}
                          {u.role?.name || "viewer"}
                        </Badge>
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <Badge variant={u.is_active ? "success" : "neutral"}>
                          {u.is_active ? "Active" : "Disabled"}
                        </Badge>
                      </td>
                      <td className="py-3.5 px-4 text-right font-mono">{u.login_count}</td>
                      <td className="py-3.5 px-4 font-mono">
                        {u.last_login_at ? new Date(u.last_login_at).toLocaleString() : "Never authenticated"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
