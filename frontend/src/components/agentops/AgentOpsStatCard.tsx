type AgentOpsStatCardProps = {
  title: string;

  value:
    | string
    | number;

  description: string;

  tone?:
    | "default"
    | "success"
    | "warning"
    | "danger";
};


export default function AgentOpsStatCard({
  title,
  value,
  description,
  tone = "default",
}: AgentOpsStatCardProps) {
  const toneStyles = {
    default: {
      icon:
        "bg-[#e4ecd9] text-[#58763d]",
      value:
        "text-[#1d2919]",
    },

    success: {
      icon:
        "bg-[#e5efe0] text-[#54733e]",
      value:
        "text-[#36552b]",
    },

    warning: {
      icon:
        "bg-[#f4eddc] text-[#8a6b32]",
      value:
        "text-[#665025]",
    },

    danger: {
      icon:
        "bg-[#f4e3df] text-[#a45b50]",
      value:
        "text-[#7a3e36]",
    },
  };

  const styles =
    toneStyles[tone];


  return (
    <div className="rounded-[22px] border border-[#dce2d6] bg-white p-5 shadow-[0_10px_28px_rgba(37,53,31,0.05)]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.12em] text-[#8a9285]">
            {title}
          </p>

          <p
            className={`mt-3 text-3xl font-semibold tracking-[-0.04em] ${styles.value}`}
          >
            {value}
          </p>
        </div>

        <div
          className={`flex h-10 w-10 items-center justify-center rounded-xl ${styles.icon}`}
        >
          <span className="h-2.5 w-2.5 rounded-full bg-current" />
        </div>
      </div>

      <p className="mt-3 text-xs leading-5 text-[#7b8476]">
        {description}
      </p>
    </div>
  );
}