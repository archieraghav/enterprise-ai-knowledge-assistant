import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface DailyQueryCount {
  day: string;
  count: number;
}

export default function AnalyticsChart({ data }: { data: DailyQueryCount[] }) {
  if (data.length === 0) {
    return (
      <div className="h-48 flex items-center justify-center text-sm text-slate-400">
        No query activity in the last 7 days.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="day" tick={{ fontSize: 12, fill: "#64748b" }} />
        <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: "#64748b" }} />
        <Tooltip />
        <Line type="monotone" dataKey="count" stroke="#0f172a" strokeWidth={2} dot={{ r: 3 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}