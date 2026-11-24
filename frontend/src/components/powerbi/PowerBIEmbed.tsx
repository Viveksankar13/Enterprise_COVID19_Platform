import React from "react";
import { useQuery } from "@tanstack/react-query";
import api from "../../services/api";
import { Card } from "../ui/Card";
import { Badge } from "../ui/Badge";
import { Spinner } from "../ui/Spinner";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { Layout, Shield, ShieldCheck } from "lucide-react";

export const PowerBIEmbed: React.FC = () => {
  const { data: embedInfo, isLoading, error } = useQuery({
    queryKey: ["powerbiEmbed"],
    queryFn: async () => {
      const res = await api.get("/powerbi/embed-info");
      return res.data;
    },
  });

  if (isLoading) {
    return (
      <div className="h-[60vh] flex flex-col items-center justify-center gap-3">
        <Spinner size="lg" />
        <span className="text-sm text-muted-foreground animate-pulse">
          Generating Power BI secure active token...
        </span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-[60vh] flex flex-col items-center justify-center text-center p-6 text-rose-400">
        <Shield size={48} className="mb-2" />
        <h2 className="text-xl font-bold">Power BI Token Generation Failed</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Verify Azure AD Tenant settings and client secrets inside app configuration.
        </p>
      </div>
    );
  }

  const isSimulated = embedInfo?.isSimulated;

  // Mock charts to display when running in simulated mode
  const mockChartData = [
    { name: "Hospital Beds", Actual: 85, Capacity: 100 },
    { name: "ICU Ventilators", Actual: 62, Capacity: 80 },
    { name: "Clinical Staff", Actual: 90, Capacity: 95 },
    { name: "Oxygen Supply", Actual: 78, Capacity: 100 },
  ];

  return (
    <div className="space-y-6">
      {/* Power BI Status Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-muted/20 border border-border p-4 rounded-xl">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 text-primary rounded-lg">
            <Layout size={20} />
          </div>
          <div>
            <h3 className="text-sm font-bold text-foreground">Active Power BI Embed Session</h3>
            <p className="text-[10px] text-muted-foreground">
              {isSimulated
                ? "Running Developer Simulation Mode (Bypass active)"
                : "Active Azure AD Session (Token secured)"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isSimulated ? (
            <Badge variant="warning">Simulated Session</Badge>
          ) : (
            <Badge variant="success" className="flex items-center gap-1">
              <ShieldCheck size={12} /> Secure Connection
            </Badge>
          )}
        </div>
      </div>

      {/* Embedded IFrame / Visualizer Viewport */}
      {isSimulated ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Mock reporting sidebar info */}
          <Card className="lg:col-span-1 p-5 flex flex-col justify-between">
            <div className="space-y-4">
              <h4 className="font-bold text-foreground">Sovereign Capacity Stats</h4>
              <p className="text-xs text-muted-foreground leading-relaxed">
                This simulated report displays real-time resource allocations across active sovereign states. In production, this pane houses the live Power BI Canvas iframe.
              </p>
            </div>
            <div className="p-3 bg-primary/5 border border-primary/20 rounded-lg text-[10px] text-muted-foreground mt-6 leading-relaxed">
              Power BI Client SDK will automatically load the iframe target at path 
              <code className="block bg-black/30 p-1.5 rounded mt-1 font-mono text-[9px] truncate">
                {embedInfo?.embedUrl}
              </code>
            </div>
          </Card>

          {/* Mock charts showing what PBI would render */}
          <Card className="lg:col-span-2 p-5 space-y-4">
            <div className="flex justify-between items-center">
              <h4 className="text-sm font-bold text-foreground">Resource Inpatient Load</h4>
              <span className="text-xs text-muted-foreground">Capacity percentages</span>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={mockChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#f8fafc" }}
                  />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Bar dataKey="Actual" fill="#3b82f6" name="Used Units" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Capacity" fill="#94a3b8" fillOpacity={0.2} name="Total Capacity" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>
      ) : (
        <Card hoverable={false} className="p-0 overflow-hidden h-[70vh] border border-border">
          <iframe
            src={`${embedInfo.embedUrl}&navContentPaneEnabled=false`}
            className="w-full h-full border-0"
            allowFullScreen={true}
            title="COVID-19 Power BI Embedded Report"
          />
        </Card>
      )}
    </div>
  );
};
