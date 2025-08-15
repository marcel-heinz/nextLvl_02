"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { PipelineConfig, PipelineConfigCreate, LOBProcessPair, LLMParams } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";

export default function PipelineConfigPage() {
  const [config, setConfig] = useState<PipelineConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Form state
  const [lobPrompt, setLobPrompt] = useState("");
  const [processPrompt, setProcessPrompt] = useState("");
  const [lobProcessPairs, setLobProcessPairs] = useState<LOBProcessPair[]>([{ lob: "", process: "" }]);
  const [llmParams, setLlmParams] = useState<LLMParams>({ temperature: 0.0, max_tokens: 500 });

  const loadConfig = async () => {
    try {
      setLoading(true);
      setError(null);
      const configData = await api.getPipelineConfig();
      
      if (configData) {
        setConfig(configData);
        setLobPrompt(configData.lob_prompt);
        setProcessPrompt(configData.process_prompt);
        setLobProcessPairs(configData.lob_process_pairs);
        setLlmParams(configData.llm_params);
      } else {
        // No config exists, use defaults
        setConfig(null);
        setLobPrompt("Analyze the document and identify the primary line of business based on key terms, company information, and document type.");
        setProcessPrompt("Identify the specific business process represented in this document based on its content, structure, and purpose.");
        setLobProcessPairs([{ lob: "", process: "" }]);
        setLlmParams({ temperature: 0.0, max_tokens: 500 });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load configuration");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConfig();
  }, []);

  const addPair = () => {
    setLobProcessPairs([...lobProcessPairs, { lob: "", process: "" }]);
  };

  const removePair = (index: number) => {
    if (lobProcessPairs.length > 1) {
      setLobProcessPairs(lobProcessPairs.filter((_, i) => i !== index));
    }
  };

  const updatePair = (index: number, field: keyof LOBProcessPair, value: string) => {
    const updated = [...lobProcessPairs];
    updated[index] = { ...updated[index], [field]: value };
    setLobProcessPairs(updated);
  };

  const validateForm = (): string | null => {
    if (!lobPrompt.trim()) return "LOB prompt is required";
    if (!processPrompt.trim()) return "Process prompt is required";
    
    const validPairs = lobProcessPairs.filter(pair => pair.lob.trim() && pair.process.trim());
    if (validPairs.length === 0) return "At least one LOB-Process pair is required";
    
    // Check for duplicates
    const pairStrings = validPairs.map(pair => `${pair.lob.trim()}|${pair.process.trim()}`);
    if (new Set(pairStrings).size !== pairStrings.length) {
      return "Duplicate LOB-Process pairs are not allowed";
    }
    
    if (llmParams.temperature < 0 || llmParams.temperature > 1) {
      return "Temperature must be between 0 and 1";
    }
    
    if (llmParams.max_tokens < 1 || llmParams.max_tokens > 8000) {
      return "Max tokens must be between 1 and 8000";
    }
    
    return null;
  };

  const handleSave = async () => {
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      // Filter out empty pairs
      const validPairs = lobProcessPairs.filter(pair => pair.lob.trim() && pair.process.trim());

      const configData: PipelineConfigCreate = {
        lob_prompt: lobPrompt.trim(),
        process_prompt: processPrompt.trim(),
        lob_process_pairs: validPairs.map(pair => ({
          lob: pair.lob.trim(),
          process: pair.process.trim()
        })),
        llm_params: llmParams
      };

      const savedConfig = await api.createOrUpdatePipelineConfig(configData);
      setConfig(savedConfig);
      setSuccess("Configuration saved successfully!");
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save configuration");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-semibold text-[#008B8B]">Pipeline Configuration</h1>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-[#008B8B]">Pipeline Configuration</h1>
        {config && (
          <Badge variant="outline" className="text-sm">
            Version {config.version}
          </Badge>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
          {success}
        </div>
      )}

      {/* LOB Prompt */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Line of Business (LOB) Prompt</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Instruction for extracting Line of Business
            </label>
            <textarea
              value={lobPrompt}
              onChange={(e) => setLobPrompt(e.target.value)}
              className="w-full h-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#008B8B]"
              placeholder="Enter instructions for how the AI should identify the Line of Business..."
            />
          </div>
        </CardContent>
      </Card>

      {/* Process Prompt */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Business Process Prompt</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Instruction for extracting Business Process
            </label>
            <textarea
              value={processPrompt}
              onChange={(e) => setProcessPrompt(e.target.value)}
              className="w-full h-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#008B8B]"
              placeholder="Enter instructions for how the AI should identify the Business Process..."
            />
          </div>
        </CardContent>
      </Card>

      {/* LOB-Process Pairs */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Available LOB-Process Pairs</CardTitle>
          <p className="text-sm text-gray-600">
            Define the valid combinations of Line of Business and Process that the classifier can select from.
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {lobProcessPairs.map((pair, index) => (
            <div key={index} className="flex gap-4 items-center">
              <div className="flex-1">
                <input
                  type="text"
                  value={pair.lob}
                  onChange={(e) => updatePair(index, "lob", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#008B8B]"
                  placeholder="Line of Business (e.g., Insurance)"
                />
              </div>
              <div className="flex-1">
                <input
                  type="text"
                  value={pair.process}
                  onChange={(e) => updatePair(index, "process", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#008B8B]"
                  placeholder="Business Process (e.g., Claim Processing)"
                />
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => removePair(index)}
                disabled={lobProcessPairs.length === 1}
                className="px-3 py-2 text-red-600 border-red-200 hover:bg-red-50"
              >
                Remove
              </Button>
            </div>
          ))}
          <Button
            variant="outline"
            onClick={addPair}
            className="w-full border-[#008B8B] text-[#008B8B] hover:bg-[#E0F7F7]"
          >
            Add Pair
          </Button>
        </CardContent>
      </Card>

      {/* LLM Parameters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">LLM Parameters</CardTitle>
          <p className="text-sm text-gray-600">
            Configure the behavior of both Mistral (OCR) and GPT-4o (extraction) models.
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Temperature (0-1)
              </label>
              <input
                type="number"
                min="0"
                max="1"
                step="0.1"
                value={llmParams.temperature}
                onChange={(e) => setLlmParams({ ...llmParams, temperature: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#008B8B]"
              />
              <p className="text-xs text-gray-500 mt-1">Lower = more deterministic</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Tokens (1-8000)
              </label>
              <input
                type="number"
                min="1"
                max="8000"
                value={llmParams.max_tokens}
                onChange={(e) => setLlmParams({ ...llmParams, max_tokens: parseInt(e.target.value) || 500 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#008B8B]"
              />
              <p className="text-xs text-gray-500 mt-1">Maximum response length</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button
          onClick={handleSave}
          disabled={saving}
          className="bg-[#008B8B] hover:bg-[#006666] text-white px-6 py-2"
        >
          {saving ? "Saving..." : "Save Configuration"}
        </Button>
      </div>
    </div>
  );
}


