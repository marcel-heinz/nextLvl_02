"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { 
  WorkflowStatus, 
  WorkflowMetrics, 
  WorkflowStages, 
  HealthStatus, 
  Stage,
  WorkflowControlResponse 
} from "@/lib/types";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { WorkflowVisualization } from "@/components/workflow/WorkflowVisualization";

export default function WorkflowMonitorPage() {
  const [status, setStatus] = useState<WorkflowStatus | null>(null);
  const [metrics, setMetrics] = useState<WorkflowMetrics | null>(null);
  const [stages, setStages] = useState<WorkflowStages | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchAllData = async () => {
    try {
      setError(null);
      const [statusData, metricsData, stagesData, healthData] = await Promise.all([
        api.getWorkflowStatus(),
        api.getWorkflowMetrics(),
        api.getWorkflowStages(),
        api.getHealthStatus(),
      ]);
      
      setStatus(statusData);
      setMetrics(metricsData);
      setStages(stagesData);
      setHealth(healthData);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch workflow data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(fetchAllData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [autoRefresh]);

  const handleWorkflowControl = async (action: "start" | "stop" | "restart") => {
    try {
      let response: WorkflowControlResponse;
      switch (action) {
        case "start":
          response = await api.startWorkflow();
          break;
        case "stop":
          response = await api.stopWorkflow();
          break;
        case "restart":
          response = await api.restartWorkflow();
          break;
      }
      
      if (response.success) {
        // Refresh data after action
        setTimeout(fetchAllData, 1000);
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to ${action} workflow`);
    }
  };

  const handleTriggerStage = async (stage: Stage) => {
    try {
      const response = await api.triggerStageProcessing(stage);
      if (response.success) {
        // Refresh metrics after triggering
        setTimeout(fetchAllData, 500);
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to trigger ${stage} stage`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg text-gray-600">Loading workflow data...</div>
      </div>
    );
  }

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case "idle": return "bg-green-100 text-green-800";
      case "processing": return "bg-blue-100 text-blue-800";
      case "error": return "bg-red-100 text-red-800";
      case "stopped": return "bg-gray-100 text-gray-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getEngineStatusColor = (running: boolean) => {
    return running ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800";
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Workflow Monitor</h1>
          <p className="text-gray-600">Real-time monitoring of automation pipeline</p>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
            Auto-refresh
          </label>
          <Button onClick={fetchAllData} variant="outline">
            🔄 Refresh
          </Button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <Card>
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2">
              <span className="text-red-600">❌</span>
              <span className="text-red-800 font-medium">Error</span>
            </div>
            <p className="text-red-700 mt-1">{error}</p>
            <Button 
              onClick={() => setError(null)} 
              variant="outline" 
              className="mt-2 text-sm"
            >
              Dismiss
            </Button>
          </div>
        </Card>
      )}

      {/* Last Updated */}
      {lastUpdated && (
        <div className="text-sm text-gray-500">
          Last updated: {lastUpdated.toLocaleTimeString()}
        </div>
      )}

      {/* System Health Overview */}
      <Card>
        <div className="p-6">
          <h2 className="text-lg font-semibold mb-4">System Health</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl mb-1">🏥</div>
              <div className="text-sm text-gray-600">API Status</div>
              <Badge className={health?.status === "healthy" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
                {health?.status || "unknown"}
              </Badge>
            </div>
            <div className="text-center">
              <div className="text-2xl mb-1">⚙️</div>
              <div className="text-sm text-gray-600">Workflow Engine</div>
              <Badge className={status?.engine_running ? getEngineStatusColor(true) : getEngineStatusColor(false)}>
                {status?.engine_running ? "Running" : "Stopped"}
              </Badge>
            </div>
            <div className="text-center">
              <div className="text-2xl mb-1">📊</div>
              <div className="text-sm text-gray-600">Total Items</div>
              <div className="text-lg font-semibold text-[#008B8B]">{metrics?.total_items || 0}</div>
            </div>
            <div className="text-center">
              <div className="text-2xl mb-1">🔄</div>
              <div className="text-sm text-gray-600">Active Processors</div>
              <div className="text-lg font-semibold text-[#008B8B]">
                {status ? Object.values(status.processors).filter(p => p.status === "processing").length : 0}
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Workflow Controls */}
      <Card>
        <div className="p-6">
          <h2 className="text-lg font-semibold mb-4">Workflow Controls</h2>
          <div className="flex gap-3">
            <Button 
              onClick={() => handleWorkflowControl("start")}
              disabled={status?.engine_running}
              className="bg-green-600 hover:bg-green-700"
            >
              ▶️ Start Engine
            </Button>
            <Button 
              onClick={() => handleWorkflowControl("stop")}
              disabled={!status?.engine_running}
              className="bg-red-600 hover:bg-red-700"
            >
              ⏹️ Stop Engine
            </Button>
            <Button 
              onClick={() => handleWorkflowControl("restart")}
              className="bg-orange-600 hover:bg-orange-700"
            >
              🔄 Restart Engine
            </Button>
          </div>
        </div>
      </Card>

      {/* Pipeline Visualization */}
      {stages && metrics && (
        <Card>
          <div className="p-6">
            <WorkflowVisualization stages={stages} metrics={metrics} />
          </div>
        </Card>
      )}

      {/* Queue Lengths */}
      <Card>
        <div className="p-6">
          <h2 className="text-lg font-semibold mb-4">Pipeline Queue Controls</h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {stages?.stages.map((stage) => (
              <div key={stage} className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-lg font-medium text-gray-900">{stage}</div>
                <div className="text-2xl font-bold text-[#008B8B] my-2">
                  {metrics?.queue_lengths[stage] || 0}
                </div>
                <div className="text-sm text-gray-600">items</div>
                {stage !== "New" && stage !== "Done" && (
                  <Button
                    onClick={() => handleTriggerStage(stage as Stage)}
                    variant="outline"
                    className="mt-2 text-xs"
                  >
                    ⚡ Trigger
                  </Button>
                )}
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Processor Status */}
      <Card>
        <div className="p-6">
          <h2 className="text-lg font-semibold mb-4">Processor Status</h2>
          <div className="space-y-3">
            {status && Object.entries(status.processors).map(([stageName, processor]) => (
              <div key={stageName} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="font-medium">{stageName}</div>
                  <Badge className={getStatusBadgeColor(processor.status)}>
                    {processor.status}
                  </Badge>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <span>Poll: {processor.poll_interval}s</span>
                  {processor.current_automation && (
                    <span className="text-blue-600">Processing: {processor.current_automation}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Stage Flow */}
      <Card>
        <div className="p-6">
          <h2 className="text-lg font-semibold mb-4">Pipeline Flow</h2>
          <div className="space-y-4">
            {stages?.stage_flow.map((flow, index) => (
              <div key={index} className="flex items-center gap-3">
                <div className="px-3 py-1 bg-[#E0F7F7] text-[#008B8B] rounded font-medium">
                  {flow.from}
                </div>
                <span className="text-gray-400">→</span>
                <div className="px-3 py-1 bg-[#E0F7F7] text-[#008B8B] rounded font-medium">
                  {flow.to}
                </div>
                <div className="text-sm text-gray-600 ml-4">
                  {stages.description[flow.to]}
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
}
