"use client";

import { Automation } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";

type Props = {
  item: Automation;
  onClick?: (automation: Automation) => void;
  onDelete?: (id: string) => void;
};

export function AutomationCard({ item, onClick, onDelete }: Props) {
  const [uploadDate, setUploadDate] = useState<string>("");
  const [mounted, setMounted] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Extract first 8 characters of ID for display
  const shortId = item.id.slice(0, 8);

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click event
    
    // Show confirmation dialog
    const confirmed = window.confirm(
      `Are you sure you want to delete automation ${shortId}?\n\nThis will permanently delete:\n- The automation record\n- The uploaded file from storage\n\nThis action cannot be undone.`
    );
    
    if (!confirmed) return;
    
    setIsDeleting(true);
    try {
      await api.deleteAutomation(item.id);
      onDelete?.(item.id);
    } catch (error) {
      console.error("Failed to delete automation:", error);
      alert("Failed to delete automation. Please try again.");
    } finally {
      setIsDeleting(false);
    }
  };
  
  useEffect(() => {
    setMounted(true);
    // Format upload date with seconds for LIFO ordering - only on client
    const formattedDate = new Date(item.created_at).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
    setUploadDate(formattedDate);
  }, [item.created_at]);
  
  return (
    <Card 
      className="bg-white hover:shadow-md transition-shadow cursor-pointer relative"
      onClick={() => onClick?.(item)}
    >
      <CardContent className="p-3 text-center space-y-2">
        <div className="text-lg font-mono font-semibold text-[#008B8B]">
          ID: {shortId}
        </div>
        <div className="text-sm text-gray-600">
          {mounted ? uploadDate : "Loading..."}
        </div>
        {item.file_name && (
          <div className="text-xs text-gray-500 truncate">
            {item.file_name}
          </div>
        )}
        
        {/* Delete button */}
        <Button
          variant="secondary"
          onClick={handleDelete}
          disabled={isDeleting}
          className="mt-2 w-full bg-red-50 hover:bg-red-100 text-red-600 border-red-200"
        >
          {isDeleting ? "Deleting..." : "Delete"}
        </Button>
      </CardContent>
    </Card>
  );
}


