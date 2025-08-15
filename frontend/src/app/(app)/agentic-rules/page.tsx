export default function AgenticRulesPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold text-[#008B8B]">Agentic Rules</h1>
      <p className="text-gray-600">Define rules for automated decisions (placeholder).</p>
      <div className="rounded-lg border border-[#E0F7F7] bg-white p-4">
        <pre className="text-sm text-gray-700">Example:
when document.type == &quot;claim&quot; and amount &lt; 1000 then auto_approve()</pre>
      </div>
    </div>
  );
}


