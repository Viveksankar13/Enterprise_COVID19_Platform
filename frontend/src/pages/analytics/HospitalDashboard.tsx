import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "../../services/api";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Spinner } from "../../components/ui/Spinner";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Stethoscope, AlertOctagon } from "lucide-react";

export const HospitalDashboard: React.FC = () => {
  const [country, setCountry] = useState("USA");

  // Fetch active country listings
  const { data: countries } = useQuery({
    queryKey: ["countriesList"],
    queryFn: async () => {
      const res = await api.get("/countries", { params: { include_aggregates: false, limit: 250 } });
      return res.data;
    },
  });

  // Fetch Hospitalization History
  const { data: hospHistory, isLoading: hospLoading } = useQuery({
    queryKey: ["hospHistory", country],
    queryFn: async () => {
      const res = await api.get("/hospitalizations", {
        params: { iso_code: country },
      });
      return res.data;
    },
  });

  const loc = countries?.find((c: any) => c.iso_code === country)?.location || country;

  // Format historical area chart data
  const chartData = hospHistory
    ? hospHistory.map((d: any) => ({
        date: d.date,
        "ICU Patients / Million": Number(d.icu_patients_per_million) || 0,
        "Hospital Patients / Million": Number(d.hosp_patients_per_million) || 0,
      }))
    : [];

  return (
    <div className="space-y-8">
      {/* Title */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground flex items-center gap-3">
            <Stethoscope className="text-blue-400" size={28} />
            Clinical Capacity & Hospital Occupancy
          </h1>
          <p className="text-muted-foreground mt-1">
            Analyze ICU admissions, clinical patient loads, and health care delivery thresholds.
          </p>
        </div>
      </div>

      {/* Country Selector */}
      <Card className="p-6 max-w-sm">
        <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">
          Select Country Viewport
        </label>
        <select
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          className="w-full bg-muted/40 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all duration-200"
        >
          {countries &&
            countries.map((c: any) => (
              <option key={c.iso_code} value={c.iso_code} className="bg-slate-900">
                {c.location}
              </option>
            ))}
        </select>
      </Card>

      {/* Hospitalization Area Chart */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="text-sm font-bold text-foreground">Clinical Capacity Timeline: {loc}</h3>
            <p className="text-xs text-muted-foreground">ICU and hospital patients per million residents</p>
          </div>
          <Badge variant="info">Hospital Load</Badge>
        </div>

        {hospLoading ? (
          <div className="h-80 flex items-center justify-center">
            <Spinner />
          </div>
        ) : chartData.length === 0 ? (
          <div className="h-80 flex flex-col items-center justify-center text-center p-6 text-muted-foreground bg-muted/5 border border-border rounded-xl">
            <AlertOctagon className="text-amber-500 mb-2" size={32} />
            No clinical hospitalization records are currently reported for this country.
          </div>
        ) : (
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                <Tooltip
                  formatter={(val) => Number(val).toFixed(2)}
                  contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#f8fafc" }}
                />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Area
                  type="monotone"
                  dataKey="Hospital Patients / Million"
                  stroke="#3b82f6"
                  fill="url(#colorHosp)"
                  fillOpacity={0.1}
                />
                <Area
                  type="monotone"
                  dataKey="ICU Patients / Million"
                  stroke="#ef4444"
                  fill="url(#colorICU)"
                  fillOpacity={0.1}
                />
                <defs>
                  <linearGradient id="colorHosp" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorICU" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                </defs>
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </Card>
    </div>
  );
};
