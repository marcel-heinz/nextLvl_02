export default function SettingsPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold text-[#008B8B]">Settings</h1>
      <p className="text-gray-600">General application settings (placeholder).</p>
      <div className="rounded-lg border border-[#E0F7F7] bg-white p-4 space-y-3 text-sm">
        <div className="flex items-center justify-between">
          <span>Dark mode</span>
          <input type="checkbox" disabled />
        </div>
        <div className="flex items-center justify-between">
          <span>Notifications</span>
          <input type="checkbox" disabled />
        </div>
      </div>
    </div>
  );
}


