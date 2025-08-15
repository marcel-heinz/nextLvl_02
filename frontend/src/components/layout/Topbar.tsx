import React from "react";

type Props = {
  onMobileMenuToggle?: () => void;
};

export function Topbar({ onMobileMenuToggle }: Props) {
  return (
    <header className="h-14 border-b border-[#E0F7F7] bg-white flex items-center justify-between px-4">
      <div className="flex items-center gap-3">
        {onMobileMenuToggle && (
          <button
            onClick={onMobileMenuToggle}
            className="md:hidden p-2 rounded-md hover:bg-[#F0FFFF] text-[#008B8B]"
            title="Toggle menu"
          >
            ☰
          </button>
        )}
        <div className="md:hidden text-[#008B8B] font-bold">nxtLvl</div>
      </div>
      <div className="flex items-center gap-3">
        <input
          placeholder="Search..."
          className="h-9 w-56 rounded-md border border-[#E0F7F7] px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#20B2AA]"
        />
      </div>
    </header>
  );
}


