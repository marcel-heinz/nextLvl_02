"use client";

import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import { Automation, AutomationCreate, Stage, STAGES } from "@/lib/types";
import { KanbanColumn } from "@/components/pipeline/KanbanColumn";
import { CreateAutomationDialog } from "@/components/pipeline/CreateAutomationDialog";
import { DocumentViewerModal } from "@/components/pipeline/DocumentViewerModal";

export default function PipelinePage() {
  const [items, setItems] = useState<Automation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAutomation, setSelectedAutomation] = useState<Automation | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listAutomations();
      setItems(data);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const grouped = useMemo(() => {
    const byStage: Record<Stage, Automation[]> = {
      New: [],
      Classification: [],
      "Data Extraction": [],
      Processing: [],
      Done: [],
    };
    for (const item of items) {
      byStage[item.stage].push(item);
    }
    
    // Sort each stage by creation date (newest first - LIFO)
    Object.keys(byStage).forEach((stage) => {
      byStage[stage as Stage].sort((a, b) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
    });
    
    return byStage;
  }, [items]);

  async function onCreate(payload: AutomationCreate) {
    await api.createAutomation({
      title: payload.title || "Untitled",
      stage: payload.stage,
    });
    await load();
  }

  async function onFileUpload(automation: Automation) {
    // File upload already created the automation, just refresh the list
    await load();
  }

  async function onDelete(id: string) {
    // Optimistically update the UI by removing the item
    setItems(prevItems => prevItems.filter(item => item.id !== id));
    
    try {
      await api.deleteAutomation(id);
    } catch (error) {
      console.error("Failed to delete automation:", error);
      // Reload data if deletion failed to restore the correct state
      await load();
    }
  }

  async function onChangeStage(id: string, stage: Stage) {
    await api.updateAutomation(id, { stage });
    await load();
  }

  function handleCardClick(automation: Automation) {
    setSelectedAutomation(automation);
  }

  function closeDocumentViewer() {
    setSelectedAutomation(null);
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-[#008B8B]">Automation Pipeline</h1>
        <CreateAutomationDialog onCreate={onCreate} onFileUpload={onFileUpload} />
      </div>
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {STAGES.map((stage) => (
            <div key={stage} className="animate-pulse h-80 rounded-lg bg-gray-100" />
          ))}
        </div>
      ) : error ? (
        <div className="text-red-600 text-sm">{error}</div>
      ) : (
        <div className="flex gap-4 h-[calc(100vh-200px)] overflow-x-auto">
          {STAGES.map((stage) => (
            <KanbanColumn
              key={stage}
              stage={stage}
              items={grouped[stage]}
              onCardClick={handleCardClick}
              onCardDelete={onDelete}
            />
          ))}
        </div>
      )}
      
      {/* Document Viewer Modal */}
      <DocumentViewerModal 
        automation={selectedAutomation} 
        onClose={closeDocumentViewer} 
      />
    </div>
  );
}


