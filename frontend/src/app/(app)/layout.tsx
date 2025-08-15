"use client";
import { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <div className="min-h-screen bg-[#FAFEFE] text-gray-900">
      <div className="flex">
        <Sidebar isCollapsed={isSidebarCollapsed} onToggle={toggleSidebar} />
        <div className="flex-1 flex flex-col">
          <Topbar onMobileMenuToggle={toggleMobileMenu} />
          <main className="p-4">{children}</main>
        </div>
      </div>
      
      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-50">
          <div className="fixed inset-0 bg-black/50" onClick={toggleMobileMenu} />
          <div className="fixed left-0 top-0 h-full w-64 bg-white border-r border-[#E0F7F7] shadow-lg">
            <div className="h-14 flex items-center justify-between px-4 border-b border-[#E0F7F7]">
              <div className="text-[#008B8B] font-bold">nxtLvl</div>
              <button
                onClick={toggleMobileMenu}
                className="p-1 rounded-md hover:bg-[#F0FFFF] text-[#008B8B] transition-colors"
              >
                ✕
              </button>
            </div>
            <nav className="px-2 py-2 space-y-1">
              {[
                { href: "/", label: "Dashboard", icon: "🏠" },
                { href: "/pipeline", label: "Automation Pipeline", icon: "🔄" },
                { href: "/workflow-monitor", label: "Workflow Monitor", icon: "📊" },
                { href: "/pipeline-config", label: "Pipeline Config", icon: "🔧" },
                { href: "/agentic-rules", label: "Agentic Rules", icon: "🤖" },
                { href: "/integration", label: "Integration", icon: "🔗" },
                { href: "/settings", label: "Settings", icon: "⚙️" },
              ].map((item) => (
                <a
                  key={item.href}
                  href={item.href}
                  onClick={toggleMobileMenu}
                  className="flex items-center rounded-md px-3 py-2 text-sm font-medium text-gray-700 hover:bg-[#F0FFFF] hover:text-[#008B8B] transition-colors"
                >
                  <span className="text-base mr-3">{item.icon}</span>
                  <span>{item.label}</span>
                </a>
              ))}
            </nav>
          </div>
        </div>
      )}
    </div>
  );
}


