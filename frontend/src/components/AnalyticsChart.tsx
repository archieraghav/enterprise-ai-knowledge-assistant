import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface DailyQueryCount {
  day: string;
  count: number;
}

export default function AnalyticsChart({ data }: { data: DailyQueryCount[] }) {
  if (data.length === 0) {
    return (
      <div className="h-48 flex items-center justify-center text-sm text-neutral-400 dark:text-neutral-600">
        No query activity in the last 7 days.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="currentColor" className="text-neutral-200 dark:text-neutral-800" />
        <XAxis dataKey="day" tick={{ fontSize: 12, fill: "currentColor" }} className="text-neutral-500 dark:text-neutral-400" />
        <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: "currentColor" }} className="text-neutral-500 dark:text-neutral-400" />
        <Tooltip contentStyle={{ borderRadius: 8, fontSize: 13 }} />
        <Line type="monotone" dataKey="count" stroke="#4f6ce8" strokeWidth={2} dot={{ r: 3 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}