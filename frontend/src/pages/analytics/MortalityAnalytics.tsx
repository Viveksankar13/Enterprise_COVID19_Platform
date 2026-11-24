import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "../../services/api";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Spinner } from "../../components/ui/Spinner";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Skull, TrendingUp, AlertTriangle } from "lucide-react";

export const MortalityAnalytics: React.FC = () => {
  const [country, setCountry] = useState("USA");

  // Fetch active country listings
  const { data: countries } = useQuery({
    queryKey: ["countriesList"],
    queryFn: async () => {
      const res = await api.get("/countries", { params: { include_aggregates: false, limit: 250 } });
      return res.data;
    },
  });

  // Fetch Excess Mortality
  const { data: excessMortality, isLoading: excessLoading } = useQuery({
    queryKey: ["excessMortality", country],
    queryFn: async () => {
      const res = await api.get("/analytics/mortality/excess", {
        params: { iso_code: country },
      });
      return res.data;
    },
  });

  // Fetch Waves Detected
  const { data: wavesData, isLoading: wavesLoading } = useQuery({
    queryKey: ["wavesData", country],
    queryFn: async () => {
      const res = await api.get("/analytics/epidemic/waves", {
        params: { iso_code: country },
      });
      return res.data;
    },
  });

  const loc = countries?.find((c: any) => c.iso_code === country)?.location || country;

  return (
    <div className="space-y-8">
      {/* Title */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground flex items-center gap-3">
            <Skull className="text-red-400" size={28} />
            Mortality & Epidemic Wave Analysis
          </h1>
          <p className="text-muted-foreground mt-1">
            Track Case Fatality Rates (CFR), wave detection algorithms, and excess mortality burdens.
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

      {/* CFR Line Chart */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="text-sm font-bold text-foreground">Case Fatality Rate (CFR) Timeline</h3>
            <p className="text-xs text-muted-foreground">Cumulative Deaths / Cumulative Cases over time</p>
          </div>
          <Badge variant="danger">CFR Ratio</Badge>
        </div>

        {excessLoading ? (
          <div className="h-72 flex items-center justify-center">
            <Spinner />
          </div>
        ) : !excessMortality || excessMortality.length === 0 ? (
          <div className="h-72 flex items-center justify-center text-sm text-muted-foreground">
            No mortality metrics found for this country.
          </div>
        ) : (
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={excessMortality}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis
                  stroke="#94a3b8"
                  fontSize={11}
                  tickLine={false}
                  tickFormatter={(val) => `${Number(val).toFixed(1)}%`}
                />
                <Tooltip
                  formatter={(val) => `${Number(val).toFixed(3)}%`}
                  contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#f8fafc" }}
                />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Line
                  type="monotone"
                  dataKey="case_fatality_rate_pct"
                  name="Case Fatality Rate"
                  stroke="#f43f5e"
                  strokeWidth={2.5}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </Card>

      {/* Wave Detection Detail Table */}
      <Card hoverable={false} className="p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
              <TrendingUp size={18} className="text-primary" />
              Epidemiological Wave Cycle Tracking: {loc}
            </h3>
            <p className="text-xs text-muted-foreground">Calculated dynamically via daily growth averages</p>
          </div>
        </div>

        {wavesLoading ? (
          <div className="h-48 flex items-center justify-center">
            <Spinner />
          </div>
        ) : !wavesData || wavesData.length === 0 ? (
          <div className="p-10 text-center text-sm text-muted-foreground bg-muted/10 border border-border rounded-xl">
            <AlertTriangle className="mx-auto text-amber-500 mb-2" size={32} />
            Growth wave peaks were not detected or require additional historical data points.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-muted-foreground border-collapse">
              <thead>
                <tr className="border-b border-border text-xs font-semibold text-foreground uppercase tracking-wider bg-muted/20">
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4 text-right">Daily Cases (Smoothed)</th>
                  <th className="py-3 px-4 text-right">Growth Rate % (Weekly)</th>
                  <th className="py-3 px-4 text-center">Epidemiological State</th>
                </tr>
              </thead>
              <tbody>
                {wavesData.slice(-15).map((w: any) => (
                  <tr key={w.date} className="border-b border-border hover:bg-muted/15 transition-colors">
                    <td className="py-3.5 px-4 font-semibold text-foreground">{w.date}</td>
                    <td className="py-3.5 px-4 text-right font-mono">
                      {w.new_cases_smoothed ? Number(w.new_cases_smoothed).toLocaleString() : "0"}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono">
                      {w.wow_growth_cases_pct
                        ? `${(Number(w.wow_growth_cases_pct) * 100).toFixed(1)}%`
                        : "—"}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <Badge variant={w.wave_state === "WAVE_START" || w.wave_state === "WAVE_PEAK" ? "danger" : "neutral"}>
                        {w.wave_state || "Baseline"}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};
