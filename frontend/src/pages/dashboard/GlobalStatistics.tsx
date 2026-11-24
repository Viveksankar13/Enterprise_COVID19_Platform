import React from "react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import api from "../../services/api";
import { Card } from "../../components/ui/Card";
import { Spinner } from "../../components/ui/Spinner";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from "recharts";
import { Globe, Users, TrendingUp, ShieldAlert, AlertTriangle } from "lucide-react";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4"];

/* ── Premium Tooltip ── */
const CustomTooltip: React.FC<any> = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-panel rounded-xl px-4 py-3 border border-white/10 shadow-2xl">
      {label && <p className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wide">{label}</p>}
      {payload.map((entry: any) => (
        <p key={entry.name} className="text-sm font-bold" style={{ color: entry.color }}>
          {entry.name}: {Number(entry.value).toLocaleString()}
        </p>
      ))}
    </div>
  );
};

/* ── KPI Card ── */
const KpiCard: React.FC<{
  label: string; value: string; sub: string;
  icon: React.ComponentType<any>; iconClass: string; bgClass: string; delay?: number;
}> = ({ label, value, sub, icon: Icon, iconClass, bgClass, delay = 0 }) => (
  <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay }}>
    <Card variant="gradient" className="flex items-center gap-4">
      <div className={`h-12 w-12 rounded-xl flex items-center justify-center shrink-0 border border-white/10 ${bgClass}`}>
        <Icon size={22} className={iconClass} />
      </div>
      <div>
        <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">{label}</p>
        <p className="text-2xl font-black text-white mt-0.5">{value}</p>
        <p className="text-[11px] text-slate-500 mt-0.5">{sub}</p>
      </div>
    </Card>
  </motion.div>
);

export const GlobalStatistics: React.FC = () => {
  /* ── Data fetching ── */
  const { data: globalKpi, isLoading: kpiLoading, error: kpiError } = useQuery({
    queryKey: ["globalKPI"],
    queryFn: async () => { const res = await api.get("/analytics/global"); return res.data; },
  });

  const { data: continentKpis, isLoading: continentLoading } = useQuery({
    queryKey: ["continentKPIs"],
    queryFn: async () => { const res = await api.get("/analytics/continents"); return res.data; },
  });

  const { data: topCountries, isLoading: countriesLoading } = useQuery({
    queryKey: ["topCountries"],
    queryFn: async () => {
      const res = await api.get("/analytics/countries", { params: { limit: 10, sort_by: "total_cases", descending: true } });
      return res.data;
    },
  });

  const isLoading = kpiLoading || continentLoading || countriesLoading;

  /* ── Loading ── */
  if (isLoading) return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
      <Spinner size="lg" />
      <p className="text-sm text-slate-500 animate-pulse">Loading platform metrics from data warehouse…</p>
    </div>
  );

  /* ── Error ── */
  if (kpiError) return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6">
      <div className="h-16 w-16 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center mb-4">
        <AlertTriangle size={32} className="text-rose-400" />
      </div>
      <h2 className="text-xl font-bold text-rose-400">Failed to Load Global Statistics</h2>
      <p className="text-sm text-slate-500 mt-2 max-w-sm">
        Verify database credentials, connection pool states, and active containers.
      </p>
    </div>
  );

  /* ── Format data ── */
  const totalCases  = Number(globalKpi?.total_cases  || 0);
  const totalDeaths = Number(globalKpi?.total_deaths || 0);
  const totalVax    = Number(globalKpi?.total_vaccinations || 0);
  const posRate     = Number(globalKpi?.avg_positive_rate || 0);
  const cfr         = totalCases ? ((totalDeaths / totalCases) * 100).toFixed(2) : "—";
  const vaxPct      = globalKpi?.people_fully_vaccinated_pct ?? "—";

  const pieData = (continentKpis || [])
    .filter((c: any) => c.continent !== "Aggregate")
    .map((c: any) => ({ name: c.continent, value: Number(c.total_cases) }));

  const barData = (topCountries || []).map((c: any) => ({
    name: c.location?.length > 8 ? c.location.slice(0, 8) + "…" : c.location,
    Cases:  Number(c.total_cases),
    Deaths: Number(c.total_deaths),
  }));

  return (
    <div className="space-y-8">
      {/* ── Page Header ── */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex flex-wrap items-center justify-between gap-4"
      >
        <div>
          <h1 className="text-3xl font-black text-white">
            Global{" "}
            <span className="gradient-text">Epidemiology Summary</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Continental aggregates and country rankings based on live OWID data feeds.
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
          <div className="pulse-dot" />
          <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Synchronized: Active</span>
        </div>
      </motion.div>

      {/* ── KPI Cards ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard label="Global Cumulative Cases"  value={totalCases >= 1e6 ? `${(totalCases/1e6).toFixed(1)}M` : totalCases.toLocaleString()}
          sub="Live data feed" icon={Globe}      iconClass="text-blue-400"    bgClass="bg-blue-500/10"    delay={0.05} />
        <KpiCard label="Global Cumulative Deaths" value={totalDeaths.toLocaleString()}
          sub={`CFR: ${cfr}%`} icon={ShieldAlert} iconClass="text-rose-400"   bgClass="bg-rose-500/10"    delay={0.1} />
        <KpiCard label="Doses Administered"       value={totalVax >= 1e9 ? `${(totalVax/1e9).toFixed(2)}B` : `${(totalVax/1e6).toFixed(0)}M`}
          sub={`Fully vacc: ${vaxPct}%`} icon={Users}   iconClass="text-emerald-400" bgClass="bg-emerald-500/10" delay={0.15} />
        <KpiCard label="Avg Positivity Rate"      value={`${(posRate * 100).toFixed(2)}%`}
          sub="Global testing median" icon={TrendingUp} iconClass="text-amber-400" bgClass="bg-amber-500/10" delay={0.2} />
      </div>

      {/* ── Charts Row ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Donut pie */}
        <motion.div initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5, delay: 0.25 }}>
          <Card hoverable={false} className="p-5 h-full flex flex-col">
            <div className="mb-1">
              <h4 className="text-sm font-bold text-slate-200">Cases by Continent</h4>
              <p className="text-xs text-slate-500">Distribution of cumulative counts</p>
            </div>
            <div className="flex-1" style={{ minHeight: 220 }}>
              <ResponsiveContainer width="100%" height={230}>
                <PieChart>
                  <defs>
                    {COLORS.map((c, i) => (
                      <linearGradient key={i} id={`pie-grad-${i}`} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor={c} stopOpacity={1} />
                        <stop offset="100%" stopColor={c} stopOpacity={0.6} />
                      </linearGradient>
                    ))}
                  </defs>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={90}
                    paddingAngle={4} dataKey="value" stroke="none">
                    {pieData.map((_: any, i: number) => (
                      <Cell key={i} fill={`url(#pie-grad-${i % COLORS.length})`} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 mt-2">
              {pieData.map((item: any, idx: number) => (
                <div key={item.name} className="flex items-center gap-2 truncate">
                  <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: COLORS[idx % COLORS.length] }} />
                  <span className="text-[11px] text-slate-400 truncate">{item.name}</span>
                </div>
              ))}
            </div>
          </Card>
        </motion.div>

        {/* Top 10 Bar chart */}
        <motion.div className="lg:col-span-2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5, delay: 0.3 }}>
          <Card hoverable={false} className="p-5 h-full flex flex-col">
            <div className="mb-4">
              <h4 className="text-sm font-bold text-slate-200">Top 10 Countries by Cases</h4>
              <p className="text-xs text-slate-500">Highest cumulative cases vs. deaths</p>
            </div>
            <div className="flex-1" style={{ minHeight: 260 }}>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={barData} barGap={4}>
                  <defs>
                    <linearGradient id="barCases" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#3b82f6" stopOpacity={1} />
                      <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.3} />
                    </linearGradient>
                    <linearGradient id="barDeaths" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#ef4444" stopOpacity={1} />
                      <stop offset="100%" stopColor="#ef4444" stopOpacity={0.3} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" vertical={false} />
                  <XAxis dataKey="name" stroke="#475569" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis stroke="#475569" fontSize={11} tickLine={false} axisLine={false}
                    tickFormatter={(v) => `${(v / 1e6).toFixed(0)}M`} />
                  <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
                  <Bar dataKey="Cases"  fill="url(#barCases)"  radius={[4, 4, 0, 0]} maxBarSize={28} />
                  <Bar dataKey="Deaths" fill="url(#barDeaths)" radius={[4, 4, 0, 0]} maxBarSize={28} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            {/* Legend */}
            <div className="flex items-center gap-5 mt-3">
              <div className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded bg-blue-500" />
                <span className="text-[11px] text-slate-400">Cases</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded bg-rose-500" />
                <span className="text-[11px] text-slate-400">Deaths</span>
              </div>
            </div>
          </Card>
        </motion.div>
      </div>

      {/* ── Continental Detail Table ── */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.4 }}>
        <Card hoverable={false} className="p-5">
          <div className="mb-5">
            <h4 className="text-sm font-bold text-slate-200">Continental Breakdown</h4>
            <p className="text-xs text-slate-500">Aggregated metrics compiled from warehouse tables</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-400 border-collapse">
              <thead>
                <tr className="border-b border-white/8">
                  {["Continent", "Total Cases", "Total Deaths", "CFR", "Total Tests", "Vacc / 100"].map((h) => (
                    <th key={h} className="py-3 px-4 text-[11px] font-bold uppercase tracking-wider text-slate-500 first:text-left text-right first:text-left">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {(continentKpis || []).map((c: any) => (
                  <tr key={c.continent} className="border-b border-white/5 hover:bg-white/3 transition-colors">
                    <td className="py-3.5 px-4 font-semibold text-slate-200">
                      {c.continent === "Aggregate" ? (
                        <span className="gradient-text font-black">Global Sum</span>
                      ) : c.continent}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono">{Number(c.total_cases).toLocaleString()}</td>
                    <td className="py-3.5 px-4 text-right font-mono text-rose-400">{Number(c.total_deaths).toLocaleString()}</td>
                    <td className="py-3.5 px-4 text-right font-mono">
                      {c.total_cases ? `${((c.total_deaths / c.total_cases) * 100).toFixed(2)}%` : "—"}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono">
                      {c.total_tests ? Number(c.total_tests).toLocaleString() : "—"}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-emerald-400">
                      {c.people_fully_vaccinated_per_hundred ? Number(c.people_fully_vaccinated_per_hundred).toFixed(1) : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </motion.div>
    </div>
  );
};
