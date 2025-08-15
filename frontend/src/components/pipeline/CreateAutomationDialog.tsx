"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/Button";
import { STAGES, AutomationCreate, Stage } from "@/lib/types";
import { api } from "@/lib/api";

type Props = {
  onCreate: (payload: AutomationCreate) => Promise<void> | void;
  onFileUpload?: (automation: any) => Promise<void> | void;
};

export function CreateAutomationDialog({ onCreate, onFileUpload }: Props) {
  const [open, setOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const reset = () => {
    setFile(null);
  };

  async function submit() {
    if (!file) return;
    setSubmitting(true);
    try {
      // Use filename as title, removing extension
      const finalTitle = file.name.replace(/\.[^/.]+$/, "");
      
      // Upload file and create automation via API
      const automation = await api.createAutomationWithFile(
        file,
        finalTitle
      );

      // Call the callback if provided
      if (onFileUpload) {
        await onFileUpload(automation);
      } else {
        // Fallback to the original onCreate method
        await onCreate({
          title: finalTitle,
          stage: "New",
        });
      }
      
      setOpen(false);
      reset();
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Upload failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      // Only allow PDF and image files
      const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/gif', 'image/webp'];
      if (allowedTypes.includes(selectedFile.type)) {
        setFile(selectedFile);
      } else {
        alert('Please select a PDF or image file (JPG, PNG, GIF, WebP)');
        e.target.value = '';
      }
    }
  };

  return (
    <div>
      <Button onClick={() => setOpen(true)}>Upload New Case</Button>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
          <div className="w-full max-w-lg rounded-lg bg-white shadow-lg border border-[#E0F7F7]">
            <div className="px-4 py-3 border-b border-[#E0F7F7] text-[#008B8B] font-semibold">Upload Case Document</div>
            <div className="p-6">
              <div className="border-2 border-dashed border-[#E0F7F7] rounded-lg p-8 text-center">
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png,.gif,.webp"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <div className="text-gray-500">
                    {file ? (
                      <div className="text-[#008B8B]">
                        <div className="text-lg mb-1">✅</div>
                        <div className="text-base font-medium">{file.name}</div>
                        <div className="text-sm">{(file.size / 1024 / 1024).toFixed(2)} MB</div>
                      </div>
                    ) : (
                      <>
                        <div className="text-3xl mb-2">📄</div>
                        <div className="text-base mb-1">Click to upload PDF or image</div>
                        <div className="text-sm text-gray-400">Supports: PDF, JPG, PNG, GIF, WebP</div>
                      </>
                    )}
                  </div>
                </label>
                {file && (
                  <button
                    type="button"
                    onClick={() => setFile(null)}
                    className="mt-3 text-sm text-red-600 hover:underline"
                  >
                    Remove file
                  </button>
                )}
              </div>
            </div>
            <div className="px-4 py-3 border-t border-[#E0F7F7] flex justify-end gap-2">
              <Button variant="ghost" onClick={() => setOpen(false)}>
                Cancel
              </Button>
              <Button onClick={submit} disabled={submitting || !file}>
                {submitting ? "Uploading..." : "Upload Case"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


