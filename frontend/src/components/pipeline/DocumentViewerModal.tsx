"use client";

import React, { useState, useEffect } from "react";
import { Automation } from "@/lib/types";
import { Button } from "@/components/ui/Button";

type Props = {
  automation: Automation | null;
  onClose: () => void;
};

export function DocumentViewerModal({ automation, onClose }: Props) {
  const [uploadDateString, setUploadDateString] = useState<string>("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (automation) {
      const dateString = new Date(automation.created_at).toLocaleString();
      setUploadDateString(dateString);
    }
  }, [automation]);
  if (!automation) return null;

  const isImage = automation.file_name?.match(/\.(jpg|jpeg|png|gif|webp)$/i);
  const isPDF = automation.file_name?.match(/\.pdf$/i);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-4xl h-[90vh] bg-white rounded-lg shadow-xl flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div>
            <h2 className="text-lg font-semibold text-[#008B8B]">
              ID: {automation.id.slice(0, 8)}
            </h2>
            <p className="text-sm text-gray-600">{automation.file_name}</p>
          </div>
          <Button variant="ghost" onClick={onClose}>
            ✕ Close
          </Button>
        </div>

        {/* Document Viewer */}
        <div className="flex-1 p-4 overflow-hidden">
          {automation.file_url ? (
            <>
              {isPDF && (
                <iframe
                  src={automation.file_url}
                  className="w-full h-full border border-gray-300 rounded"
                  title={`PDF Viewer - ${automation.file_name}`}
                />
              )}
              
              {isImage && (
                <div className="w-full h-full flex items-center justify-center bg-gray-50">
                  <img
                    src={automation.file_url}
                    alt={automation.file_name || 'Uploaded image'}
                    className="max-w-full max-h-full object-contain rounded shadow-lg"
                    onError={(e) => {
                      console.error('Image failed to load:', automation.file_url);
                      e.currentTarget.style.display = 'none';
                      e.currentTarget.nextElementSibling?.setAttribute('style', 'display: block');
                    }}
                    onLoad={() => {
                      console.log('Image loaded successfully:', automation.file_url);
                    }}
                  />
                  <div className="text-center text-gray-500" style={{ display: 'none' }}>
                    <div className="text-6xl mb-4">🖼️</div>
                    <p className="text-lg font-medium">Image failed to load</p>
                    <p className="text-sm">The image file might not be accessible</p>
                    <div className="mt-2 text-xs text-gray-400 break-all">
                      {automation.file_url}
                    </div>
                  </div>
                </div>
              )}
              
              {!isPDF && !isImage && (
                <div className="w-full h-full flex items-center justify-center text-center">
                  <div className="space-y-4">
                    <div className="text-6xl">📄</div>
                    <div className="text-gray-600">
                      <p className="text-lg font-medium">{automation.file_name}</p>
                      <p className="text-sm">Preview not available for this file type</p>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-500">
              <div className="text-center">
                <div className="text-6xl mb-4">❌</div>
                <p>File not available</p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex justify-between items-center text-sm text-gray-600">
            <div>
              <span className="font-medium">Upload Date:</span>{" "}
              {mounted ? uploadDateString : "Loading..."}
            </div>
            <div>
              <span className="font-medium">Stage:</span> {automation.stage}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
