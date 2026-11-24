import React, { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import api from "../../services/api";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { Spinner } from "../../components/ui/Spinner";
import { Database, Play, Download, HelpCircle, Code } from "lucide-react";

interface QueryResult {
  columns: string[];
  rows: Record<string, any>[];
  message?: string;
}

export const SQLExplorer: React.FC = () => {
  const [sql, setSql] = useState("SELECT iso_code, location, continent, income_group \nFROM countries \nWHERE is_aggregate = false \nLIMIT 10;");
  const [result, setResult] = useState<QueryResult | null>(null);
  const [errorMsg, setErrorMsg] = useState("");

  const templates = [
    {
      title: "Query active countries list",
      code: "SELECT iso_code, location, continent, income_group \nFROM countries \nWHERE is_active = true AND is_aggregate = false \nORDER BY location ASC \nLIMIT 20;",
    },
    {
      title: "Analyze cumulative metrics",
      code: "SELECT iso_code, count(*) as records_count, max(total_cases) as peak_cases, max(total_deaths) as peak_deaths \nFROM daily_metrics \nGROUP BY iso_code \nORDER BY peak_cases DESC \nLIMIT 10;",
    },
    {
      title: "Audit database ETL logs",
      code: "SELECT run_id, pipeline_name, status, started_at, completed_at, rows_inserted \nFROM etl_logs \nORDER BY started_at DESC \nLIMIT 15;",
    },
  ];

  const mutation = useMutation({
    mutationFn: async (sqlQuery: string) => {
      setErrorMsg("");
      const res = await api.post("/admin/query", { sql: sqlQuery });
      return res.data;
    },
    onSuccess: (data) => {
      setResult(data);
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail || "Execution failed due to query syntax error.";
      setErrorMsg(msg);
      setResult(null);
    },
  });

  const handleExecute = () => {
    mutation.mutate(sql);
  };

  const handleExportCSV = () => {
    if (!result || result.rows.length === 0) return;

    // Build CSV content
    const headers = result.columns.join(",");
    const rows = result.rows.map((row) =>
      result.columns.map((col) => {
        const val = row[col];
        if (val === null || val === undefined) return "";
        const strVal = String(val).replace(/"/g, '""');
        return strVal.includes(",") || strVal.includes("\n") ? `"${strVal}"` : strVal;
      }).join(",")
    );

    const csvContent = "data:text/csv;charset=utf-8," + [headers, ...rows].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `sql_query_result_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-8">
      {/* Title */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground flex items-center gap-3">
            <Database className="text-primary" size={28} />
            Data Warehouse SQL Explorer
          </h1>
          <p className="text-muted-foreground mt-1">
            Execute read-only SQL queries directly against database schemas for custom reporting.
          </p>
        </div>
        <Badge variant="info">Write Restrictions Enabled</Badge>
      </div>

      {/* Editor & Templates Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Templates list */}
        <Card className="lg:col-span-1 p-5 flex flex-col gap-4">
          <div className="flex items-center gap-2 border-b border-border pb-3">
            <HelpCircle size={18} className="text-primary" />
            <h3 className="text-sm font-bold text-foreground">Query Templates</h3>
          </div>
          <div className="space-y-3 flex-1">
            {templates.map((tpl, idx) => (
              <button
                key={idx}
                onClick={() => setSql(tpl.code)}
                className="w-full text-left p-3 rounded-lg bg-muted/40 hover:bg-muted border border-border/60 hover:border-primary/50 text-xs font-semibold text-muted-foreground hover:text-foreground transition-all duration-200 cursor-pointer"
              >
                {tpl.title}
              </button>
            ))}
          </div>
        </Card>

        {/* Query Input Editor */}
        <Card className="lg:col-span-3 p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Code size={18} className="text-primary" />
              <h3 className="text-sm font-bold text-foreground">SQL Query Editor</h3>
            </div>
            <span className="text-[10px] text-muted-foreground font-mono">Dialect: PostgreSQL</span>
          </div>

          <textarea
            value={sql}
            onChange={(e) => setSql(e.target.value)}
            rows={8}
            className="w-full font-mono text-sm bg-black/30 border border-border rounded-xl p-4 text-foreground focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all duration-200"
            placeholder="SELECT * FROM table LIMIT 10;"
          />

          <div className="flex gap-3">
            <Button
              onClick={handleExecute}
              isLoading={mutation.isPending}
              className="flex items-center gap-2"
            >
              <Play size={16} /> Execute Query
            </Button>
            {result && result.rows.length > 0 && (
              <Button variant="outline" onClick={handleExportCSV} className="flex items-center gap-2">
                <Download size={16} /> Export CSV
              </Button>
            )}
          </div>

          {/* Validation/Error alerts */}
          {errorMsg && (
            <div className="p-4 rounded-xl bg-destructive/15 border border-destructive/20 text-rose-400 text-xs font-semibold leading-relaxed">
              {errorMsg}
            </div>
          )}
        </Card>
      </div>

      {/* Query Output Results Console */}
      <Card hoverable={false} className="p-6 min-h-[200px]">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-sm font-bold text-foreground">Query Output Results</h3>
          {result && (
            <span className="text-xs text-muted-foreground font-mono">
              Returned {result.rows.length} rows
            </span>
          )}
        </div>

        {mutation.isPending ? (
          <div className="flex flex-col items-center justify-center py-12 gap-2 text-muted-foreground text-xs">
            <Spinner />
            <span>Running database queries...</span>
          </div>
        ) : !result ? (
          <div className="flex flex-col items-center justify-center py-12 text-muted-foreground text-xs">
            <span>Execute a SQL query to see data outputs.</span>
          </div>
        ) : result.rows.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-muted-foreground text-xs">
            <span>Query executed successfully. 0 rows returned.</span>
          </div>
        ) : (
          <div className="overflow-x-auto max-h-[400px]">
            <table className="w-full text-left text-xs text-muted-foreground border-collapse">
              <thead>
                <tr className="border-b border-border text-[10px] font-semibold text-foreground uppercase tracking-wider bg-muted/30">
                  {result.columns.map((col) => (
                    <th key={col} className="py-2.5 px-3">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.rows.map((row, idx) => (
                  <tr
                    key={idx}
                    className="border-b border-border/50 hover:bg-muted/15 transition-colors"
                  >
                    {result.columns.map((col) => (
                      <td key={col} className="py-2.5 px-3 font-mono truncate max-w-[200px]">
                        {row[col] === null || row[col] === undefined ? "NULL" : String(row[col])}
                      </td>
                    ))}
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
