"use client";

import { WorkflowStages, WorkflowMetrics } from "@/lib/types";

interface WorkflowVisualizationProps {
  stages: WorkflowStages;
  metrics: WorkflowMetrics;
}

export function WorkflowVisualization({ stages, metrics }: WorkflowVisualizationProps) {
  return (
    <div className="bg-gray-50 rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4 text-center">Pipeline Flow</h3>
      
      {/* Desktop View */}
      <div className="hidden md:flex items-center justify-center space-x-4">
        {stages.stages.map((stage, index) => {
          const isLast = index === stages.stages.length - 1;
          const queueCount = metrics.queue_lengths[stage] || 0;
          const isActive = queueCount > 0;
          
          return (
            <div key={stage} className="flex items-center">
              {/* Stage Box */}
              <div className={`
                relative px-4 py-3 rounded-lg border-2 min-w-[120px] text-center transition-all
                ${isActive 
                  ? 'border-[#008B8B] bg-[#E0F7F7] text-[#008B8B] scale-105' 
                  : 'border-gray-300 bg-white text-gray-600'
                }
              `}>
                <div className="font-medium text-sm">{stage}</div>
                <div className={`text-lg font-bold mt-1 ${isActive ? 'text-[#008B8B]' : 'text-gray-400'}`}>
                  {queueCount}
                </div>
                
                {/* Activity Indicator */}
                {isActive && (
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                )}
              </div>
              
              {/* Arrow */}
              {!isLast && (
                <div className="mx-2 text-gray-400">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
                  </svg>
                </div>
              )}
            </div>
          );
        })}
      </div>
      
      {/* Mobile View */}
      <div className="md:hidden space-y-3">
        {stages.stages.map((stage, index) => {
          const isLast = index === stages.stages.length - 1;
          const queueCount = metrics.queue_lengths[stage] || 0;
          const isActive = queueCount > 0;
          
          return (
            <div key={stage} className="flex flex-col items-center">
              {/* Stage Box */}
              <div className={`
                relative px-4 py-3 rounded-lg border-2 w-full text-center transition-all
                ${isActive 
                  ? 'border-[#008B8B] bg-[#E0F7F7] text-[#008B8B]' 
                  : 'border-gray-300 bg-white text-gray-600'
                }
              `}>
                <div className="font-medium">{stage}</div>
                <div className={`text-xl font-bold mt-1 ${isActive ? 'text-[#008B8B]' : 'text-gray-400'}`}>
                  {queueCount} items
                </div>
                
                {/* Activity Indicator */}
                {isActive && (
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                )}
              </div>
              
              {/* Arrow */}
              {!isLast && (
                <div className="my-2 text-gray-400">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6-1.41-1.41z"/>
                  </svg>
                </div>
              )}
            </div>
          );
        })}
      </div>
      
      {/* Legend */}
      <div className="mt-6 text-center">
        <div className="inline-flex items-center gap-4 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <span>Active (has items)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
            <span>Idle (empty)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
