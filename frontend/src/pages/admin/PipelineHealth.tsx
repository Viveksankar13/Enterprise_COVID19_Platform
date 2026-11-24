import React from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import api from "../../services/api";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { Spinner } from "../../components/ui/Spinner";
import { HardDrive, Server, RefreshCw, Activity, CheckCircle, Database } from "lucide-react";

export const PipelineHealth: React.FC = () => {
  // Fetch database pool details
  const { data: dbPool, isLoading: dbLoading, refetch: refetchPool } = useQuery({
    queryKey: ["dbPoolStats"],
    queryFn: async () => {
      const res = await api.get("/admin/db-pool");
      return res.data;
    },
  });

  // Fetch Health service status
  const { data: health, isLoading: healthLoading, refetch: refetchHealth } = useQuery({
    queryKey: ["apiHealthStatus"],
    queryFn: async () => {
      const res = await api.get("/health");
      return res.data;
    },
  });

  // Invalidate cache mutation
  const clearCacheMutation = useMutation({
    mutationFn: async () => {
      const res = await api.post("/admin/cache/clear");
      return res.data;
    },
  });

  const handleClearCache = () => {
    clearCacheMutation.mutate();
  };

  const handleRefreshAll = () => {
    refetchPool();
    refetchHealth();
  };

  const isLoading = dbLoading || healthLoading;

  return (
    <div className="space-y-8">
      {/* Title */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground flex items-center gap-3">
            <HardDrive className="text-primary" size={28} />
            System Observability & Cache Console
          </h1>
          <p className="text-muted-foreground mt-1">
            Monitor API gateways health, connection pool sizing, and flush caching databases.
          </p>
        </div>
        <Button variant="outline" onClick={handleRefreshAll} className="flex items-center gap-2">
          <RefreshCw size={16} /> Refresh Observability
        </Button>
      </div>

      {isLoading ? (
        <div className="h-[40vh] flex items-center justify-center">
          <Spinner size="lg" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Services Status Cards */}
          <Card className="p-5 flex flex-col justify-between">
            <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
              <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
                <Server size={18} className="text-primary" /> Active Services Status
              </h3>
              <Badge variant={health?.status === "healthy" ? "success" : "danger"}>
                {health?.status || "UNKNOWN"}
              </Badge>
            </div>
            <div className="space-y-3.5 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">API Gateway Server</span>
                <span className="font-semibold text-emerald-400 flex items-center gap-1">
                  <CheckCircle size={14} /> ONLINE
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Database Schema Layer</span>
                <span
                  className={`font-semibold flex items-center gap-1 ${
                    health?.database === "healthy" ? "text-emerald-400" : "text-rose-400"
                  }`}
                >
                  <CheckCircle size={14} /> {health?.database?.toUpperCase() || "OFFLINE"}
                </span>
              </div>
            </div>
          </Card>

          {/* Database Pool Connection metrics */}
          <Card className="p-5 flex flex-col justify-between">
            <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
              <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
                <Database size={18} className="text-primary" /> DB Connection Pool Stats
              </h3>
              <Badge variant="info">SQLAlchemy 2.x</Badge>
            </div>
            <div className="space-y-3 text-xs">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Database Pool Size Limit</span>
                <span className="font-mono font-bold text-foreground">{dbPool?.pool_size}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Checked-in Connections</span>
                <span className="font-mono font-bold text-foreground">{dbPool?.checked_in}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Checked-out Active Connections</span>
                <span className="font-mono font-bold text-primary">{dbPool?.checked_out}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Pool Overflow Limit</span>
                <span className="font-mono font-bold text-foreground">{dbPool?.overflow}</span>
              </div>
            </div>
          </Card>

          {/* Caching control triggers */}
          <Card className="p-5 flex flex-col justify-between">
            <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
              <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
                <Activity size={18} className="text-primary" /> Redis Caching Console
              </h3>
              <Badge variant="info">In-memory Store</Badge>
            </div>
            <div className="space-y-4">
              <p className="text-xs text-muted-foreground leading-relaxed">
                Manually flushing the Redis cache invalidates all query pre-renders. The next API requests will compile fresh metrics from PostgreSQL tables.
              </p>
              <Button
                variant="danger"
                onClick={handleClearCache}
                isLoading={clearCacheMutation.isPending}
                className="w-full flex items-center justify-center gap-2 py-2 font-bold uppercase text-[10px] tracking-wider"
              >
                Flush Redis Cache keys
              </Button>
              {clearCacheMutation.isSuccess && (
                <div className="text-[10px] text-center text-emerald-400 font-semibold mt-1.5">
                  Cache keys flushed successfully!
                </div>
              )}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
