import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  getOrganizationUsers,
  getOrganizationMetrics,
  getAnalytics,
  type AdminUser,
  type OrganizationMetrics,
  type AnalyticsData,
} from "../lib/api";
import AnalyticsChart from "../components/AnalyticsChart";

function MetricCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl px-5 py-4">
      <p className="text-xs text-slate-400 mb-1">{label}</p>
      <p className="text-2xl font-semibold text-slate-900">{value}</p>
    </div>
  );
}

export default function AdminPage() {
  const [metrics, setMetrics] = useState<OrganizationMetrics | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [metricsData, analyticsData, usersData] = await Promise.all([
          getOrganizationMetrics(),
          getAnalytics(),
          getOrganizationUsers(),
        ]);
        setMetrics(metricsData);
        setAnalytics(analyticsData);
        setUsers(usersData.items);
      } catch {
        setError("Failed to load admin data. You may not have admin permissions.");
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center text-slate-400">Loading...</div>;
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-3">
        <p className="text-red-600 text-sm">{error}</p>
        <Link to="/" className="text-slate-500 text-sm hover:underline">
          ← Back home
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-10">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-semibold text-slate-900">Admin Dashboard</h1>
          <Link to="/" className="text-sm text-slate-500 hover:underline">
            ← Back home
          </Link>
        </div>

        {metrics && (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-8">
            <MetricCard label="Total Users" value={metrics.total_users} />
            <MetricCard label="Active Users" value={metrics.active_users} />
            <MetricCard label="Total Documents" value={metrics.total_documents} />
            <MetricCard label="Indexed Documents" value={metrics.indexed_documents} />
            <MetricCard label="Failed Documents" value={metrics.failed_documents} />
            <MetricCard label="Conversations" value={metrics.total_conversations} />
          </div>
        )}

        {analytics && (
          <div className="bg-white border border-slate-200 rounded-xl p-5 mb-8">
            <h2 className="text-sm font-medium text-slate-700 mb-4">
              Queries — Last 7 Days ({analytics.total_queries} total)
            </h2>
            <AnalyticsChart data={analytics.queries_last_7_days} />

            <div className="flex gap-6 mt-4 pt-4 border-t border-slate-100 text-sm">
              <span className="text-slate-500">
                Feedback: <span className="font-medium text-slate-900">{analytics.feedback_summary.total_feedback}</span>
              </span>
              <span className="text-green-600">👍 {analytics.feedback_summary.positive_count}</span>
              <span className="text-red-600">👎 {analytics.feedback_summary.negative_count}</span>
              <span className="text-slate-500">
                {Math.round(analytics.feedback_summary.positive_rate * 100)}% positive
              </span>
            </div>
          </div>
        )}

        <div className="bg-white border border-slate-200 rounded-xl divide-y divide-slate-100">
          <div className="px-5 py-3">
            <h2 className="text-sm font-medium text-slate-700">Organization Users</h2>
          </div>
          {users.map((u) => (
            <div key={u.id} className="flex items-center justify-between px-5 py-3">
              <div>
                <p className="text-sm text-slate-900">{u.full_name}</p>
                <p className="text-xs text-slate-400">{u.email}</p>
              </div>
              <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-slate-100 text-slate-700">
                {u.is_superuser ? "superuser" : u.role}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}