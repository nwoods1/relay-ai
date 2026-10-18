interface InventoryStatCardProps {
  title: string;
  value: number;
  description?: string;
}

export default function InventoryStatCard({
  title,
  value,
  description,
}: InventoryStatCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-slate-500">
        {title}
      </p>

      <p className="mt-2 text-3xl font-semibold text-slate-900">
        {value.toLocaleString()}
      </p>

      {description && (
        <p className="mt-2 text-sm text-slate-500">
          {description}
        </p>
      )}
    </div>
  );
}