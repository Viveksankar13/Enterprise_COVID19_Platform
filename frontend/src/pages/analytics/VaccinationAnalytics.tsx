import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "../../services/api";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Spinner } from "../../components/ui/Spinner";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Syringe, Award } from "lucide-react";

export const VaccinationAnalytics: React.FC = () => {
  const [country, setCountry] = useState("USA");

  // Fetch active country listings
  const { data: countries } = useQuery({
    queryKey: ["countriesList"],
    queryFn: async () => {
      const res = await api.get("/countries", { params: { include_aggregates: false, limit: 250 } });
      return res.data;
    },
  });

  // Fetch Vaccine Equity by Income Group
  const { data: equityData, isLoading: equityLoading } = useQuery({
    queryKey: ["vaccineEquity"],
    queryFn: async () => {
      const res = await api.get("/vaccinations/equity");
      return res.data;
    },
  });

  // Fetch Country Vaccination History
  const { data: vaccHistory, isLoading: historyLoading } = useQuery({
    queryKey: ["vaccHistory", country],
    queryFn: async () => {
      const res = await api.get("/vaccinations/history", {
        params: { iso_code: country },
      });
      return res.data;
    },
  });

  // Format historical area chart data
  const historyChartData = vaccHistory
    ? vaccHistory.map((d: any) => ({
        date: d.date,
        "Doses Administered": Number(d.total_vaccinations) || 0,
        "Fully Vaccinated": Number(d.people_fully_vaccinated) || 0,
      }))
    : [];

  const loc = countries?.find((c: any) => c.iso_code === country)?.location || country;

  return (
    <div className="space-y-8">
      {/* Title */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground flex items-center gap-3">
            <Syringe className="text-emerald-400" size={28} />
            Immunization & Vaccine Equity Analytics
          </h1>
          <p className="text-muted-foreground mt-1">
            Analyze global vaccine distribution, coverage milestones, and socio-economic gaps.
          </p>
        </div>
      </div>

      {/* Equity Chart (Global distribution by income groups) */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="text-sm font-bold text-foreground">Global Vaccine Coverage by Income Group</h3>
            <p className="text-xs text-muted-foreground">Compares coverage milestones by World Bank GDP category</p>
          </div>
          <Badge variant="warning">Equity Insights</Badge>
        </div>

        {equityLoading ? (
          <div className="h-64 flex items-center justify-center">
            <Spinner />
          </div>
        ) : (
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={equityData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis type="number" stroke="#94a3b8" fontSize={11} tickLine={false} domain={[0, 100]} />
                <YAxis
                  type="category"
                  dataKey="income_group"
                  stroke="#94a3b8"
                  fontSize={11}
                  tickLine={false}
                  width={140}
                />
                <Tooltip
                  formatter={(val) => `${Number(val).toFixed(2)}%`}
                  contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#f8fafc" }}
                />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Bar
                  dataKey="people_fully_vaccinated_per_hundred"
                  name="Fully Vaccinated %"
                  fill="#10b981"
                  radius={[0, 4, 4, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </Card>

      {/* Country Immunization Timeline Area Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Country Selector */}
        <Card className="lg:col-span-1 p-6 flex flex-col justify-between">
          <div>
            <h4 className="text-sm font-bold text-foreground mb-4">Country Selection</h4>
            <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">
              Select Country Filter
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
          </div>

          <div className="mt-6 p-4 bg-muted/20 border border-border rounded-xl">
            <div className="flex gap-2 text-primary mb-2">
              <Award size={20} />
              <span className="text-xs font-bold uppercase tracking-wider">Milestone Alert</span>
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Fully vaccinated rate indicates the percentage of the population that has received all prescribed doses. Track the curve to observe herd immunity transitions.
            </p>
          </div>
        </Card>

        {/* Timeline Area Chart */}
        <Card className="lg:col-span-2 p-6">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-sm font-bold text-foreground">Immunization Curves: {loc}</h3>
              <p className="text-xs text-muted-foreground">Cumulative doses administered over time</p>
            </div>
          </div>

          {historyLoading ? (
            <div className="h-72 flex items-center justify-center">
              <Spinner />
            </div>
          ) : historyChartData.length === 0 ? (
            <div className="h-72 flex items-center justify-center text-sm text-muted-foreground">
              No vaccination historical records found for this country.
            </div>
          ) : (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={historyChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <YAxis
                    stroke="#94a3b8"
                    fontSize={11}
                    tickLine={false}
                    tickFormatter={(val) => `${(val / 1e6).toFixed(0)}M`}
                  />
                  <Tooltip
                    formatter={(val) => Number(val).toLocaleString()}
                    contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#f8fafc" }}
                  />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Area
                    type="monotone"
                    dataKey="Doses Administered"
                    stroke="#3b82f6"
                    fill="url(#colorDoses)"
                    fillOpacity={0.15}
                  />
                  <Area
                    type="monotone"
                    dataKey="Fully Vaccinated"
                    stroke="#10b981"
                    fill="url(#colorFully)"
                    fillOpacity={0.15}
                  />
                  <defs>
                    <linearGradient id="colorDoses" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorFully" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};
