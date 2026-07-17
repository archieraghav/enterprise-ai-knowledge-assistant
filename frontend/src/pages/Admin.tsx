import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Header from "../components/Header";
import Footer from "../components/Footer";
import BackgroundGlow from "../components/BackgroundGlow";
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
    <div className="card px-4 sm:px-5 py-4">
      <p className="text-xs text-neutral-400 dark:text-neutral-500 mb-1">{label}</p>
      <p className="text-xl sm:text-2xl font-semibold text-neutral-900 dark:text-white">{value}</p>
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
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50 dark:bg-neutral-950 text-neutral-400 dark:text-neutral-500">
        Loading...
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col bg-neutral-50 dark:bg-neutral-950">
        <Header />
        <div className="flex-1 flex flex-col items-center justify-center gap-3">
          <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col relative">
      <BackgroundGlow />
      <Header />

      <main className="flex-1 px-4 sm:px-6 py-8 sm:py-10">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="max-w-3xl mx-auto"
        >
          <h1 className="text-xl sm:text-2xl font-semibold text-neutral-900 dark:text-white mb-6 sm:mb-8">
            Admin Dashboard
          </h1>

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
            <div className="card p-4 sm:p-5 mb-8">
              <h2 className="text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-4">
                Queries — Last 7 Days ({analytics.total_queries} total)
              </h2>
              <AnalyticsChart data={analytics.queries_last_7_days} />

              <div className="flex flex-wrap gap-4 sm:gap-6 mt-4 pt-4 border-t border-neutral-100 dark:border-neutral-800 text-sm">
                <span className="text-neutral-500 dark:text-neutral-400">
                  Feedback: <span className="font-medium text-neutral-900 dark:text-white">{analytics.feedback_summary.total_feedback}</span>
                </span>
                <span className="text-emerald-600 dark:text-emerald-400">👍 {analytics.feedback_summary.positive_count}</span>
                <span className="text-red-600 dark:text-red-400">👎 {analytics.feedback_summary.negative_count}</span>
                <span className="text-neutral-500 dark:text-neutral-400">
                  {Math.round(analytics.feedback_summary.positive_rate * 100)}% positive
                </span>
              </div>
            </div>
          )}

          <div className="card divide-y divide-neutral-100 dark:divide-neutral-800">
            <div className="px-4 sm:px-5 py-3">
              <h2 className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Organization Users</h2>
            </div>
            {users.map((u) => (
              <div key={u.id} className="flex items-center justify-between gap-3 px-4 sm:px-5 py-3">
                <div className="min-w-0">
                  <p className="text-sm text-neutral-900 dark:text-white truncate">{u.full_name}</p>
                  <p className="text-xs text-neutral-400 dark:text-neutral-500 truncate">{u.email}</p>
                </div>
                <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 shrink-0">
                  {u.is_superuser ? "superuser" : u.role}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      </main>

      <Footer />
    </div>
  );
}