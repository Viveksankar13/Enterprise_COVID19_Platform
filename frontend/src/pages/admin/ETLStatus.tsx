import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../../services/api";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { Spinner } from "../../components/ui/Spinner";
import { Calendar, Play, CheckCircle, XCircle, RefreshCw, AlertTriangle } from "lucide-react";

export const ETLStatus: React.FC = () => {
  const queryClient = useQueryClient();

  // Fetch ETL Runs history
  const { data: runs, isLoading: runsLoading, refetch } = useQuery({
    queryKey: ["etlRuns"],
    queryFn: async () => {
      const res = await api.get("/etl/runs", { params: { limit: 15 } });
      return res.data;
    },
  });

  // Fetch active runs
  const { data: activeRuns } = useQuery({
    queryKey: ["etlActive"],
    queryFn: async () => {
      const res = await api.get("/etl/active");
      return res.data;
    },
    refetchInterval: 5000, // Poll active runs every 5 seconds
  });

  // Ingestion Trigger mutation
  const triggerMutation = useMutation({
    mutationFn: async (force: boolean) => {
      const res = await api.post(`/etl/trigger`, null, { params: { force } });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["etlRuns"] });
      queryClient.invalidateQueries({ queryKey: ["etlActive"] });
    },
  });

  const handleTrigger = (force: boolean) => {
    triggerMutation.mutate(force);
  };

  const isPipelineRunning = activeRuns && activeRuns.length > 0;

  return (
    <div className="space-y-8">
      {/* Title */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground flex items-center gap-3">
            <Calendar className="text-primary" size={28} />
            ETL Ingestion Logs
          </h1>
          <p className="text-muted-foreground mt-1">
            Track daily ingestion pipeline executions and manual warehouse refresh runs.
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={() => refetch()} className="flex items-center gap-2">
            <RefreshCw size={16} /> Refresh State
          </Button>
          <Button
            onClick={() => handleTrigger(false)}
            isLoading={triggerMutation.isPending}
            disabled={isPipelineRunning}
            className="flex items-center gap-2"
          >
            <Play size={16} /> Trigger Ingestion
          </Button>
          <Button
            variant="outline"
            onClick={() => handleTrigger(true)}
            disabled={isPipelineRunning}
            className="border-amber-500/30 text-amber-400 hover:bg-amber-500/10 flex items-center gap-2"
          >
            Force Complete Run
          </Button>
        </div>
      </div>

      {/* Active Run Status alert banner */}
      {isPipelineRunning && (
        <Card className="border-l-4 border-l-primary bg-primary/5 p-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Spinner size="sm" />
            <div>
              <h4 className="font-bold text-foreground">Pipeline Execution In Progress</h4>
              <p className="text-xs text-muted-foreground">
                ETL is downloading the latest dataset from Our World in Data and refreshing materialized views.
              </p>
            </div>
          </div>
          <Badge variant="info">Active Ingest</Badge>
        </Card>
      )}

      {/* Logs Table */}
      <Card hoverable={false} className="p-6">
        <h3 className="text-sm font-bold text-foreground mb-4">Historical Pipeline Execution Runs</h3>
        {runsLoading ? (
          <div className="h-64 flex items-center justify-center">
            <Spinner />
          </div>
        ) : !runs || runs.length === 0 ? (
          <div className="py-12 text-center text-sm text-muted-foreground">
            No pipeline executions recorded in the logging tables.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-muted-foreground border-collapse">
              <thead>
                <tr className="border-b border-border text-[10px] font-semibold text-foreground uppercase tracking-wider bg-muted/20">
                  <th className="py-3 px-4">Run ID</th>
                  <th className="py-3 px-4">Started At</th>
                  <th className="py-3 px-4">Completed At</th>
                  <th className="py-3 px-4 text-center">Status</th>
                  <th className="py-3 px-4 text-right">Downloaded</th>
                  <th className="py-3 px-4 text-right">Inserted</th>
                  <th className="py-3 px-4 text-right">Rejected</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((run: any) => (
                  <React.Fragment key={run.run_id}>
                    <tr className="border-b border-border hover:bg-muted/15 transition-colors">
                      <td className="py-3.5 px-4 font-mono font-semibold text-foreground truncate max-w-[150px]">
                        {run.run_id}
                      </td>
                      <td className="py-3.5 px-4">{new Date(run.started_at).toLocaleString()}</td>
                      <td className="py-3.5 px-4">
                        {run.completed_at ? new Date(run.completed_at).toLocaleString() : "—"}
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <Badge
                          variant={
                            run.status === "SUCCESS"
                              ? "success"
                              : run.status === "FAILED"
                              ? "danger"
                              : "neutral"
                          }
                          className="flex items-center gap-1 w-fit mx-auto"
                        >
                          {run.status === "SUCCESS" ? (
                            <CheckCircle size={12} />
                          ) : run.status === "FAILED" ? (
                            <XCircle size={12} />
                          ) : (
                            <Spinner size="sm" className="h-3 w-3 text-muted-foreground" />
                          )}
                          {run.status}
                        </Badge>
                      </td>
                      <td className="py-3.5 px-4 text-right font-mono">
                        {Number(run.rows_downloaded).toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4 text-right font-mono text-emerald-400">
                        {Number(run.rows_inserted).toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4 text-right font-mono text-rose-400">
                        {Number(run.rows_rejected).toLocaleString()}
                      </td>
                    </tr>
                    {/* Error tracing row */}
                    {run.status === "FAILED" && run.error_message && (
                      <tr className="bg-destructive/5 text-rose-300">
                        <td colSpan={7} className="py-2.5 px-4 font-mono text-[10px] leading-relaxed">
                          <div className="flex items-start gap-2">
                            <AlertTriangle className="shrink-0 text-rose-400 mt-0.5" size={14} />
                            <div>
                              <span className="font-bold text-rose-400 uppercase">Error Traceback:</span>{" "}
                              {run.error_message}
                              {run.error_traceback && (
                                <pre className="mt-1 bg-black/20 p-2 rounded max-h-[150px] overflow-y-auto text-[9px]">
                                  {run.error_traceback}
                                </pre>
                              )}
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};
