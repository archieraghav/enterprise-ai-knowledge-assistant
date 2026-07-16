import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";

function HomePage() {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-sm border border-slate-200 p-8">
        <h1 className="text-2xl font-semibold text-slate-900 mb-2">
          Enterprise AI Knowledge Assistant
        </h1>
        <p className="text-slate-500 mb-6">
          Ask questions about your company documents, powered by RAG.
        </p>

        {isAuthenticated ? (
          <div className="space-y-3">
            <p className="text-slate-700">
              Signed in as <span className="font-medium">{user?.email}</span>
            </p>
            <button
              onClick={logout}
              className="w-full bg-slate-900 text-white rounded-lg py-2.5 font-medium hover:bg-slate-800 transition"
            >
              Sign out
            </button>
          </div>
        ) : (
          <p className="text-slate-500 text-sm">
            Login and registration pages coming tomorrow (Day 54).
          </p>
        )}
      </div>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;