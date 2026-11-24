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
import { GitCompare, Calendar } from "lucide-react";

export const CountryComparison: React.FC = () => {
  const [countryA, setCountryA] = useState("USA");
  const [countryB, setCountryB] = useState("GBR");
  const [metric, setMetric] = useState("new_cases_smoothed");
  const [startDate, setStartDate] = useState("2020-03-01");
  const [endDate, setEndDate] = useState("2022-12-31");

  // Fetch active country listings
  const { data: countries } = useQuery({
    queryKey: ["countriesList"],
    queryFn: async () => {
      const res = await api.get("/countries", { params: { include_aggregates: false, limit: 250 } });
      return res.data;
    },
  });

  // Fetch Country A historical trend
  const { data: trendA, isLoading: loadingA } = useQuery({
    queryKey: ["trend", countryA, metric, startDate, endDate],
    queryFn: async () => {
      const res = await api.get("/analytics/trends/historical", {
        params: { iso_code: countryA, start_date: startDate, end_date: endDate, metric },
      });
      return res.data;
    },
  });

  // Fetch Country B historical trend
  const { data: trendB, isLoading: loadingB } = useQuery({
    queryKey: ["trend", countryB, metric, startDate, endDate],
    queryFn: async () => {
      const res = await api.get("/analytics/trends/historical", {
        params: { iso_code: countryB, start_date: startDate, end_date: endDate, metric },
      });
      return res.data;
    },
  });

  // Align dates and construct line chart data
  const chartData = React.useMemo(() => {
    if (!trendA || !trendB) return [];

    const mapA = new Map(trendA.map((d: any) => [d.date, d.value]));
    const mapB = new Map(trendB.map((d: any) => [d.date, d.value]));

    // Get all unique dates sorted
    const allDates = Array.from(new Set([...mapA.keys(), ...mapB.keys()])).sort();

    const locA = countries?.find((c: any) => c.iso_code === countryA)?.location || countryA;
    const locB = countries?.find((c: any) => c.iso_code === countryB)?.location || countryB;

    return allDates.map((dateStr) => ({
      date: dateStr,
      [locA]: mapA.get(dateStr) !== undefined ? Number(mapA.get(dateStr)) : null,
      [locB]: mapB.get(dateStr) !== undefined ? Number(mapB.get(dateStr)) : null,
    }));
  }, [trendA, trendB, countryA, countryB, countries]);

  // Fetch socioeconomic demographics details
  const { data: countryDetailsA } = useQuery({
    queryKey: ["countryDetails", countryA],
    queryFn: async () => {
      const res = await api.get(`/countries/${countryA}`);
      return res.data;
    },
    enabled: !!countryA,
  });

  const { data: countryDetailsB } = useQuery({
    queryKey: ["countryDetails", countryB],
    queryFn: async () => {
      const res = await api.get(`/countries/${countryB}`);
      return res.data;
    },
    enabled: !!countryB,
  });

  const isLoading = loadingA || loadingB;

  const metricsOptions = [
    { label: "Daily Cases (Smoothed)", value: "new_cases_smoothed" },
    { label: "Cumulative Cases", value: "total_cases" },
    { label: "Daily Deaths (Smoothed)", value: "new_deaths_smoothed" },
    { label: "Cumulative Deaths", value: "total_deaths" },
    { label: "Containment Policy Index", value: "stringency_index" },
    { label: "Positivity Testing Rate", value: "positive_rate" },
    { label: "Reproduction Number R", value: "reproduction_rate" },
  ];

  const locA = countries?.find((c: any) => c.iso_code === countryA)?.location || countryA;
  const locB = countries?.find((c: any) => c.iso_code === countryB)?.location || countryB;

  return (
    <div className="space-y-8">
      {/* Title */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground flex items-center gap-3">
            <GitCompare className="text-primary" size={28} />
            Country Comparison Panel
          </h1>
          <p className="text-muted-foreground mt-1">
            Compare infection curves, vaccination trends, and social parameters side-by-side.
          </p>
        </div>
      </div>

      {/* Control Filters Panel */}
      <Card className="p-6 grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">
            Country Alpha
          </label>
          <select
            value={countryA}
            onChange={(e) => setCountryA(e.target.value)}
            className="w-full bg-muted/40 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all duration-200"
          >
            {countries &&
              countries.map((c: any) => (
                <option key={c.iso_code} value={c.iso_code} className="bg-slate-900">
                  {c.location}
                </option>
              ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">
            Country Beta
          </label>
          <select
            value={countryB}
            onChange={(e) => setCountryB(e.target.value)}
            className="w-full bg-muted/40 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all duration-200"
          >
            {countries &&
              countries.map((c: any) => (
                <option key={c.iso_code} value={c.iso_code} className="bg-slate-900">
                  {c.location}
                </option>
              ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">
            Select Metric
          </label>
          <select
            value={metric}
            onChange={(e) => setMetric(e.target.value)}
            className="w-full bg-muted/40 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all duration-200"
          >
            {metricsOptions.map((m) => (
              <option key={m.value} value={m.value} className="bg-slate-900">
                {m.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
            <Calendar size={14} /> Start Date
          </label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="w-full bg-muted/40 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all duration-200"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
            <Calendar size={14} /> End Date
          </label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="w-full bg-muted/40 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all duration-200"
          />
        </div>
      </Card>

      {/* Primary Chart Visualization */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="text-sm font-bold text-foreground">Timeline Infection curves</h3>
            <p className="text-xs text-muted-foreground">Adjust filters above to modify axes values</p>
          </div>
          <Badge variant="info">Comparative Time-Series</Badge>
        </div>

        {isLoading ? (
          <div className="h-80 flex flex-col items-center justify-center gap-2">
            <Spinner />
            <span className="text-xs text-muted-foreground">Compiling historical vectors...</span>
          </div>
        ) : chartData.length === 0 ? (
          <div className="h-80 flex items-center justify-center text-sm text-muted-foreground">
            No historical records found for this combination of query filters.
          </div>
        ) : (
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                <Tooltip
                  formatter={(value) => (value !== null ? Number(value).toLocaleString() : "N/A")}
                  contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#f8fafc" }}
                />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Line
                  type="monotone"
                  dataKey={locA}
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 6 }}
                />
                <Line
                  type="monotone"
                  dataKey={locB}
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </Card>

      {/* Side-by-Side Socioeconomic Profiles */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Profile Country A */}
        <Card hoverable={false} className="p-6 border-l-4 border-l-blue-500">
          <div className="flex justify-between items-center mb-4">
            <h4 className="font-bold text-foreground text-lg">{locA}</h4>
            <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-blue-500/10 text-blue-400 uppercase">
              {countryDetailsA?.income_group || "Socioeconomic baseline"}
            </span>
          </div>
          <div className="space-y-3.5 text-sm">
            <div className="flex justify-between border-b border-border/50 pb-1.5">
              <span className="text-muted-foreground">Continent</span>
              <span className="font-semibold">{countryDetailsA?.continent}</span>
            </div>
            <div className="flex justify-between border-b border-border/50 pb-1.5">
              <span className="text-muted-foreground">Data Ingestion Source</span>
              <span className="font-semibold">{countryDetailsA?.data_source}</span>
            </div>
            <div className="flex justify-between border-b border-border/50 pb-1.5">
              <span className="text-muted-foreground">Entity Type</span>
              <span className="font-semibold">
                {countryDetailsA?.is_aggregate ? "Regional Aggregate" : "Individual Sovereign State"}
              </span>
            </div>
          </div>
        </Card>

        {/* Profile Country B */}
        <Card hoverable={false} className="p-6 border-l-4 border-l-emerald-500">
          <div className="flex justify-between items-center mb-4">
            <h4 className="font-bold text-foreground text-lg">{locB}</h4>
            <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-emerald-500/10 text-emerald-400 uppercase">
              {countryDetailsB?.income_group || "Socioeconomic baseline"}
            </span>
          </div>
          <div className="space-y-3.5 text-sm">
            <div className="flex justify-between border-b border-border/50 pb-1.5">
              <span className="text-muted-foreground">Continent</span>
              <span className="font-semibold">{countryDetailsB?.continent}</span>
            </div>
            <div className="flex justify-between border-b border-border/50 pb-1.5">
              <span className="text-muted-foreground">Data Ingestion Source</span>
              <span className="font-semibold">{countryDetailsB?.data_source}</span>
            </div>
            <div className="flex justify-between border-b border-border/50 pb-1.5">
              <span className="text-muted-foreground">Entity Type</span>
              <span className="font-semibold">
                {countryDetailsB?.is_aggregate ? "Regional Aggregate" : "Individual Sovereign State"}
              </span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
