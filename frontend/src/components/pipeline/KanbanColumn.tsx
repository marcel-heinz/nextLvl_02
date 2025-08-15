import { Automation, Stage } from "@/lib/types";
import { AutomationCard } from "@/components/pipeline/AutomationCard";

type Props = {
  stage: Stage;
  items: Automation[];
  onCardClick?: (automation: Automation) => void;
  onCardDelete?: (id: string) => void;
};

export function KanbanColumn({ stage, items, onCardClick, onCardDelete }: Props) {
  return (
    <div className="flex flex-col bg-[#F8FFFF] rounded-lg border border-[#E0F7F7] flex-1">
      <div className="px-4 py-3 border-b border-[#E0F7F7]">
        <div className="text-sm font-semibold text-[#008B8B]">{stage}</div>
        <div className="text-xs text-gray-500 mt-1">{items.length} case{items.length !== 1 ? 's' : ''}</div>
      </div>
      <div className="p-3 space-y-3 min-h-[300px]">
        {items.length === 0 ? (
          <div className="text-center text-gray-400 text-xs py-8">
            No cases in this stage
          </div>
        ) : (
          items.map((item) => (
            <AutomationCard
              key={item.id}
              item={item}
              onClick={stage === "New" ? onCardClick : undefined}
              onDelete={onCardDelete}
            />
          ))
        )}
      </div>
    </div>
  );
}


