import Link from "next/link";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-[#008B8B]">Dashboard</h1>
        <p className="text-gray-600">Welcome. Start by exploring the automation pipeline.</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Link
          href="/pipeline"
          className="rounded-lg border border-[#E0F7F7] bg-white p-6 hover:shadow-md transition-shadow"
        >
          <div className="text-lg font-medium text-[#008B8B]">Automation Pipeline</div>
          <p className="text-sm text-gray-600 mt-2">Track items across stages with progress.</p>
        </Link>
        <Link
          href="/pipeline-config"
          className="rounded-lg border border-[#E0F7F7] bg-white p-6 hover:shadow-md transition-shadow"
        >
          <div className="text-lg font-medium text-[#008B8B]">Pipeline Config</div>
          <p className="text-sm text-gray-600 mt-2">Manage stages and settings.</p>
        </Link>
        <Link
          href="/agentic-rules"
          className="rounded-lg border border-[#E0F7F7] bg-white p-6 hover:shadow-md transition-shadow"
        >
          <div className="text-lg font-medium text-[#008B8B]">Agentic Rules</div>
          <p className="text-sm text-gray-600 mt-2">Define rules for automated decisions.</p>
        </Link>
        <Link
          href="/integration"
          className="rounded-lg border border-[#E0F7F7] bg-white p-6 hover:shadow-md transition-shadow"
        >
          <div className="text-lg font-medium text-[#008B8B]">Integration</div>
          <p className="text-sm text-gray-600 mt-2">Connect with core systems.</p>
        </Link>
        <Link
          href="/settings"
          className="rounded-lg border border-[#E0F7F7] bg-white p-6 hover:shadow-md transition-shadow"
        >
          <div className="text-lg font-medium text-[#008B8B]">Settings</div>
          <p className="text-sm text-gray-600 mt-2">General application settings.</p>
        </Link>
      </div>
    </div>
  );
}


