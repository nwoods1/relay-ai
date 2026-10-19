type QuickActionsProps = {
  disabled: boolean;

  userRole?: string;

  onAction: (
    message: string
  ) => void;
};


export default function QuickActions({
  disabled,
  userRole,
  onAction,
}: QuickActionsProps) {

  const actions = [
    ...(userRole ===
      "manager" ||
    userRole ===
      "admin"
      ? [
          {
            label:
              "Pending approvals",

            prompt:
              "Do I have any pending approvals?",
          },
        ]
      : []),

    {
      label:
        "Check inventory",

      prompt:
        "How many Alpine Shell Jackets are available?",
    },

    {
      label:
        "Create quote",

      prompt:
        "Quote 30 Alpine Shell Jackets for Pacific Mountain Outfitters.",
    },
  ];


  return (
    <div className="flex flex-wrap gap-2">
      {actions.map(
        (action) => (
          <button
            key={
              action.label
            }
            type="button"
            disabled={
              disabled
            }
            onClick={() =>
              onAction(
                action.prompt
              )
            }
            className="rounded-full border border-[#dce3d4] bg-white px-3 py-1.5 text-xs font-medium text-[#42533a] transition hover:border-[#a8bc96] hover:bg-[#f3f7ef] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {action.label}
          </button>
        )
      )}
    </div>
  );
}