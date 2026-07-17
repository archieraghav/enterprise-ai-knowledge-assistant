import { Sparkles } from "lucide-react";

export default function Logo({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const dims = { sm: "h-6 w-6", md: "h-8 w-8", lg: "h-10 w-10" }[size];
  const textSize = { sm: "text-sm", md: "text-base", lg: "text-xl" }[size];

  return (
    <div className="flex items-center gap-2">
      <div className={`${dims} rounded-lg bg-brand-600 flex items-center justify-center shrink-0`}>
        <Sparkles className="text-white" size={size === "lg" ? 20 : size === "md" ? 16 : 14} />
      </div>
      <span className={`${textSize} font-semibold text-neutral-900 dark:text-white tracking-tight`}>
                Knowledge Assistant
      </span>
    </div>
  );
}