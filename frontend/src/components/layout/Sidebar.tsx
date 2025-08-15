"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

type NavItem = { href: string; label: string; icon: string };

const nav: NavItem[] = [
  { href: "/", label: "Dashboard", icon: "🏠" },
  { href: "/pipeline", label: "Automation Pipeline", icon: "🔄" },
  { href: "/workflow-monitor", label: "Workflow Monitor", icon: "📊" },
  { href: "/pipeline-config", label: "Pipeline Config", icon: "🔧" },
  { href: "/agentic-rules", label: "Agentic Rules", icon: "🤖" },
  { href: "/integration", label: "Integration", icon: "🔗" },
  { href: "/settings", label: "Settings", icon: "⚙️" },
];

type Props = {
  isCollapsed: boolean;
  onToggle: () => void;
};

export function Sidebar({ isCollapsed, onToggle }: Props) {
  const pathname = usePathname();
  
  return (
    <aside className={`hidden md:flex md:flex-col border-r border-[#E0F7F7] bg-white transition-all duration-300 ${isCollapsed ? 'md:w-16' : 'md:w-64'}`}>
      <div className="h-14 flex items-center justify-between px-4 border-b border-[#E0F7F7]">
        {!isCollapsed && <div className="text-[#008B8B] font-bold">nxtLvl</div>}
        <button
          onClick={onToggle}
          className="p-1 rounded-md hover:bg-[#F0FFFF] text-[#008B8B] transition-colors"
          title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {isCollapsed ? "▶️" : "◀️"}
        </button>
      </div>
      <nav className="flex-1 px-2 py-2 space-y-1">
        {nav.map((item) => {
          const active = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={[
                "flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors",
                active ? "bg-[#E0F7F7] text-[#008B8B]" : "text-gray-700 hover:bg-[#F0FFFF] hover:text-[#008B8B]",
              ].join(" ")}
              title={isCollapsed ? item.label : undefined}
            >
              <span className="text-base mr-3">{item.icon}</span>
              {!isCollapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}


