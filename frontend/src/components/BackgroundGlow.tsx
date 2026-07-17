export default function BackgroundGlow() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
      <div className="absolute -top-40 -left-40 h-[28rem] w-[28rem] rounded-full bg-brand-300/30 dark:bg-brand-500/10 blur-[100px]" />
      <div className="absolute top-1/3 -right-40 h-[26rem] w-[26rem] rounded-full bg-violet-300/25 dark:bg-violet-500/10 blur-[100px]" />
      <div className="absolute bottom-0 left-1/4 h-[24rem] w-[24rem] rounded-full bg-emerald-200/20 dark:bg-emerald-500/10 blur-[100px]" />
      <div
        className="absolute inset-0 opacity-[0.4] dark:opacity-[0.15]"
        style={{
          backgroundImage: "radial-gradient(circle, rgba(0,0,0,0.06) 1px, transparent 1px)",
          backgroundSize: "24px 24px",
        }}
      />
    </div>
  );
}