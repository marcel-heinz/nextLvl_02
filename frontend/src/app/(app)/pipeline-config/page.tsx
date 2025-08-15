export default function PipelineConfigPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold text-[#008B8B]">Pipeline Config</h1>
      <p className="text-gray-600">Configure stages and defaults (placeholder).</p>
      <div className="rounded-lg border border-[#E0F7F7] bg-white p-4">
        <ul className="list-disc pl-5 text-sm text-gray-700">
          <li>Define stages order and labels.</li>
          <li>Set default priorities and SLA thresholds.</li>
          <li>Toggle WIP limits per stage.</li>
        </ul>
      </div>
    </div>
  );
}


